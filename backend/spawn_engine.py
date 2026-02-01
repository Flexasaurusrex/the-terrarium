import time
import schedule
from datetime import datetime, timedelta
from database import TerrariumDB
from agent_generator import generate_intro_post, select_random_archetype
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
            # Use credentials from environment variable
            cred = credentials.Certificate(FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred, {
                'databaseURL': FIREBASE_DB_URL
            })
            print("✓ Firebase initialized")
        except Exception as e:
            print(f"⚠ Firebase init failed: {e}")
    
    def create_agent_zero(self):
        """Create the first agent (Agent-0) if doesn't exist"""
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
            
            # Release immediately
            self.db.queue_for_release(agent_id, datetime.now())
            self.agent_counter = 1
            
            print(f"✓ Agent-0 created: {archetype}")
            print(f"  Post: {intro[:80]}...")
    
    def generate_batch(self):
        """Generate a batch of agents"""
        stats = self.db.get_stats()
        
        if stats['kill_switch_active']:
            print("⚠ Kill switch active. Stopping generation.")
            return
        
        parents = self.db.get_available_parents()
        
        if not parents:
            print("⚠ No parents available yet. Waiting...")
            return
        
        print(f"\n🌱 Generating batch of {BATCH_SIZE} agents...")
        
        batch_start_time = datetime.now() + timedelta(seconds=30)  # Start releasing in 30 seconds
        
        for i in range(BATCH_SIZE):
            # Select random parent
            parent_id, parent_name, parent_gen, parent_archetype = random.choice(parents)
            
            # Generate agent details
            agent_name = f"Agent-{self.agent_counter}"
            generation = parent_gen + 1
            archetype = select_random_archetype(parent_archetype)
            
            # Generate intro post
            try:
                intro = generate_intro_post(
                    agent_name=agent_name,
                    parent_name=parent_name,
                    parent_gen=parent_gen,
                    generation=generation,
                    archetype=archetype
                )
                
                # Save to database
                agent_id = self.db.create_agent(
                    agent_name=agent_name,
                    parent_id=parent_id,
                    generation=generation,
                    archetype=archetype,
                    first_post=intro
                )
                
                # Queue for release (1 per minute)
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
            # Mark as released in DB
            self.db.mark_released(queue_id, agent_id)
            
            # Push to Firebase for real-time frontend
            self.push_to_firebase({
                'agent_id': agent_id,
                'agent_name': agent_name,
                'generation': generation,
                'archetype': archetype,
                'first_post': first_post,
                'parent_id': parent_id,
                'released_at': datetime.now().isoformat()
            })
            
            print(f"🔴 LIVE: {agent_name} (Gen {generation}, {archetype})")
    
    def push_to_firebase(self, agent_data):
        """Push agent to Firebase for real-time updates"""
        try:
            ref = firebase_db.reference('/agents')
            ref.push(agent_data)
            
            # Update stats
            stats = self.db.get_stats()
            stats_ref = firebase_db.reference('/stats')
            stats_ref.set(stats)
            
        except Exception as e:
            print(f"⚠ Firebase push failed: {e}")
    
    def run(self):
        """Main spawn engine loop"""
        print("=" * 60)
        print("THE TERRARIUM - SPAWN ENGINE")
        print("=" * 60)
        
        # Create Agent-0 if needed
        self.create_agent_zero()
        
        # Schedule batch generation
        schedule.every(BATCH_INTERVAL).seconds.do(self.generate_batch)
        
        # Generate first batch immediately
        self.generate_batch()
        
        print(f"\n🌱 Spawn engine running...")
        print(f"   Batch generation: every {BATCH_INTERVAL}s")
        print(f"   Release rate: 1 agent every {RELEASE_INTERVAL}s")
        print(f"   Press Ctrl+C to stop\n")
        
        # Main loop
        while True:
            try:
                # Check for scheduled batch generation
                schedule.run_pending()
                
                # Check for agents ready to release
                self.release_agents()
                
                # Sleep briefly
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
