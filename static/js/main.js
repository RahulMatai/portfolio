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
            ${text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                  .replace(/\*(.*?)\*/g, '<em>$1</em>')
                  .replace(/\n/g, '<br>')
                  .replace(/•/g, '&bull;')}
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
    
    addMessage(message, true);
    chatInput.value = '';
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

// Hint questions
function askHint(btn) {
    chatInput.value = btn.textContent;
    sendMessage();
}

// Event listeners
chatSend.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Fetch and render projects dynamically
async function loadProjects() {
    try {
        const response = await fetch('/projects');
        const data = await response.json();
        
        const grid = document.getElementById('projectsGrid');
        grid.innerHTML = '';
        
        // Show only latest 3 projects
        const latest = data.projects.slice(-3);
        
        latest.forEach(project => {
            const card = document.createElement('div');
            card.className = `project-card ${project.color}`;
            
            const tags = project.tags.map(tag => 
                `<span class="tag">${tag}</span>`
            ).join('');
            
            const statusBadge = project.status === 'building' 
                ? '<span class="status-badge building">⚡ Building</span>'
                : '<span class="status-badge live">🟢 Live</span>';
            
            card.innerHTML = `
                <div class="project-day">${project.day}</div>
                ${statusBadge}
                <div class="project-name">${project.name}</div>
                <div class="project-desc">${project.description}</div>
                <div class="project-tags">${tags}</div>
                <div class="project-links">
                    <a href="${project.live_url}" class="proj-link" target="_blank">↗ Live App</a>
                    <a href="${project.github_url}" class="proj-link" target="_blank">⌥ GitHub</a>
                </div>
            `;
            
            grid.appendChild(card);
        });

        // View all button
        const viewAll = document.createElement('div');
        viewAll.style.cssText = 'grid-column: 1/-1; text-align: center; margin-top: 2rem;';
        viewAll.innerHTML = `
            <a href="https://github.com/RahulMatai" target="_blank" class="btn-secondary">
                View all projects on GitHub →
            </a>
        `;
        grid.appendChild(viewAll);
        
    } catch(error) {
        console.error('Failed to load projects:', error);
    }
}

// Fetch and render blog posts dynamically
async function loadBlogs() {
    try {
        const response = await fetch('/Blogs');
        const data = await response.json();
        
        const grid = document.getElementById('blogGrid');
        grid.innerHTML = '';
        
        data.blogs.forEach(blog => {
            const card = document.createElement('div');
            card.className = 'blog-card';
            
            card.innerHTML = `
                <div class="blog-date">${blog.date}</div>
                <div class="blog-title">${blog.title}</div>
                <div class="blog-excerpt">${blog.excerpt}</div>
                <span class="blog-tag">${blog.tag}</span>
            `;
            
            card.addEventListener('click', () => {
                window.open(blog.url, '_blank');
            });
            
            grid.appendChild(card);
        });
        
    } catch(error) {
        console.error('Failed to load blogs:', error);
    }
}

// Load blogs on page load
loadBlogs();

// Load projects on page load
loadProjects();