from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        num_players = request.form.get('num_players')
        players = [request.form.get(f'player_{i+1}') for i in range(int(num_players))]
        rules = request.form.get('rules')

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

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/results')
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True)
