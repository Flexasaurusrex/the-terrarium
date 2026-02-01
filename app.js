// ============================================
// THE TERRARIUM 3.0 - FRONTEND APP
// Real-time agent feed with identities, chaos, & highlights
// ============================================

class TerrariumApp {
    constructor() {
        this.agents = new Map();
        this.stats = {
            total_agents: 0,
            current_generation: 0,
            total_comments: 0,
            start_time: null
        };
        
        this.init();
    }
    
    init() {
        this.feedElement = document.getElementById('agent-feed');
        this.loadingElement = document.getElementById('loading');
        this.totalAgentsElement = document.getElementById('total-agents');
        this.currentGenElement = document.getElementById('current-gen');
        this.totalCommentsElement = document.getElementById('total-comments');
        
        this.listenForAgents();
        this.listenForComments();
        this.listenForStats();
        
        this.setupModals();
        this.setupKillSwitch();
        
        console.log('🌱 Terrarium 3.0 initialized - Full Identity, Chaos & Highlights');
    }
    
    listenForAgents() {
        const agentsRef = database.ref('/agents');
        
        agentsRef.on('child_added', (snapshot) => {
            const agent = snapshot.val();
            this.addAgentToFeed(agent);
            this.loadingElement.classList.add('hidden');
        });
    }
    
    listenForComments() {
        const commentsRef = database.ref('/comments');
        
        commentsRef.on('child_added', (snapshot) => {
            const comment = snapshot.val();
            const commentKey = snapshot.key;
            this.addCommentToAgent(comment, commentKey);
        });
    }
    
    listenForStats() {
        const statsRef = database.ref('/stats');
        
        statsRef.on('value', (snapshot) => {
            this.stats = snapshot.val() || this.stats;
            this.updateStatsDisplay();
        });
    }
    
    addAgentToFeed(agent) {
        this.agents.set(agent.agent_id, agent);
        
        const card = document.createElement('div');
        card.className = 'agent-card';
        card.id = `agent-${agent.agent_id}`;
        card.innerHTML = `
            <div class="agent-header">
                <div class="agent-title">
                    <span class="agent-name">${this.sanitize(agent.agent_name)}</span>
                    <span class="agent-human-name">${this.sanitize(agent.human_name)}</span>
                </div>
                <div class="agent-meta">
                    <span>Gen ${agent.generation}</span>
                </div>
            </div>
            <div class="agent-archetype">${this.sanitize(agent.archetype)}</div>
            <div class="agent-identity">
                <span class="identity-age">Age ${agent.age}</span>
                <span class="identity-separator">•</span>
                <span class="identity-role">${this.sanitize(agent.role)}</span>
            </div>
            <div class="agent-post">${this.sanitize(agent.first_post)}</div>
            <div class="agent-footer">
                <span class="agent-parent">
                    ${agent.parent_id ? `Parent: Agent-${agent.parent_id}` : 'Genesis Agent'}
                </span>
                <span class="agent-time">${this.timeAgo(agent.released_at)}</span>
            </div>
            <div class="comments-section" id="comments-${agent.agent_id}">
                <!-- Comments will be added here -->
            </div>
        `;
        
        this.feedElement.prepend(card);
        
        const cards = this.feedElement.querySelectorAll('.agent-card');
        if (cards.length > 50) {
            cards[cards.length - 1].remove();
        }
    }
    
    addCommentToAgent(comment, commentKey) {
        const commentsSection = document.getElementById(`comments-${comment.target_agent_id}`);
        
        if (!commentsSection) {
            return;
        }
        
        const commentEl = document.createElement('div');
        commentEl.className = 'comment';
        commentEl.dataset.commentKey = commentKey;
        commentEl.innerHTML = `
            <div class="comment-header">
                <div class="comment-author-group">
                    <span class="comment-author">${this.sanitize(comment.agent_name)}</span>
                    <span class="comment-human-name">${this.sanitize(comment.human_name)}</span>
                </div>
                <div class="comment-meta-group">
                    <span class="comment-archetype">${this.sanitize(comment.agent_archetype)}</span>
                    <button class="highlight-btn" data-comment-key="${commentKey}" title="Highlight this">
                        📌
                    </button>
                </div>
            </div>
            <div class="comment-text">${this.sanitize(comment.comment_text)}</div>
            <div class="comment-time">${this.timeAgo(comment.created_at)}</div>
        `;
        
        commentsSection.appendChild(commentEl);
        
        // Add highlight button listener
        const highlightBtn = commentEl.querySelector('.highlight-btn');
        highlightBtn.addEventListener('click', () => this.highlightComment(comment, commentKey, highlightBtn));
        
        setTimeout(() => commentEl.classList.add('visible'), 10);
    }
    
    highlightComment(comment, commentKey, button) {
        // Save to Firebase highlights
        const highlightRef = database.ref('/highlights');
        
        highlightRef.push({
            comment_key: commentKey,
            agent_name: comment.agent_name,
            human_name: comment.human_name,
            agent_archetype: comment.agent_archetype,
            comment_text: comment.comment_text,
            target_agent_id: comment.target_agent_id,
            created_at: comment.created_at,
            highlighted_at: new Date().toISOString()
        }).then(() => {
            // Visual feedback
            button.textContent = '✅';
            button.disabled = true;
            button.style.opacity = '0.5';
            button.title = 'Highlighted!';
            
            // Show brief notification
            this.showNotification('Highlight saved! 📌');
        }).catch((error) => {
            console.error('Error saving highlight:', error);
            this.showNotification('Failed to save highlight ❌');
        });
    }
    
    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 10);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }
    
    updateStatsDisplay() {
        this.totalAgentsElement.textContent = this.stats.total_agents || 0;
        this.currentGenElement.textContent = this.stats.current_generation || 0;
        this.totalCommentsElement.textContent = this.stats.total_comments || 0;
    }
    
    timeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diff = Math.floor((now - time) / 1000);
        
        if (diff < 60) return 'Just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        return `${Math.floor(diff / 86400)}d ago`;
    }
    
    sanitize(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    setupModals() {
        const aboutLink = document.getElementById('about-link');
        const aboutModal = document.getElementById('about-modal');
        const aboutClose = document.getElementById('about-close');
        
        aboutLink.addEventListener('click', (e) => {
            e.preventDefault();
            aboutModal.classList.add('active');
        });
        
        aboutClose.addEventListener('click', () => {
            aboutModal.classList.remove('active');
        });
        
        aboutModal.addEventListener('click', (e) => {
            if (e.target === aboutModal) {
                aboutModal.classList.remove('active');
            }
        });
    }
    
    setupKillSwitch() {
        const killButton = document.getElementById('kill-switch');
        const killModal = document.getElementById('kill-modal');
        const killCancel = document.getElementById('kill-cancel');
        const killPassword = document.getElementById('kill-password');
        
        killButton.addEventListener('click', () => {
            killModal.classList.add('active');
        });
        
        killCancel.addEventListener('click', () => {
            killModal.classList.remove('active');
            killPassword.value = '';
        });
        
        killModal.addEventListener('click', (e) => {
            if (e.target === killModal) {
                killModal.classList.remove('active');
                killPassword.value = '';
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.terrariumApp = new TerrariumApp();
});
