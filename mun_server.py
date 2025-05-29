from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_ici'  # Remplacez par une clé unique en production
socketio = SocketIO(app)

# Dictionnaire pour stocker les utilisateurs connectés (ID de session -> nom)
users = {}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/chat')
def comite():
    return render_template('comite.html')

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
