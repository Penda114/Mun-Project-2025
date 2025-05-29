from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_ici'  # Remplacez par une clé unique en production
socketio = SocketIO(app)

# Chemin du fichier JSON pour stocker les comités
COMMITTEES_FILE = "committees.json"

# Dictionnaire pour stocker les utilisateurs connectés (ID de session -> nom)
users = {}

# Liste prédéfinie des thèmes possibles
THEMES = ["Environnement", "Santé", "Éducation", "Sécurité", "Technologie"]

# Fonction pour charger les comités depuis le fichier JSON
def load_committees():
    if not os.path.exists(COMMITTEES_FILE):
        # Initialiser avec des données par défaut si le fichier n'existe pas
        initial_data = [
            {"name": "NOM COP 1", "creator": "Nom Joueur 1", "type": "vocal", "language": "Français", "participants": 5, "code": "1234"},
            {"name": "NOM COP 2", "creator": "Nom Joueur 2", "type": "chat", "language": "Anglais", "participants": 10, "code": "5678"}
        ]
        with open(COMMITTEES_FILE, 'w') as f:
            json.dump(initial_data, f, indent=4)
        return initial_data
    with open(COMMITTEES_FILE, 'r') as f:
        return json.load(f)

# Fonction pour sauvegarder les comités dans le fichier JSON
def save_committees(committees):
    with open(COMMITTEES_FILE, 'w') as f:
        json.dump(committees, f, indent=4)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/chat')
def comite():
    return render_template('comite.html')

# Route pour vérifier le code et rediriger vers la salle d'attente
@app.route('/check_code', methods=['POST'])
def check_code():
    data = request.json
    entered_code = data.get('code')
    committees = load_committees()
    
    # Vérifier si le code existe dans les comités
    for COP in committees:
        if entered_code == COP["code"]:
            return jsonify({"success": True, "redirect": f"/wait?code={entered_code}"})
    return jsonify({"success": False, "message": "Code invalide"})

# Route pour récupérer la liste des comités
@app.route('/get_committees', methods=['GET'])
def get_committees():
    committees = load_committees()
    return jsonify(committees)

# Route pour la page d'attente
@app.route('/wait')
def wait():
    code = request.args.get('code')
    committees = load_committees()
    
    # Trouver le comité correspondant au code
    committee = next((COP for COP in committees if COP["code"] == code), None)
    if not committee:
        return "Comité non trouvé", 404
    
    return render_template('wait.html', committee=committee)

# Route pour la page de création
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        theme = request.form['theme']
        language = request.form['language']
        committee_type = request.form['type']
        code = request.form['code'].strip()
        username = list(users.values())[0] if users else "Inconnu"  # Utilise le premier utilisateur connecté comme créateur

        committees = load_committees()

        # Vérifier si le code existe déjà
        for COP in committees:
            if code == COP["code"]:
                return render_template('create.html', themes=THEMES, error="Ce code est déjà utilisé.")

        # Ajouter le nouveau comité
        new_committee = {
            "name": theme,
            "creator": username,
            "type": committee_type,
            "language": language,
            "participants": 0,
            "code": code
        }
        committees.append(new_committee)
        save_committees(committees)
        return redirect(url_for('comite'))

    return render_template('create.html', themes=THEMES)

# Événement de connexion
@socketio.on('connect')
def handle_connect():
    print('Nouvelle connexion établie')

# Événement quand un utilisateur rejoint
@socketio.on('join')
def handle_join(data):
    username = data['username']
    session_id = request.sid
    users[session_id] = username
    # Annoncer l'arrivée de l'utilisateur à tous
    socketio.emit('message', {'username': 'Système', 'message': f'{username} a rejoint le salon !'})
    # Mettre à jour la liste des utilisateurs pour tous les clients
    socketio.emit('update_users', list(users.values()))

# Événement quand un message est envoyé
@socketio.on('send_message')
def handle_message(data):
    username = users.get(request.sid, 'Inconnu')
    message = data['message']
    socketio.emit('message', {'username': username, 'message': message})

# Événement de déconnexion
@socketio.on('disconnect')
def handle_disconnect():
    username = users.pop(request.sid, 'Inconnu')
    socketio.emit('message', {'username': 'Système', 'message': f'{username} a quitté le salon.'})
    socketio.emit('update_users', list(users.values()))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
