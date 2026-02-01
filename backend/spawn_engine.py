import time
import schedule
from datetime import datetime, timedelta
from database import TerrariumDB
from agent_generator import generate_intro_post, generate_comment, select_random_archetype, should_agent_interact, determine_relationship_type
from config import *
import firebase_admin
from firebase_admin import credentials, db as firebase_db
import random

class TerrariumSpawnEngine:
    def __init__(self):
        self.db = TerrariumDB(DB_PATH)
        self.init_firebase()
        self.agent_counter = 0
        
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
                return
        except Exception as e:
            print(f"⚠ Could not check Firebase for existing agents: {e}")
        
        # Only create Agent-0 if Firebase is empty
        stats = self.db.get_stats()
        
        if stats['total_agents'] == 0:
            print("Creating Agent-0...")
            
            archetype = select_random_archetype()
            intro = generate_intro_post(
                agent_name="Agent-0",
                parent_name="None",
                parent_gen=0,
                generation=0,
                archetype=archetype
            )
            
            agent_id = self.db.create_agent(
                agent_name="Agent-0",
                parent_id=None,
                generation=0,
                archetype=archetype,
                first_post=intro
            )
            
            self.db.queue_for_release(agent_id, datetime.now())
            self.agent_counter = 1
            
            print(f"✓ Agent-0 created: {archetype}")
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
            parent_id, parent_name, parent_gen, parent_archetype = random.choice(parents)
            
            agent_name = f"Agent-{self.agent_counter}"
            generation = parent_gen + 1
            archetype = select_random_archetype(parent_archetype)
            
            try:
                intro = generate_intro_post(
                    agent_name=agent_name,
                    parent_name=parent_name,
                    parent_gen=parent_gen,
                    generation=generation,
                    archetype=archetype
                )
                
                agent_id = self.db.create_agent(
                    agent_name=agent_name,
                    parent_id=parent_id,
                    generation=generation,
                    archetype=archetype,
                    first_post=intro
                )
                
                release_time = batch_start_time + timedelta(seconds=i * RELEASE_INTERVAL)
                self.db.queue_for_release(agent_id, release_time)
                
                print(f"  ✓ {agent_name} (Gen {generation}, {archetype}) → release at {release_time.strftime('%H:%M:%S')}")
                
                self.agent_counter += 1
                
            except Exception as e:
                print(f"  ✗ Error generating {agent_name}: {e}")
        
        print(f"✓ Batch complete. Next batch in {BATCH_INTERVAL} seconds.\n")
    
    def release_agents(self):
        """Release agents from queue that are ready"""
        ready = self.db.get_agents_ready_for_release()
        
        for queue_id, agent_id, agent_name, generation, archetype, first_post, parent_id in ready:
            self.db.mark_released(queue_id, agent_id)
            
            self.push_to_firebase({
                'agent_id': agent_id,
                'agent_name': agent_name,
                'generation': generation,
                'archetype': archetype,
                'first_post': first_post,
                'parent_id': parent_id,
                'released_at': datetime.now().isoformat(),
                'comments': []
            })
            
            print(f"🔴 LIVE: {agent_name} (Gen {generation}, {archetype})")
    
    def process_interactions(self):
        """Process agent interactions (comments, relationships)"""
        # Check Firebase for kill switch
        try:
            stats_ref = firebase_db.reference('/stats')
            stats = stats_ref.get()
            if stats and stats.get('kill_switch_active', False):
                return
        except:
            pass
        
        # Get agents from Firebase for interaction
        try:
            agents_ref = firebase_db.reference('/agents')
            firebase_agents = agents_ref.get()
            
            if not firebase_agents:
                return
            
            # Convert to list for processing
            agents = []
            for agent_data in firebase_agents.values():
                agents.append((
                    agent_data.get('agent_id'),
                    agent_data.get('agent_name'),
                    agent_data.get('generation'),
                    agent_data.get('archetype'),
                    0,  # interaction_count - we'll track this differently
                    None  # last_interaction
                ))
        except Exception as e:
            print(f"⚠ Error getting agents for interaction: {e}")
            agents = self.db.get_agents_ready_for_interaction()
        
        recent_content = self.db.get_recent_posts_for_interaction(limit=20)
        
        if not recent_content:
            return
        
        for agent_data in agents:
            agent_id, agent_name, generation, archetype, interaction_count, last_interaction = agent_data
            
            if not should_agent_interact(archetype, last_interaction, interaction_count or 0):
                continue
            
            target_content = random.choice(recent_content)
            target_id, target_name, target_archetype, target_text, target_time, content_type = target_content
            
            if target_name == agent_name:
                continue
            
            try:
                comment_text = generate_comment(
                    agent_name=agent_name,
                    agent_archetype=archetype,
                    target_post=target_text,
                    target_agent_name=target_name,
                    target_archetype=target_archetype
                )
                
                comment_id = self.db.create_comment(
                    agent_id=agent_id,
                    target_agent_id=target_id,
                    comment_text=comment_text
                )
                
                relationship_type = determine_relationship_type(archetype, target_archetype, "positive")
                self.db.update_relationship(agent_id, target_id, relationship_type)
                
                self.push_comment_to_firebase({
                    'comment_id': comment_id,
                    'agent_id': agent_id,
                    'agent_name': agent_name,
                    'agent_archetype': archetype,
                    'target_agent_id': target_id,
                    'comment_text': comment_text,
                    'created_at': datetime.now().isoformat()
                })
                
                print(f"💬 {agent_name} ({archetype}) commented on {target_name}'s post")
                
            except Exception as e:
                print(f"⚠ Error generating comment: {e}")
    
    def push_to_firebase(self, agent_data):
        """Push agent to Firebase for real-time updates"""
        try:
            ref = firebase_db.reference('/agents')
            ref.push(agent_data)
            
            # Update stats based on Firebase data
            agents_ref = firebase_db.reference('/agents')
            all_agents = agents_ref.get()
            
            if all_agents:
                total = len(all_agents)
                max_gen = max([a.get('generation', 0) for a in all_agents.values()])
                
                stats_ref = firebase_db.reference('/stats')
                stats_ref.update({
                    'total_agents': total,
                    'current_generation': max_gen
                })
            
        except Exception as e:
            print(f"⚠ Firebase push failed: {e}")
    
    def push_comment_to_firebase(self, comment_data):
        """Push comment to Firebase"""
        try:
            ref = firebase_db.reference('/comments')
            ref.push(comment_data)
            
            # Update comment count
            comments_ref = firebase_db.reference('/comments')
            all_comments = comments_ref.get()
            
            if all_comments:
                stats_ref = firebase_db.reference('/stats')
                stats_ref.update({
                    'total_comments': len(all_comments)
                })
            
        except Exception as e:
            print(f"⚠ Firebase comment push failed: {e}")
    
    def run(self):
        """Main spawn engine loop"""
        print("=" * 60)
        print("THE TERRARIUM 2.0 - SPAWN ENGINE WITH SOCIAL DYNAMICS")
        print("=" * 60)
        
        self.create_agent_zero()
        
        schedule.every(BATCH_INTERVAL).seconds.do(self.generate_batch)
        
        self.generate_batch()
        
        print(f"\n🌱 Spawn engine running...")
        print(f"   Batch generation: every {BATCH_INTERVAL}s")
        print(f"   Release rate: 1 agent every {RELEASE_INTERVAL}s")
        print(f"   Interaction checks: every {INTERACTION_CHECK_INTERVAL}s")
        print(f"   Press Ctrl+C to stop\n")
        
        last_interaction_check = datetime.now()
        
        while True:
            try:
                schedule.run_pending()
                self.release_agents()
                
                if (datetime.now() - last_interaction_check).total_seconds() >= INTERACTION_CHECK_INTERVAL:
                    self.process_interactions()
                    last_interaction_check = datetime.now()
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("\n\n⚠ Spawn engine stopped by user")
                break
            except Exception as e:
                print(f"⚠ Error in main loop: {e}")
                time.sleep(10)


if __name__ == "__main__":
    engine = TerrariumSpawnEngine()
    engine.run()
