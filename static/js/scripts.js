const socket = io();

function joinChat() {
    const username = document.getElementById('username').value.trim();
    if (username) {
        socket.emit('join', { username: username });
        window.location.href = '/chat';
    } else {
        alert('Veuillez entrer un pseudo.');
    }
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    if (message) {
        socket.emit('send_message', { message: message });
        messageInput.value = '';
    }
}

socket.on('message', (data) => {
    const messages = document.getElementById('messages');
    if (messages) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.textContent = `${data.username}: ${data.message}`;
        messages.appendChild(messageElement);
        messages.scrollTop = messages.scrollHeight;
    }
});

socket.on('update_users', (users) => {
    const userList = document.getElementById('userList');
    if (userList) {
        userList.textContent = users.join(', ');
    }
});