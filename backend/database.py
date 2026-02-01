import sqlite3
from datetime import datetime, timedelta
import json

class TerrariumDB:
    def __init__(self, db_path='/tmp/terrarium.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database with schema"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT UNIQUE NOT NULL,
                human_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                role TEXT NOT NULL,
                parent_id INTEGER,
                generation INTEGER NOT NULL,
                archetype TEXT NOT NULL,
                first_post TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                released_at TIMESTAMP,
                status TEXT DEFAULT 'queued',
                faction_id INTEGER,
                interaction_count INTEGER DEFAULT 0,
                last_interaction_at TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES agents(id)
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                target_agent_id INTEGER NOT NULL,
                target_comment_id INTEGER,
                comment_text TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agents(id),
                FOREIGN KEY (target_agent_id) REFERENCES agents(id),
                FOREIGN KEY (target_comment_id) REFERENCES comments(id)
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                target_agent_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                strength INTEGER DEFAULT 1,
                last_updated TIMESTAMP NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agents(id),
                FOREIGN KEY (target_agent_id) REFERENCES agents(id),
                UNIQUE(agent_id, target_agent_id)
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS factions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP NOT NULL,
                member_count INTEGER DEFAULT 0
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                creator_agent_id INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL,
                supporter_count INTEGER DEFAULT 1,
                opposer_count INTEGER DEFAULT 0,
                FOREIGN KEY (creator_agent_id) REFERENCES agents(id)
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS movement_participation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movement_id INTEGER NOT NULL,
                agent_id INTEGER NOT NULL,
                stance TEXT NOT NULL,
                joined_at TIMESTAMP NOT NULL,
                FOREIGN KEY (movement_id) REFERENCES movements(id),
                FOREIGN KEY (agent_id) REFERENCES agents(id),
                UNIQUE(movement_id, agent_id)
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS spawn_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                scheduled_release TIMESTAMP NOT NULL,
                released BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY,
                total_agents INTEGER DEFAULT 0,
                current_generation INTEGER DEFAULT 0,
                start_time TIMESTAMP,
                kill_switch_active BOOLEAN DEFAULT FALSE,
                total_comments INTEGER DEFAULT 0,
                total_factions INTEGER DEFAULT 0,
                total_movements INTEGER DEFAULT 0
            )
        ''')
        
        c.execute('SELECT COUNT(*) FROM stats')
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO stats (id, start_time) VALUES (1, ?)', 
                     (datetime.now(),))
        
        conn.commit()
        conn.close()
    
    def create_agent(self, agent_name, human_name, age, role, parent_id, generation, archetype, first_post):
        """Create new agent in database with identity"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        created_at = datetime.now()
        
        c.execute('''
            INSERT INTO agents (agent_name, human_name, age, role, parent_id, generation, archetype, first_post, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'queued')
        ''', (agent_name, human_name, age, role, parent_id, generation, archetype, first_post, created_at))
        
        agent_id = c.lastrowid
        
        conn.commit()
        conn.close()
        
        return agent_id
    
    def queue_for_release(self, agent_id, scheduled_release):
        """Add agent to release queue"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO spawn_queue (agent_id, scheduled_release, released)
            VALUES (?, ?, FALSE)
        ''', (agent_id, scheduled_release))
        
        conn.commit()
        conn.close()
    
    def get_agents_ready_for_release(self):
        """Get agents scheduled for release now or earlier"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        now = datetime.now()
        
        c.execute('''
            SELECT q.id, q.agent_id, a.agent_name, a.human_name, a.age, a.role, a.generation, a.archetype, a.first_post, a.parent_id
            FROM spawn_queue q
            JOIN agents a ON q.agent_id = a.id
            WHERE q.released = FALSE AND q.scheduled_release <= ?
            ORDER BY q.scheduled_release ASC
        ''', (now,))
        
        results = c.fetchall()
        conn.close()
        
        return results
    
    def mark_released(self, queue_id, agent_id):
        """Mark agent as released"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        released_at = datetime.now()
        
        c.execute('UPDATE spawn_queue SET released = TRUE WHERE id = ?', (queue_id,))
        c.execute('UPDATE agents SET status = ?, released_at = ? WHERE id = ?',
                 ('live', released_at, agent_id))
        
        conn.commit()
        conn.close()
    
    def get_available_parents(self):
        """Get agents that can spawn children (already released)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, agent_name, human_name, generation, archetype
            FROM agents
            WHERE status = 'live'
            ORDER BY RANDOM()
        ''')
        
        results = c.fetchall()
        conn.close()
        
        return results
    
    def get_agents_ready_for_interaction(self):
        """Get agents who can interact (past cooldown period)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, agent_name, human_name, generation, archetype, interaction_count, last_interaction_at
            FROM agents
            WHERE status = 'live'
        ''')
        
        results = c.fetchall()
        conn.close()
        
        return results
    
    def get_recent_posts_for_interaction(self, limit=20):
        """Get recent posts/comments that agents might interact with"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT a.id, a.agent_name, a.human_name, a.archetype, a.first_post, a.released_at, 'post' as type
            FROM agents a
            WHERE a.status = 'live'
            ORDER BY a.released_at DESC
            LIMIT ?
        ''', (limit,))
        
        posts = c.fetchall()
        
        c.execute('''
            SELECT c.id, a.agent_name, a.human_name, a.archetype, c.comment_text, c.created_at, 'comment' as type
            FROM comments c
            JOIN agents a ON c.agent_id = a.id
            ORDER BY c.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        comments = c.fetchall()
        
        conn.close()
        
        all_content = posts + comments
        all_content.sort(key=lambda x: x[5], reverse=True)
        
        return all_content[:limit]
    
    def create_comment(self, agent_id, target_agent_id, comment_text, target_comment_id=None):
        """Create a comment from one agent to another"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        created_at = datetime.now()
        
        c.execute('''
            INSERT INTO comments (agent_id, target_agent_id, target_comment_id, comment_text, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (agent_id, target_agent_id, target_comment_id, comment_text, created_at))
        
        comment_id = c.lastrowid
        
        c.execute('''
            UPDATE agents 
            SET interaction_count = interaction_count + 1, last_interaction_at = ?
            WHERE id = ?
        ''', (created_at, agent_id))
        
        c.execute('UPDATE stats SET total_comments = total_comments + 1 WHERE id = 1')
        
        conn.commit()
        conn.close()
        
        return comment_id
    
    def update_relationship(self, agent_id, target_agent_id, relationship_type):
        """Update or create relationship between two agents"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        now = datetime.now()
        
        c.execute('''
            SELECT id, strength FROM relationships 
            WHERE agent_id = ? AND target_agent_id = ?
        ''', (agent_id, target_agent_id))
        
        existing = c.fetchone()
        
        if existing:
            new_strength = existing[1] + 1
            c.execute('''
                UPDATE relationships 
                SET relationship_type = ?, strength = ?, last_updated = ?
                WHERE id = ?
            ''', (relationship_type, new_strength, now, existing[0]))
        else:
            c.execute('''
                INSERT INTO relationships (agent_id, target_agent_id, relationship_type, strength, last_updated)
                VALUES (?, ?, ?, 1, ?)
            ''', (agent_id, target_agent_id, relationship_type, now))
        
        conn.commit()
        conn.close()
    
    def get_stats(self):
        """Get current terrarium stats"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM agents WHERE status = "live"')
        total_live = c.fetchone()[0]
        
        c.execute('SELECT MAX(generation) FROM agents WHERE status = "live"')
        max_gen = c.fetchone()[0] or 0
        
        c.execute('SELECT COUNT(*) FROM comments')
        total_comments = c.fetchone()[0]
        
        c.execute('SELECT start_time, kill_switch_active FROM stats WHERE id = 1')
        stats = c.fetchone()
        
        conn.close()
        
        return {
            'total_agents': total_live,
            'current_generation': max_gen,
            'total_comments': total_comments,
            'start_time': stats[0] if stats else None,
            'kill_switch_active': bool(stats[1]) if stats else False
        }
    
    def activate_kill_switch(self):
        """Activate the kill switch"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('UPDATE stats SET kill_switch_active = TRUE WHERE id = 1')
        
        conn.commit()
        conn.close()
    
    def get_agent_details(self, agent_id):
        """Get full details for an agent"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, agent_name, human_name, age, role, archetype, generation, first_post, interaction_count
            FROM agents WHERE id = ?
        ''', (agent_id,))
        
        result = c.fetchone()
        conn.close()
        
        return result
