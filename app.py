import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response, send_file
from models.game import valider_vote

app = Flask(__name__)
app.secret_key = 'azerty'  # Nécessaire pour utiliser les sessions

@app.route('/')
def home():
    """
    @brief Affiche la page d'accueil.
    @return Le template HTML de la page d'accueil.
    """
    return render_template('home.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """
    @brief Gère la configuration des paramètres du jeu.
    - GET : Affiche la page de configuration.
    - POST : Enregistre les paramètres dans la session.

    @return Redirection vers la page de proposition de fonctionnalités ou affichage de la page de configuration.
    """
    if request.method == 'POST':
        num_players = request.form.get('num_players')
        players = [request.form.get(f'player_{i+1}') for i in range(int(num_players))]
        rules = request.form.get('rules')
        time_limit = request.form.get('time_limit', 30)
        no_time_limit = request.form.get('no_time_limit', False)

        # Enregistrer les paramètres dans la session
        if no_time_limit:
            session['time_limit'] = None  # Pas de limite
        else:
            session['time_limit'] = int(time_limit)

        session['players'] = players
        session['rules'] = rules
        session['index_player'] = 0
        session['liste_vote'] = []
        session['features'] = []  # Liste des fonctionnalités
        session['current_feature_index'] = 0  # Index de la fonctionnalité en cours
        session['results'] = {}  # Résultats finaux pour chaque fonctionnalité
        session['time_limit'] = int(time_limit)  # Stockage du temps limite

        return redirect(url_for('propose_features'))
    return render_template('settings.html')

@app.route('/propose_features', methods=['GET', 'POST'])
def propose_features():
    """
    @brief Gère la proposition de fonctionnalités par les utilisateurs.
    - GET : Affiche la liste des fonctionnalités proposées.
    - POST : Ajoute une nouvelle fonctionnalité.

    @return Redirection ou affichage de la page de proposition de fonctionnalités.
    """
    if 'features' not in session:
        session['features'] = []  # Initialiser si absent

    if request.method == 'POST':
        new_feature = request.form.get('feature')
        if new_feature:
            features = session['features']
            features.append(new_feature)
            session['features'] = features
        return redirect(url_for('propose_features'))

    return render_template('propose_features.html', features=session['features'])

@app.route('/delete_feature', methods=['POST'])
def delete_feature():
    """
    @brief Supprime une fonctionnalité proposée.
    @return Réponse JSON confirmant la suppression ou indiquant une erreur.
    """
    data = request.get_json()
    feature_to_delete = data.get('feature')
    if 'features' in session and feature_to_delete in session['features']:
        # Supprime la fonctionnalité et met à jour la session
        features = session['features']
        features.remove(feature_to_delete)
        session['features'] = features  # Réaffecter pour mettre à jour la session
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/game', methods=['GET', 'POST'])
def game():
    """
    @brief Gère le processus de vote pour chaque fonctionnalité, joueur par joueur.
    - GET : Affiche la fonctionnalité et le joueur actuel, avec un temps limite.
    - POST : Enregistre un vote ou passe au joueur suivant si pas de vote.
    
    @details
    Le temps est géré côté front. Si le joueur n'a pas voté avant la fin du temps,
    il vote 'interro'. Lorsque tous les joueurs ont été itérés, on évalue le résultat.
    Si tous ont voté "cafe", on passe en mode pause.
    Si le vote est unanime ou majoritaire, on enregistre le résultat.
    Si le vote enregistrer est 'interro', alors une phase de discussion est mise ne place,
    avant de revoter la fonctionnalité.
    Si personne n'a voté, on relance la même fonctionnalité.

    @return Redirection ou affichage de la page de jeu.
    """
    players = session.get('players', [])
    features = session.get('features', [])
    current_feature_index = session.get('current_feature_index', 0)
    current_player_index = session['index_player'] % len(players)
    time_limit = session.get('time_limit', 30)

    if current_feature_index >= len(features):
        return redirect(url_for('results'))

    current_feature = features[current_feature_index]

    if request.method == 'POST':

        # Si on revient de "interro", ne pas incrémenter `index_player` et son choix
        if not session.get('revote', False):
            session['index_player'] += 1
            valeur_choisi = request.form.get('valeur_choisi', 'interro')  # Si le joueur n'a pas eu le temps de répondre = 'interro'
        else:
            session['revote'] = False  # Désactiver l'état de revote
            session['index_player'] = 0  # Revenir au premier joueur
            valeur_choisi = None

        if valeur_choisi:
            # Valeur café/interro ou chiffre
            if valeur_choisi == "cafe" or valeur_choisi == "interro":
                session['liste_vote'].append(valeur_choisi)
            else:
                session['liste_vote'].append(int(valeur_choisi))

            # Si on a traité tous les joueurs pour cette fonctionnalité
            if (session['index_player'] % len(players)) == 0:
                # Evaluation du vote
                resultat, chiffrage = valider_vote(session['liste_vote'], session['rules'])
                if resultat:
                    session['liste_vote'] = []
                    session['index_player'] = 0
                    if chiffrage == "cafe":
                        # Tous ont voté café, rediriger vers /pause
                        return redirect(url_for('pause'))
                    elif chiffrage == "interro":
                        # Tous ont voté "interro", rediriger vers /interro
                        return redirect(url_for('interro'))
                    else:
                        # On a un résultat valide (unanime ou majorite)
                        session['results'][current_feature] = chiffrage
                        session['current_feature_index'] += 1
                else:
                    # Aucun résultat majoritaire/unanime.
                    if len(session['liste_vote']) == 0:
                        # Personne n'a voté, on recommence le tour
                        session['index_player'] = 0
                        # Pas de changement de current_feature_index
                    else:
                        min_vote = min(session['liste_vote'])
                        max_vote = max(session['liste_vote'])
                        debate_players = [
                            players[session['liste_vote'].index(min_vote)],
                            players[session['liste_vote'].index(max_vote)]
                        ]
                        session['revote'] = True
                        session['liste_vote'] = []
                        return render_template('debate.html', feature=current_feature, debate_players=debate_players, vote=[min_vote, max_vote])

            return redirect(url_for('game'))

    current_player_index = session['index_player'] % len(players)
    return render_template('game.html', 
                           player=players[current_player_index], 
                           feature=current_feature, 
                           time_limit=time_limit)

@app.route('/debate', methods=['GET'])
def debate():
    """
    @brief Gère la redirection pendant un débat.
    @return Redirection vers la page de jeu.
    """
    return redirect(url_for('game'))

@app.route('/interro')
def interro():
    """
    @brief Affiche une page spéciale lorsque tous les joueurs votent "interro".

    @details
    - Cette page demande aux joueurs d'expliquer ou justifier leur vote.
    - Elle propose un bouton pour revenir à la fonctionnalité en cours ou relancer le vote.
    
    @return Le template 'interro.html'.
    """
    # Réinitialiser index_player pour recommencer le tour
    session['index_player'] = 0

    session['revote'] = True  # Indiquer qu'on revient d'une phase interro

    current_feature_index = session.get('current_feature_index', 0)
    features = session.get('features', [])
    current_feature = features[current_feature_index] if current_feature_index < len(features) else None

    return render_template('interro.html', feature=current_feature)

@app.route('/pause', methods=['GET', 'POST'])
def pause():
    """
    @brief Affiche l'écran de pause lorsque tous les joueurs ont voté 'cafe'.
    
    @details
    Sur cette page, deux options :
    - Télécharger la partie sauvegardée.
    - Retourner directement au jeu.
    
    @return Le template 'pause.html'.
    """
    if request.method == 'POST':
        # Crée un fichier de sauvegarde au format JSON
        game_state = {
            "players": session.get("players", []),
            "features": session.get("features", []),
            "current_feature_index": session.get("current_feature_index", 0),
            "index_player": session.get("index_player", 0),
            "rules": session.get("rules", "unanime"),
            "results": session.get("results", {}),
            "liste_vote": session.get("liste_vote", []),
            "time_limit": session.get("time_limit", None)
        }
        save_path = os.path.join(os.getcwd(), "sauvegarde.json")
        with open(save_path, "w") as f:
            json.dump(game_state, f)

        return send_file(save_path, as_attachment=True)

    return render_template('pause.html')

@app.route('/load_game', methods=['GET', 'POST'])
def load_game():
    """
    @brief Charge l'état d'une partie depuis un fichier JSON uploadé par l'utilisateur.

    @details
    - L'utilisateur upload un fichier JSON via un formulaire.
    - L'état du jeu est restauré dans la session.

    @return Redirection vers la page de jeu après chargement.
    """
    if request.method == 'POST':
        file = request.files.get('savefile')
        if file and file.filename.endswith('.json'):
            try:
                game_state = json.load(file)
                session['players'] = game_state.get("players", [])
                session['features'] = game_state.get("features", [])
                session['current_feature_index'] = game_state.get("current_feature_index", 0)
                session['index_player'] = game_state.get("index_player", 0)
                session['rules'] = game_state.get("rules", "unanime")
                session['results'] = game_state.get("results", {})
                session['liste_vote'] = game_state.get("liste_vote", [])
                session['time_limit'] = game_state.get("time_limit", None)
                return redirect(url_for('game'))
            except Exception as e:
                return f"Erreur lors du chargement de la sauvegarde : {e}", 400
        else:
            return "Veuillez fournir un fichier JSON valide.", 400
    return render_template('load_game.html')

@app.route('/results')
def results():
    """
    @brief Affiche les résultats finaux du processus de vote.
    @return Le template HTML avec les résultats.
    """
    results = session.get('results', {})
    return render_template('results.html', results=results)

if __name__ == '__main__':
    """
    @brief Point d'entrée de l'application Flask.
    """
    app.run(debug=True)