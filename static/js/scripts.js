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

function checkCode() {
    const codeInput = document.getElementById('codeInput').value.trim();
    if (codeInput) {
        fetch('/check_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: codeInput })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect;
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Erreur:', error));
    } else {
        alert('Veuillez entrer un code.');
    }
}

function createRoom() {
    window.location.href = '/create';
}

function sendChatMessage(room) {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    if (message) {
        socket.emit('send_chat_message', { room: room, message: message });
        chatInput.value = '';
    }
}

document.getElementById('joinCodeBtn').addEventListener('click', checkCode);
document.getElementById('createRoomBtn').addEventListener('click', createRoom);

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

socket.on('chat_message', (data) => {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.textContent = `${data.username}: ${data.message}`;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

socket.on('update_participants', (data) => {
    const participantsDiv = document.getElementById('participants');
    const participantCount = document.getElementById('participantCount');
    const playerList = document.getElementById('playerList');
    if (participantsDiv && participantCount && playerList) {
        const count = data.participants;
        participantsDiv.innerHTML = '';
        for (let i = 0; i < count; i++) {
            const dot = document.createElement('span');
            dot.classList.add('participant-dot');
            participantsDiv.appendChild(dot);
        }
        for (let i = count; i < 20; i++) {
            const dot = document.createElement('span');
            dot.classList.add('empty-dot');
            participantsDiv.appendChild(dot);
        }
        participantCount.textContent = `${count}/20`;
        playerList.innerHTML = '';
        for (let sid in data.players) {
            const playerDiv = document.createElement('div');
            playerDiv.textContent = data.players[sid].username;
            playerList.appendChild(playerDiv);
        }
    }
});

socket.on('start_game', (data) => {
    window.location.href = data.redirect;
});

socket.on('update_committees', (committees) => {
    const committeeList = document.getElementById('committeeList');
    if (committeeList) {
        committeeList.innerHTML = '';
        if (committees.length === 0) {
            committeeList.innerHTML = '<p>aucun comité encore actif</p>';
        } else {
            committees.forEach(committee => {
                const div = document.createElement('div');
                div.classList.add('committee-item');
                div.style.cursor = 'pointer';
                div.addEventListener('click', () => {
                    window.location.href = `/wait?code=${committee.code}`;
                });
                div.innerHTML = `
                    <span>${committee.creator}</span>
                    <span>${committee.type}</span>
                    <span>${committee.language}</span>
                    <span>${committee.name}</span>
                    <span>${committee.participants}/20</span>
                `;
                committeeList.appendChild(div);
            });
        }
    }
});

// Initial population
updateCommitteeList();

function updateCommitteeList() {
    fetch('/get_committees')
        .then(response => response.json())
        .then(committees => {
            const committeeList = document.getElementById('committeeList');
            if (committeeList) {
                committeeList.innerHTML = '';
                if (committees.length === 0) {
                    committeeList.innerHTML = '<p>aucun comité encore actif</p>';
                } else {
                    committees.forEach(committee => {
                        const div = document.createElement('div');
                        div.classList.add('committee-item');
                        div.style.cursor = 'pointer';
                        div.addEventListener('click', () => {
                            window.location.href = `/wait?code=${committee.code}`;
                        });
                        div.innerHTML = `
                            <span>${committee.creator}</span>
                            <span>${committee.type}</span>
                            <span>${committee.language}</span>
                            <span>${committee.name}</span>
                            <span>${committee.participants}/20</span>
                        `;
                        committeeList.appendChild(div);
                    });
                }
            }
        })
        .catch(error => console.error('Erreur:', error));
}