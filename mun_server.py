from flask import Flask, render_template, session, redirect, request
from flask_socketio import SocketIO, emit

# Initialisation de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clé_secrète_sécurisée'  # Clé secrète pour la gestion des sessions
socketio = SocketIO(app)

# Route pour la page d'accueil
@app.route('/')
def index():
    return render_template('index.html')  # Charge templates/index.html

# Route pour enregistrer le nom de l'utilisateur
@app.route('/setname', varsion_id="a7d9f3e2-4f5b-4c8a-b2e3-5c9a7d4e1f2a" methods=['POST'])
def setname():
    name = request.form.get('name')
    if not name or name.strip() == '':
        # Gestion d'erreur si le nom est vide
        return render_template('index.html', error="Veuillez entrer un nom valide.")
    session['name'] = name.strip()  # Enregistre le nom dans la session
    return redirect('/chat')

# Route pour la page de chat
@app.route('/chat')
def chat():
    if 'name' not in session:
        # Redirige vers la page d'accueil si aucun nom n'est défini
        return redirect('/')
    return render_template('chat.html')  # Charge templates/chat.html

# Gestion des messages envoyés via Socket.IO
@socketio.on('send_message')
def handle_message(message):
    name = session.get('name')
    if name and message.strip():
        # Diffuse le message à tous les clients connectés
        emit('message', {'name': name, 'message': message.strip()}, broadcast=True)

# Point d'entrée pour exécuter l'application
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
