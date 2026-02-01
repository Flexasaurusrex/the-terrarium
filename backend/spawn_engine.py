import time
import schedule
from datetime import datetime, timedelta
from database import TerrariumDB
from agent_generator import generate_identity, generate_intro_post, generate_topic_thread, generate_comment, select_random_archetype, should_agent_interact, determine_relationship_type, perform_web_search
from config import *
import firebase_admin
from firebase_admin import credentials, db as firebase_db
import random

class TerrariumSpawnEngine:
    def __init__(self):
        self.db = TerrariumDB(DB_PATH)
        self.init_firebase()
        self.agent_counter = 0
        self.topic_counter = 0
        
    def init_firebase(self):
        """Initialize Firebase for real-time updates"""
        try:
            cred = credentials.Certificate(FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred, {
                'databaseURL': FIREBASE_DB_URL
            })
            print("✓ Firebase initialized")
        except Exception as e:
            print(f"⚠ Firebase init failed: {e}")
    
    def generate_unique_identity(self, archetype):
        """Generate identity with uniqueness check against Firebase"""
        max_attempts = 10
        
        for attempt in range(max_attempts):
            human_name, age, role = generate_identity(archetype)
            
            # Check Firebase for existing names
            try:
                agents_ref = firebase_db.reference('/agents')
                existing_agents = agents_ref.get()
                
                if existing_agents:
                    existing_names = [agent.get('human_name', '').lower() for agent in existing_agents.values()]
                    
                    # Check if first OR last name already used
                    name_parts = human_name.lower().split()
                    first_name = name_parts[0] if name_parts else ''
                    last_name = name_parts[-1] if len(name_parts) > 1 else ''
                    
                    # Check if full name OR either part already exists
                    names_match = any(
                        existing_name == human_name.lower() or
                        existing_name.split()[0] == first_name or
                        (len(existing_name.split()) > 1 and existing_name.split()[-1] == last_name)
                        for existing_name in existing_names
                    )
                    
                    if not names_match:
                        print(f"  ✓ Unique name generated: {human_name}")
                        return human_name, age, role
                    else:
                        print(f"  ⚠ Name conflict: {human_name} (attempt {attempt + 1})")
                        continue
                else:
                    return human_name, age, role
                    
            except Exception as e:
                print(f"  ⚠ Error checking names: {e}")
                return human_name, age, role
        
        print(f"  ⚠ WARNING: Could not generate unique name after {max_attempts} attempts")
        return human_name, age, role
    
    def create_agent_zero(self):
        """Create the first agent (Agent-0) if doesn't exist"""
        # Check Firebase first to see if agents already exist
        try:
            ref = firebase_db.reference('/stats')
            firebase_stats = ref.get()
            
            if firebase_stats and firebase_stats.get('total_agents', 0) > 0:
                print(f"✓ Terrarium already has {firebase_stats['total_agents']} agents. Skipping Agent-0 creation.")
                # Set agent counter to continue from existing agents
                agents_ref = firebase_db.reference('/agents')
                existing_agents = agents_ref.get()
                if existing_agents:
                    # Find highest agent number by parsing agent_name
                    max_agent_num = 0
                    for agent in existing_agents.values():
                        agent_name = agent.get('agent_name', 'Agent-0')
                        try:
                            agent_num = int(agent_name.split('-')[1])
                            if agent_num > max_agent_num:
                                max_agent_num = agent_num
                        except:
                            pass
                    self.agent_counter = max_agent_num + 1
                    print(f"✓ Resuming from Agent-{self.agent_counter}")
                    
                # Also get highest topic number
                try:
                    topics_ref = firebase_db.reference('/topics')
                    existing_topics = topics_ref.get()
                    if existing_topics:
                        max_topic_num = 0
                        for topic in existing_topics.values():
                            topic_id = topic.get('topic_id', 0)
                            if topic_id > max_topic_num:
                                max_topic_num = topic_id
                        self.topic_counter = max_topic_num + 1
                        print(f"✓ Resuming topics from Topic-{self.topic_counter}")
                except:
                    self.topic_counter = 0
                    
                return
        except Exception as e:
            print(f"⚠ Could not check Firebase for existing agents: {e}")
        
        # Only create Agent-0 if Firebase is empty
        print("Creating Agent-0...")
        
        archetype = select_random_archetype()
        human_name, age, role = self.generate_unique_identity(archetype)
        
        intro = generate_intro_post(
            agent_name="Agent-0",
            human_name=human_name,
            age=age,
            role=role,
            parent_name="None",
            parent_gen=0,
            generation=0,
            archetype=archetype
        )
        
        # CRITICAL FIX: Use agent_counter (0) as agent_id
        agent_id = 0
        
        # Still create in database for compatibility
        db_id = self.db.create_agent(
            agent_name="Agent-0",
            human_name=human_name,
            age=age,
            role=role,
            parent_id=None,
            generation=0,
            archetype=archetype,
            first_post=intro
        )
        
        # Push Agent-0 to Firebase with consistent ID
        self.push_to_firebase({
            'agent_id': agent_id,  # Use 0, not db_id
            'agent_name': "Agent-0",
            'human_name': human_name,
            'age': age,
            'role': role,
            'generation': 0,
            'archetype': archetype,
            'first_post': intro,
            'parent_id': None,
            'released_at': datetime.now().isoformat(),
            'comments': []
        })
        
        self.agent_counter = 1
        
        print(f"✓ Agent-0 created: {human_name} ({archetype}, {role})")
        print(f"  Post: {intro[:80]}...")
    
    def generate_batch(self):
        """Generate a batch of agents"""
        # Check Firebase stats instead of local DB
        try:
            stats_ref = firebase_db.reference('/stats')
            stats = stats_ref.get()
            
            if stats and stats.get('kill_switch_active', False):
                print("⚠ Kill switch active. Stopping generation.")
                return
        except:
            stats = self.db.get_stats()
            if stats['kill_switch_active']:
                print("⚠ Kill switch active. Stopping generation.")
                return
        
        # Get parents from Firebase
        try:
            agents_ref = firebase_db.reference('/agents')
            firebase_agents = agents_ref.get()
            
            if not firebase_agents:
                print("⚠ No parents available yet. Waiting...")
                return
            
            # Convert Firebase agents to parent list
            parents = []
            for agent_data in firebase_agents.values():
                parents.append((
                    agent_data.get('agent_id'),
                    agent_data.get('agent_name'),
                    agent_data.get('human_name'),
                    agent_data.get('generation'),
                    agent_data.get('archetype')
                ))
            
        except Exception as e:
            print(f"⚠ Error getting parents from Firebase: {e}")
            parents = self.db.get_available_parents()
        
        if not parents:
            print("⚠ No parents available yet. Waiting...")
            return
        
        print(f"\n🌱 Generating batch of {BATCH_SIZE} agents...")
        
        batch_start_time = datetime.now() + timedelta(seconds=30)
        
        for i in range(BATCH_SIZE):
            parent_id, parent_name, parent_human_name, parent_gen, parent_archetype = random.choice(parents)
            
            agent_name = f"Agent-{self.agent_counter}"
            generation = parent_gen + 1
            archetype = select_random_archetype(parent_archetype)
            
            try:
                # Generate unique identity with Firebase checking
                human_name, age, role = self.generate_unique_identity(archetype)
                
                intro = generate_intro_post(
                    agent_name=agent_name,
                    human_name=human_name,
                    age=age,
                    role=role,
                    parent_name=parent_name,
                    parent_gen=parent_gen,
                    generation=generation,
                    archetype=archetype
                )
                
                # CRITICAL FIX: Use agent_counter as agent_id (not SQLite auto-increment)
                agent_id = self.agent_counter
                
                # Still create in database for compatibility
                db_id = self.db.create_agent(
                    agent_name=agent_name,
                    human_name=human_name,
                    age=age,
                    role=role,
                    parent_id=parent_id,
                    generation=generation,
                    archetype=archetype,
                    first_post=intro
                )
                
                release_time = batch_start_time + timedelta(seconds=i * RELEASE_INTERVAL)
                self.db.queue_for_release(db_id, release_time)  # Use db_id for queue
                
                print(f"  ✓ {agent_name} (ID: {agent_id}) - {human_name} (Gen {generation}, {archetype}, {role}) → release at {release_time.strftime('%H:%M:%S')}")
                
                self.agent_counter += 1
                
            except Exception as e:
                print(f"  ✗ Error generating {agent_name}: {e}")
        
        print(f"✓ Batch complete. Next batch in {BATCH_INTERVAL} seconds.\n")
    
    def release_agents(self):
        """Release agents from queue that are ready"""
        ready = self.db.get_agents_ready_for_release()
        
        for queue_id, db_id, agent_name, human_name, age, role, generation, archetype, first_post, parent_id in ready:
            self.db.mark_released(queue_id, db_id)
            
            # Extract agent number from agent_name to get consistent agent_id
            try:
                agent_num = int(agent_name.split('-')[1])
                agent_id =
