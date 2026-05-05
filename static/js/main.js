// Get DOM elements
const chatBody = document.getElementById('chatBody');
const chatInput = document.getElementById('chatInput');
const chatSend = document.getElementById('chatSend');

// Add a message bubble to the chat
function addMessage(text, isUser) {
    const msg = document.createElement('div');
    msg.className = `msg ${isUser ? 'msg-right' : ''}`;
    
    msg.innerHTML = `
        <div class="msg-avatar ${isUser ? 'avatar-user' : 'avatar-ai'}">
            ${isUser ? 'U' : 'R'}
        </div>
        <div class="msg-bubble ${isUser ? 'bubble-user' : 'bubble-ai'}">
            ${text}
        </div>
    `;
    
    chatBody.appendChild(msg);
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Show typing indicator
function showTyping() {
    const typing = document.createElement('div');
    typing.className = 'msg';
    typing.id = 'typing';
    typing.innerHTML = `
        <div class="msg-avatar avatar-ai">R</div>
        <div class="msg-bubble bubble-ai">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;
    chatBody.appendChild(typing);
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Remove typing indicator
function removeTyping() {
    const typing = document.getElementById('typing');
    if (typing) typing.remove();
}

// Send message to Flask backend
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Show user message
    addMessage(message, true);
    chatInput.value = '';
    
    // Show typing
    showTyping();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        removeTyping();
        addMessage(data.response, false);
        
    } catch (error) {
        removeTyping();
        addMessage('Sorry, something went wrong. Please try again.', false);
    }
}

// Event listeners
chatSend.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});