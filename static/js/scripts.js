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

// Populate committee list by fetching from the server
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

// Initial population
updateCommitteeList();