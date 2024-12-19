from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response
from models.game import valider_vote

app = Flask(__name__)
app.secret_key = 'azerty'  # Nécessaire pour utiliser les sessions

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        num_players = request.form.get('num_players')
        players = [request.form.get(f'player_{i+1}') for i in range(int(num_players))]
        rules = request.form.get('rules')

        session['players'] = players
        session['rules'] = rules
        session['index_player'] = 0
        session['liste_vote'] = []
        session['features'] = []  # Liste des fonctionnalités
        session['current_feature_index'] = 0  # Index de la fonctionnalité en cours
        session['results'] = {}  # Résultats finaux pour chaque fonctionnalité

        return redirect(url_for('propose_features'))
    return render_template('settings.html')

# Liste temporaire pour stocker les fonctionnalités proposées
features = []

@app.route('/propose_features', methods=['GET', 'POST'])
def propose_features():
    global features
    if request.method == 'POST':
        # Ajout d'une nouvelle fonctionnalité
        new_feature = request.form.get('feature')
        if new_feature:
            features.append(new_feature)  # Ajout à la liste
        return redirect(url_for('propose_features'))
    return render_template('propose_features.html', features=features)

@app.route('/delete_feature', methods=['POST'])
def delete_feature():
    global features
    data = request.get_json()
    feature_to_delete = data.get('feature')
    if feature_to_delete in features:
        features.remove(feature_to_delete)
        return jsonify({"success": True})  # Réponse JSON pour confirmer la suppression
    return jsonify({"success": False})  # Erreur si la fonctionnalité n'existe pas

@app.route('/game', methods=['GET', 'POST'])
def game():
    players = session.get('players', [])
    features = session.get('features', [])
    
    # Vérifier si la fonctionnalité courante est terminée
    current_feature_index = session.get('current_feature_index', 0)
    current_player_index = session['index_player'] % len(players)

    # Si la fonctionnalité actuelle est terminée, on passe à la suivante
    if current_feature_index >= len(features):
        return redirect(url_for('results'))  # Si toutes les fonctionnalités sont traitées, on passe aux résultats.

    current_feature = features[current_feature_index]

    # Gestion du vote
    if request.method == 'POST':
        valeur_choisi = request.form.get('valeur_choisi')
        session['liste_vote'].append(int(valeur_choisi))
        session['index_player'] += 1  # Passer au joueur suivant
        
        # Vérifier si tous les joueurs ont voté
        if current_player_index >= len(players)-1:
            # Vérification des votes de tous les joueurs
            resultat, chiffrage = valider_vote(session['liste_vote'], session['rules'])
            
            if resultat:  # Tous d'accord
                # Enregistrer le vote pour la fonctionnalité et passer à la suivante
                session['results'][current_feature] = chiffrage
                session['current_feature_index'] += 1  # Passer à la fonctionnalité suivante
                session['index_player'] = 0  # Réinitialiser l'index du joueur
                session['liste_vote'] = []  # Réinitialiser les votes
            else:
                # Désaccord, lancer un débat
                min_vote = min(session['liste_vote'])
                max_vote = max(session['liste_vote'])
                print("session liste vote : ", session['liste_vote'])
                print("min : ", min_vote, " et max : ", max_vote)
                print("index max : ", session['liste_vote'].index(max_vote))
                print("liste joueur : ", players)
                debate_players = [
                    players[session['liste_vote'].index(min_vote)],
                    players[session['liste_vote'].index(max_vote)]
                ]
                print("liste debate players", debate_players)
                session['revote'] = True  # Flag pour le revote
                session['liste_vote'] = []  # Réinitialiser les votes
                return render_template('debate.html', feature=current_feature, debate_players=debate_players, vote=[min_vote, max_vote])

            # Revenir à la page de jeu après avoir enregistré les résultats
            return redirect(url_for('game'))
    
    # Recalcule si changement
    current_player_index = session['index_player'] % len(players)

    # Afficher le joueur et la fonctionnalité actuels
    return render_template('game.html', player=players[current_player_index], feature=current_feature)

@app.route('/debate', methods=['GET'])
def debate():
    return redirect(url_for('game'))

@app.route('/results')
def results():
    results = session.get('results', {})
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)