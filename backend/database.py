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
        
        # Agents table
        c.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT UNIQUE NOT NULL,
                parent_id INTEGER,
                generation INTEGER NOT NULL,
                archetype TEXT NOT NULL,
                first_post TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                released_at TIMESTAMP,
                status TEXT DEFAULT 'queued',
                FOREIGN KEY (parent_id) REFERENCES agents(id)
            )
        ''')
        
        # Spawn queue table
        c.execute('''
            CREATE TABLE IF NOT EXISTS spawn_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                scheduled_release TIMESTAMP NOT NULL,
                released BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            )
        ''')
        
        # Stats table
        c.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY,
                total_agents INTEGER DEFAULT 0,
                current_generation INTEGER DEFAULT 0,
                start_time TIMESTAMP,
                kill_switch_active BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Initialize stats if empty
        c.execute('SELECT COUNT(*) FROM stats')
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO stats (id, start_time) VALUES (1, ?)', 
                     (datetime.now(),))
        
        conn.commit()
        conn.close()
    
    def create_agent(self, agent_name, parent_id, generation, archetype, first_post):
        """Create new agent in database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        created_at = datetime.now()
        
        c.execute('''
            INSERT INTO agents (agent_name, parent_id, generation, archetype, first_post, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, 'queued')
        ''', (agent_name, parent_id, generation, archetype, first_post, created_at))
        
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
            SELECT q.id, q.agent_id, a.agent_name, a.generation, a.archetype, a.first_post, a.parent_id
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
        
        # Update queue
        c.execute('UPDATE spawn_queue SET released = TRUE WHERE id = ?', (queue_id,))
        
        # Update agent
        c.execute('UPDATE agents SET status = ?, released_at = ? WHERE id = ?',
                 ('live', released_at, agent_id))
        
        conn.commit()
        conn.close()
    
    def get_available_parents(self):
        """Get agents that can spawn children (already released)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, agent_name, generation, archetype
            FROM agents
            WHERE status = 'live'
            ORDER BY RANDOM()
        ''')
        
        results = c.fetchall()
        conn.close()
        
        return results
    
    def get_stats(self):
        """Get current terrarium stats"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM agents WHERE status = "live"')
        total_live = c.fetchone()[0]
        
        c.execute('SELECT MAX(generation) FROM agents WHERE status = "live"')
        max_gen = c.fetchone()[0] or 0
        
        c.execute('SELECT start_time, kill_switch_active FROM stats WHERE id = 1')
        stats = c.fetchone()
        
        conn.close()
        
        return {
            'total_agents': total_live,
            'current_generation': max_gen,
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
