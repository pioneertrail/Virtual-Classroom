let messageHistory = [];

function appendMessage(message, isUser) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    messageHistory.push({ role: isUser ? 'user' : 'assistant', content: message });
}

function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (message) {
        appendMessage(message, true);
        input.value = '';
        
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                history: messageHistory
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            appendMessage(data.response, false);
        })
        .catch(error => {
            console.error('Error:', error);
            appendMessage('Sorry, there was an error processing your message. Please try again.', false);
        });
    }
}

function sendCommand(command) {
    const input = document.getElementById('message-input');
    input.value = command;
    sendMessage();
}

// Add event listener for Enter key
document.getElementById('message-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Initialize with a welcome message
window.onload = function() {
    appendMessage('Welcome! How can I help you today?', false);
}; 