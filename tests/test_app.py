import pytest
from app import app

@pytest.fixture
def client():
    """
    Fixture pour configurer un client de test Flask.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
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