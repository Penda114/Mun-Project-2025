from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_ici'  # Remplacez par une clé unique en production
socketio = SocketIO(app)

# Dictionnaire pour stocker les utilisateurs connectés (ID de session -> nom)
users = {}

# Liste des comités actifs (exemple: [nom, créateur, type, langue, participants, code])
committees = [
    ["NOM COP 1", "Nom Joueur 1", "vocal", "Français", 0, "1234"],
    ["NOM COP 2", "Nom Joueur 2", "chat", "Anglais", 0, "5678"]
]

# Liste prédéfinie des thèmes possibles
THEMES = ["Environnement", "Santé", "Éducation", "Sécurité", "Technologie"]

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/chat')
def comite():
    return render_template('comite.html')

# Route pour vérifier le code
@app.route('/check_code', methods=['POST'])
def check_code():
    data = request.json
    entered_code = data.get('code')
    valid_code = "1234"  # Code valide temporaire
    if entered_code == valid_code:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Code invalide"})

# Route pour la page de création
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        theme = request.form['theme']
        language = request.form['language']
        committee_type = request.form['type']
        code = request.form['code'].strip()
        username = list(users.values())[0] if users else "Inconnu"  # Utilise le premier utilisateur connecté comme créateur

        # Vérifier si le code existe déjà
        if any(committee[5] == code for committee in committees):
            return render_template('create.html', themes=THEMES, error="Ce code est déjà utilisé.")

        # Ajouter le nouveau comité
        committees.append([theme, username, committee_type, language, 0, code])
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
