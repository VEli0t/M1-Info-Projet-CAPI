from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response
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

        # Enregistrer les paramètres dans la session
        session['players'] = players
        session['rules'] = rules
        session['index_player'] = 0
        session['liste_vote'] = []
        session['features'] = []  # Liste des fonctionnalités
        session['current_feature_index'] = 0  # Index de la fonctionnalité en cours
        session['results'] = {}  # Résultats finaux pour chaque fonctionnalité

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
    @brief Gère le processus de vote pour chaque fonctionnalité.
    - GET : Affiche la fonctionnalité et le joueur actuel.
    - POST : Enregistre un vote et traite les désaccords.

    @return Redirection ou affichage de la page de jeu.
    """
    players = session.get('players', [])
    features = session.get('features', [])
    current_feature_index = session.get('current_feature_index', 0)
    current_player_index = session['index_player'] % len(players)

    if current_feature_index >= len(features):
        return redirect(url_for('results'))

    current_feature = features[current_feature_index]

    if request.method == 'POST':
        valeur_choisi = request.form.get('valeur_choisi')
        session['liste_vote'].append(int(valeur_choisi))
        session['index_player'] += 1

        if current_player_index >= len(players) - 1:
            resultat, chiffrage = valider_vote(session['liste_vote'], session['rules'])
            if resultat:
                session['results'][current_feature] = chiffrage
                session['current_feature_index'] += 1
                session['index_player'] = 0
                session['liste_vote'] = []
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
    return render_template('game.html', player=players[current_player_index], feature=current_feature)

@app.route('/debate', methods=['GET'])
def debate():
    """
    @brief Gère la redirection pendant un débat.
    @return Redirection vers la page de jeu.
    """
    return redirect(url_for('game'))

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