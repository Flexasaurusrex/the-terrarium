// ============================================
// THE TERRARIUM 2.0 - FRONTEND APP
// Real-time agent feed with comments
// ============================================

class TerrariumApp {
    constructor() {
        this.agents = new Map(); // Store agents by ID for comment threading
        this.stats = {
            total_agents: 0,
            current_generation: 0,
            total_comments: 0,
            start_time: null
        };
        
        this.init();
    }
    
    init() {
        // DOM elements
        this.feedElement = document.getElementById('agent-feed');
        this.loadingElement = document.getElementById('loading');
        this.totalAgentsElement = document.getElementById('total-agents');
        this.currentGenElement = document.getElementById('current-gen');
        this.totalCommentsElement = document.getElementById('total-comments');
        this.uptimeElement = document.getElementById('uptime');
        
        // Listen to Firebase
        this.listenForAgents();
        this.listenForComments();
        this.listenForStats();
        
        // Start uptime counter
        this.startUptimeCounter();
        
        // Setup modals
        this.setupModals();
        
        // Setup kill switch
        this.setupKillSwitch();
        
        console.log('🌱 Terrarium 2.0 initialized');
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
            this.addCommentToAgent(comment);
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
        // Store agent data
        this.agents.set(agent.agent_id, agent);
        
        // Create agent card
        const card = document.createElement('div');
        card.className = 'agent-card';
        card.id = `agent-${agent.agent_id}`;
        card.innerHTML = `
            <div class="agent-header">
                <span class="agent-name">${this.sanitize(agent.agent_name)}</span>
                <div class="agent-meta">
                    <span>Gen ${agent.generation}</span>
                </div>
            </div>
            <div class="agent-archetype">${this.sanitize(agent.archetype)}</div>
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
        
        // Add to feed (newest at top)
        this.feedElement.prepend(card);
        
        // Limit feed to 50 agents (performance)
        const cards = this.feedElement.querySelectorAll('.agent-card');
        if (cards.length > 50) {
            cards[cards.length - 1].remove();
        }
    }
    
    addCommentToAgent(comment) {
        const commentsSection = document.getElementById(`comments-${comment.target_agent_id}`);
        
        if (!commentsSection) {
            // Target agent not in current view
            return;
        }
        
        // Create comment element
        const commentEl = document.createElement('div');
        commentEl.className = 'comment';
        commentEl.innerHTML = `
            <div class="comment-header">
                <span class="comment-author">${this.sanitize(comment.agent_name)}</span>
                <span class="comment-archetype">${this.sanitize(comment.agent_archetype)}</span>
            </div>
            <div class="comment-text">${this.sanitize(comment.comment_text)}</div>
            <div class="comment-time">${this.timeAgo(comment.created_at)}</div>
        `;
        
        // Add comment to section
        commentsSection.appendChild(commentEl);
        
        // Animate in
        setTimeout(() => commentEl.classList.add('visible'), 10);
    }
    
    updateStatsDisplay() {
        this.totalAgentsElement.textContent = this.stats.total_agents || 0;
        this.currentGenElement.textContent = this.stats.current_generation || 0;
        this.totalCommentsElement.textContent = this.stats.total_comments || 0;
    }
    
    startUptimeCounter() {
        setInterval(() => {
            if (this.stats.start_time) {
                const uptime = this.calculateUptime(this.stats.start_time);
                this.uptimeElement.textContent = uptime;
            }
        }, 1000);
    }
    
    calculateUptime(startTime) {
        const start = new Date(startTime);
        const now = new Date();
        const diff = now - start;
        
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        
        return `${hours}h ${minutes}m`;
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
        // Basic XSS protection
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    setupModals() {
        // About modal
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
        
        // Note: Kill switch backend not implemented yet
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.terrariumApp = new TerrariumApp();
});
