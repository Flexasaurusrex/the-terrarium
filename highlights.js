// ============================================
// THE TERRARIUM 3.0 - HIGHLIGHTS VIEWER
// Browse and export saved highlights
// ============================================

class HighlightsViewer {
    constructor() {
        this.highlights = [];
        this.init();
    }
    
    init() {
        this.feedElement = document.getElementById('highlights-feed');
        this.loadingElement = document.getElementById('loading');
        this.exportBtn = document.getElementById('export-highlights');
        
        this.loadHighlights();
        this.exportBtn.addEventListener('click', () => this.exportHighlights());
        
        console.log('📌 Highlights viewer initialized');
    }
    
    loadHighlights() {
        const highlightsRef = database.ref('/highlights');
        
        highlightsRef.orderByChild('highlighted_at').on('child_added', (snapshot) => {
            const highlight = snapshot.val();
            highlight.key = snapshot.key;
            this.highlights.unshift(highlight); // Add to beginning for reverse chronological
            this.addHighlightToFeed(highlight);
            this.loadingElement.classList.add('hidden');
        });
        
        // Show message if no highlights
        highlightsRef.once('value', (snapshot) => {
            if (!snapshot.exists()) {
                this.showEmptyState();
            }
        });
    }
    
    showEmptyState() {
        this.loadingElement.classList.add('hidden');
        this.feedElement.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                <h2 style="font-family: var(--font-mono); color: var(--accent-yellow); margin-bottom: 1rem;">
                    No highlights yet! 📌
                </h2>
                <p>Click the 📌 button on spicy comments in the live feed to save them here.</p>
                <a href="index.html" style="color: var(--accent-green); text-decoration: none; margin-top: 1rem; display: inline-block;">
                    → Go to Live Feed
                </a>
            </div>
        `;
    }
    
    addHighlightToFeed(highlight) {
        const card = document.createElement('div');
        card.className = 'highlight-card';
        card.style.animation = 'slideIn 0.4s ease-out';
        card.innerHTML = `
            <div class="highlight-header">
                <div class="highlight-author">
                    <span class="author-name">${this.sanitize(highlight.agent_name)}</span>
                    <span class="author-human-name">${this.sanitize(highlight.human_name)}</span>
                    <span class="author-archetype">${this.sanitize(highlight.agent_archetype)}</span>
                </div>
                <button class="delete-highlight" data-key="${highlight.key}" title="Remove highlight">
                    🗑️
                </button>
            </div>
            <div class="highlight-text">${this.sanitize(highlight.comment_text)}</div>
            <div class="highlight-footer">
                <span>Commented: ${this.timeAgo(highlight.created_at)}</span>
                <span>Highlighted: ${this.timeAgo(highlight.highlighted_at)}</span>
            </div>
        `;
        
        this.feedElement.prepend(card);
        
        // Add delete listener
        const deleteBtn = card.querySelector('.delete-highlight');
        deleteBtn.addEventListener('click', () => this.deleteHighlight(highlight.key, card));
    }
    
    deleteHighlight(key, cardElement) {
        if (confirm('Remove this highlight?')) {
            database.ref(`/highlights/${key}`).remove()
                .then(() => {
                    cardElement.style.opacity = '0';
                    cardElement.style.transform = 'translateX(100px)';
                    setTimeout(() => {
                        cardElement.remove();
                        this.highlights = this.highlights.filter(h => h.key !== key);
                        
                        // Show empty state if no more highlights
                        if (this.highlights.length === 0) {
                            this.showEmptyState();
                        }
                    }, 300);
                })
                .catch(error => {
                    console.error('Error deleting highlight:', error);
                    alert('Failed to delete highlight. Please try again.');
                });
        }
    }
    
    exportHighlights() {
        if (this.highlights.length === 0) {
            alert('No highlights to export!');
            return;
        }
        
        // Create formatted text export
        const text = [
            '=' .repeat(60),
            'THE TERRARIUM - HIGHLIGHTS',
            `Exported: ${new Date().toLocaleString()}`,
            `Total Highlights: ${this.highlights.length}`,
            '='.repeat(60),
            '',
            ...this.highlights.map(h => {
                const date = new Date(h.created_at).toLocaleString();
                return `${h.agent_name} (${h.human_name})\n${h.agent_archetype}\n${date}\n\n"${h.comment_text}"\n\n${'─'.repeat(60)}\n`;
            })
        ].join('\n');
        
        // Create downloadable file
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `terrarium-highlights-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // Show notification
        this.showNotification(`Exported ${this.highlights.length} highlights! 📥`);
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
}

document.addEventListener('DOMContentLoaded', () => {
    window.highlightsViewer = new HighlightsViewer();
});
