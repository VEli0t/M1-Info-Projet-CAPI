import pytest
from flask import url_for
from app import app
import os
import json

@pytest.fixture
def client():
    """
    Fixture pour configurer un client de test Flask.
    """
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Désactive CSRF pour les tests
    with app.test_client() as client:
        with client.session_transaction() as session:
            # Initialisation des données de session
            session['players'] = ["Alice", "Bob", "Charlie"]
            session['features'] = ["Feature A", "Feature B"]
            session['current_feature_index'] = 0
            session['index_player'] = 0
            session['rules'] = "majorite"
            session['time_limit'] = 30
            session['results'] = {}
            session['liste_vote'] = []
            session['revote'] = False
        yield client


def test_home(client):
    """
    Test de la route d'accueil.
    Vérifie que la page se charge correctement et contient le texte attendu.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"Commencer une partie" in response.data


def test_settings_get(client):
    """
    Test de la route settings en méthode GET.
    Vérifie que la page se charge correctement et affiche les champs de formulaire attendus.
    """
    response = client.get('/settings')
    assert response.status_code == 200
    assert b"Nombre de joueurs" in response.data
    assert "règles".encode('utf-8') in response.data


def test_settings_post(client):
    """
    Test de la route settings en méthode POST.
    Vérifie que les données sont enregistrées dans la session et qu'il y a une redirection.
    """
    data = {
        'num_players': '3',
        'player_1': 'Alice',
        'player_2': 'Bob',
        'player_3': 'Charlie',
        'rules': '2'
    }
    response = client.post('/settings', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert "Proposer des fonctionnalités".encode('utf-8') in response.data


def test_propose_features_post(client):
    """
    Test de la route propose_features en méthode POST.
    Vérifie que l'utilisateur peut proposer une fonctionnalité et que celle-ci est enregistrée.
    """
    with client.session_transaction() as session:
        session['features'] = []

    response = client.post('/propose_features', data={'feature': 'Nouvelle fonctionnalité'}, follow_redirects=True)
    assert response.status_code == 200
    assert "Nouvelle fonctionnalité".encode('utf-8') in response.data


def test_delete_feature(client):
    """
    Test de la route delete_feature en méthode POST.
    Vérifie que la suppression d'une fonctionnalité fonctionne.
    """
    with client.session_transaction() as session:
        session['features'] = ['Fonctionnalité 1', 'Fonctionnalité 2']

    response = client.post('/delete_feature', json={'feature': 'Fonctionnalité 1'})
    assert response.status_code == 200
    assert b'"success":true' in response.data

    with client.session_transaction() as session:
        assert 'Fonctionnalité 1' not in session['features']  # Doit être supprimé
        assert 'Fonctionnalité 2' in session['features']      # Doit rester


def test_game_get(client):
    """
    Test de la route game en méthode GET.
    Vérifie que la page affiche les informations du joueur actuel et de la fonctionnalité.
    """
    with client.session_transaction() as session:
        session['players'] = ['Alice', 'Bob']
        session['features'] = ['Fonctionnalité A']
        session['index_player'] = 0
        session['current_feature_index'] = 0

    response = client.get('/game')
    assert response.status_code == 200
    assert b"Alice" in response.data  # Vérifie que le joueur actuel est affiché
    assert "Fonctionnalité A".encode('utf-8') in response.data


def test_game_post(client):
    """
    Test de la route game en méthode POST.
    Vérifie qu'un vote est enregistré et que le joueur suivant est bien pris en compte.
    """
    with client.session_transaction() as session:
        session['players'] = ['Alice', 'Bob']
        session['features'] = ['Fonctionnalité A']
        session['index_player'] = 0
        session['current_feature_index'] = 0
        session['liste_vote'] = []

    response = client.post('/game', data={'valeur_choisi': '3'}, follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert session['liste_vote'] == [3]
        assert session['index_player'] == 1


def test_results(client):
    """
    Test de la route results.
    Vérifie que les résultats finaux sont affichés correctement.
    """
    with client.session_transaction() as session:
        session['results'] = {'Fonctionnalité A': 4.5}

    response = client.get('/results')
    assert response.status_code == 200
    assert "Fonctionnalité A".encode('utf-8') in response.data
    assert b"4.5" in response.data

def test_load_game_page_get(client):
    """
    Test de la route /load_game en méthode GET.
    Vérifie que la page se charge correctement.
    """
    response = client.get('/load_game')
    assert response.status_code == 200
    assert b"Charger une partie" in response.data

def test_load_game_page_post(client, tmp_path):
    """
    Test de la route /load_game en méthode POST.
    Vérifie que le jeu charge correctement une sauvegarde valide.
    """
    # Créer un fichier de sauvegarde temporaire
    save_data = {
        "players": ["Alice", "Bob", "Charlie"],
        "features": ["Feature A", "Feature B"],
        "current_feature_index": 1,
        "index_player": 2,
        "rules": "unanime",
        "results": {"Feature A": "1"},
        "liste_vote": ["1", "2", "3"],
        "time_limit": 60
    }
    save_file = tmp_path / "sauvegarde.json"
    with open(save_file, 'w') as f:
        json.dump(save_data, f)
    
    # Charger la sauvegarde via la route
    with open(save_file, 'rb') as f:
        response = client.post('/load_game', data={'savefile': f}, follow_redirects=False)
    assert response.status_code == 302  # Redirection attendue après chargement
    assert response.location == url_for('game', _external=True)
    
    # Vérifie que la session a été mise à jour
    with client.session_transaction() as session:
        assert session['players'] == save_data['players']
        assert session['features'] == save_data['features']
        assert session['current_feature_index'] == save_data['current_feature_index']
        assert session['index_player'] == save_data['index_player']
        assert session['rules'] == save_data['rules']
        assert session['results'] == save_data['results']
        assert session['liste_vote'] == save_data['liste_vote']
        assert session['time_limit'] == save_data['time_limit']

def test_interro_redirection(client):
    """
    Test de la redirection vers /interro lorsque tous les joueurs votent 'interro'.
    """
    # Simuler que tous les joueurs ont voté 'interro'
    with client.session_transaction() as session:
        session['liste_vote'] = ["interro", "interro", "interro"]

    response = client.post('/game', data={}, follow_redirects=False)
    assert response.status_code == 302 # Redirection

def test_interro_page_get(client):
    """
    Test de la route /interro en méthode GET.
    Vérifie que la page se charge correctement.
    """
    # Simuler un retour depuis interro en réinitialisant index_player et revote
    with client.session_transaction() as session:
        session['index_player'] = 0
        session['revote'] = True
        session['features'] = ["Feature A"]
    
    response = client.get('/interro')
    assert response.status_code == 200
    assert b"Phase de discussion" in response.data

def test_load_game_page_post(client, tmp_path):
    """
    Test de la route /load_game en méthode POST.
    Vérifie que le jeu charge correctement une sauvegarde valide.
    """
    # Créer un fichier de sauvegarde temporaire
    save_data = {
        "players": ["Alice", "Bob", "Charlie"],
        "features": ["Feature A", "Feature B"],
        "current_feature_index": 1,
        "index_player": 2,
        "rules": "unanime",
        "results": {"Feature A": "1"},
        "liste_vote": ["1", "2", "3"],
        "time_limit": 60
    }
    save_file = tmp_path / "sauvegarde.json"
    with open(save_file, 'w') as f:
        json.dump(save_data, f)
    
    # Charger la sauvegarde via la route
    with open(save_file, 'rb') as f:
        response = client.post('/load_game', data={'savefile': f}, follow_redirects=False)
    assert response.headers['Location'].endswith('/game')
    
    # Vérifie que la session a été mise à jour
    with client.session_transaction() as session:
        assert session['players'] == save_data['players']
        assert session['features'] == save_data['features']
        assert session['current_feature_index'] == save_data['current_feature_index']
        assert session['index_player'] == save_data['index_player']
        assert session['rules'] == save_data['rules']
        assert session['results'] == save_data['results']
        assert session['liste_vote'] == save_data['liste_vote']
        assert session['time_limit'] == save_data['time_limit']

def test_valider_vote_unanime():
    """
    Test de la fonction valider_vote pour le type 'unanime'.
    """
    from models.game import valider_vote
    # Tous les votes sont identiques
    assert valider_vote(['1', '1', '1'], 'unanime') == (True, '1')
    # Les votes sont différents
    assert valider_vote(['1', '2', '1'], 'unanime') == (False, False)
    # Liste vide
    assert valider_vote([], 'unanime') == (False, False)

def test_valider_vote_majorite():
    """
    Test de la fonction valider_vote pour le type 'majorite'.
    """
    from models.game import valider_vote
    # Un vote majoritaire
    assert valider_vote(['1', '2', '1'], 'majorite') == (True, '1')
    # Pas de majorité
    assert valider_vote(['1', '2', '3'], 'majorite') == (False, False)
    # Liste vide
    assert valider_vote([], 'majorite') == (False, False)

def test_valider_vote_invalid_type():
    """
    Test de la fonction valider_vote avec un type de vote invalide.
    """
    from models.game import valider_vote
    with pytest.raises(AttributeError):
        valider_vote(['1', '2', '3'], 'invalid_type')