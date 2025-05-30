from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_ici'  # Remplacez par une clé unique en production
socketio = SocketIO(app)

# Chemin du fichier JSON pour stocker les comités
COMMITTEES_FILE = "committees.json"

# Dictionnaire pour stocker les utilisateurs connectés (ID de session -> nom)
users = {}

# Dictionnaire pour stocker les joueurs actifs par comité (code -> {sid: {"username": str, "photo": str}})
players = {}

# Liste prédéfinie des thèmes possibles
THEMES = ["Environnement", "Santé", "Éducation", "Sécurité", "Technologie"]

# Fonction pour charger les comités depuis le fichier JSON
def load_committees():
    if not os.path.exists(COMMITTEES_FILE):
        initial_data = []
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
    
    committee = next((COP for COP in committees if COP["code"] == code), None)
    if not committee:
        return "Comité non trouvé", 404
    
    return render_template('wait.html', committee=committee)

# Route pour la page de jeu
@app.route('/game')
def game():
    code = request.args.get('code')
    committees = load_committees()
    committee = next((COP for COP in committees if COP["code"] == code), None)
    if not committee:
        return "Comité non trouvé", 404
    return render_template('game.html', committee=committee)

# Route pour la page de création
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        theme = request.form['theme']
        language = request.form['language']
        committee_type = request.form['type']
        code = request.form['code'].strip()
        username = list(users.values())[0] if users else "Inconnu"

        committees = load_committees()

        for COP in committees:
            if code == COP["code"]:
                return render_template('create.html', themes=THEMES, error="Ce code est déjà utilisé.")

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
        socketio.emit('update_committees', committees)  # Notify clients of new committee
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
    socketio.emit('message', {'username': 'Système', 'message': f'{username} a rejoint le salon !'})
    socketio.emit('update_users', list(users.values()))

# Événement pour rejoindre une salle d'attente
@socketio.on('join_waiting_room')
def join_waiting_room(data):
    room = data['room']
    session_id = request.sid  # Define session_id here
    join_room(room)
    username = users.get(session_id, 'Inconnu')
    committees = load_committees()
    committee = next((COP for COP in committees if COP["code"] == room), None)
    if committee:
        if room not in players:
            players[room] = {}
        if session_id not in players[room]:
            players[room][session_id] = {"username": username, "photo": "default.jpg"}  # Placeholder for photo
            committee["participants"] = len(players[room])
            save_committees(committees)
        emit('update_participants', {'participants': committee["participants"], 'players': players[room]}, room=room)
        print(f"send {committee['participants']} and {players[room]}")
        emit('update_committees', committees, broadcast=True)  # Update all clients
        if committee["participants"] >= 20:
            emit('start_game', {'redirect': f"/game?code={room}"}, room=room)

# Événement pour envoyer un message dans la salle d'attente
@socketio.on('send_chat_message')
def handle_chat_message(data):
    room = data['room']
    message = data['message']
    username = users.get(request.sid, 'Inconnu')
    emit('chat_message', {'username': username, 'message': message}, room=room)

# Événement de déconnexion
@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    username = users.pop(session_id, 'Inconnu')
    socketio.emit('message', {'username': 'Système', 'message': f'{username} a quitté le salon.'})
    socketio.emit('update_users', list(users.values()))
    # Mettre à jour le nombre de participants si l'utilisateur était dans une salle d'attente
    client_rooms = rooms()
    for room in client_rooms:
        if room != session_id and room in [COP["code"] for COP in load_committees()]:
            if room in players and session_id in players[room]:
                del players[room][session_id]
                committees = load_committees()
                committee = next((COP for COP in committees if COP["code"] == room), None)
                if committee:
                    committee["participants"] = len(players.get(room, {}))
                    save_committees(committees)
                    emit('update_participants', {'participants': committee["participants"], 'players': players.get(room, {})}, room=room)
                    emit('update_committees', committees, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
