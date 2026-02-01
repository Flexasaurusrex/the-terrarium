"""
TERRARIUM: LEGENDS NIGHT OUT
Main engine for the groundhog day loop
"""

import time
import schedule
from datetime import datetime, timedelta
from database import TerrariumDB
from legends_generator import generate_legend_intro, generate_legend_comment
from legends_personas import LEGENDS, SCENARIO_TIMELINE
from config import *
import firebase_admin
from firebase_admin import credentials, db as firebase_db
import random

class LegendsEngine:
    def __init__(self):
        self.db = TerrariumDB(DB_PATH)
        self.init_firebase()
        self.loop_number = 1
        self.loop_start_time = None
        self.loop_duration_minutes = 360  # 6 hours simulated
        self.comment_counter = 0
        
    def init_firebase(self):
        """Initialize Firebase"""
        try:
            creds = FIREBASE_CREDENTIALS.copy()
            if 'private_key' in creds:
                creds['private_key'] = creds['private_key'].replace('\\n', '\n')
            
            cred = credentials.Certificate(creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': FIREBASE_DB_URL
            })
            print("✓ Firebase initialized")
        except Exception as e:
            print(f"⚠ Firebase init failed: {e}")
            raise
    
    def get_loop_time_minutes(self):
        """Get current time within the loop (0-360 minutes)"""
        if not self.loop_start_time:
            return 0
        elapsed = (datetime.now() - self.loop_start_time).total_seconds() / 60
        return int(elapsed % self.loop_duration_minutes)
    
    def start_new_loop(self):
        """Start a new loop - reset everything"""
        print(f"\n{'='*60}")
        print(f"🔄 STARTING LOOP #{self.loop_number}")
        print(f"{'='*60}\n")
        
        self.loop_start_time = datetime.now()
        self.comment_counter = 0
        
        # Clear Firebase
        try:
            firebase_db.reference('/legends').delete()
            firebase_db.reference('/comments').delete()
        except:
            pass
        
        # Create the three legends in Firebase
        legends_ref = firebase_db.reference('/legends')
        
        for legend_id, legend_data in LEGENDS.items():
            intro = generate_legend_intro(legend_id, 0, self.loop_number)
            
            legends_ref.push({
                'legend_id': legend_id,
                'agent_name': legend_data['agent_name'],
                'human_name': legend_data['human_name'],
                'age': legend_data['age'],
                'role': legend_data['role'],
                'archetype': legend_data['archetype'],
                'first_post': intro,
                'loop_number': self.loop_number,
                'spawned_at': datetime.now().isoformat()
            })
            
            print(f"🎭 {legend_data['human_name']}: {intro}")
        
        # Update stats
        stats_ref = firebase_db.reference('/stats')
        stats_ref.set({
            'loop_number': self.loop_number,
            'loop_start_time': self.loop_start_time.isoformat(),
            'total_comments': 0,
            'legends_count': 3
        })
    
    def generate_interaction(self):
        """Generate a random interaction between legends"""
        try:
            loop_time = self.get_loop_time_minutes()
            
            # Pick random speaker and target
            legend_ids = list(LEGENDS.keys())
            speaker_id = random.choice(legend_ids)
            target_id = random.choice([lid for lid in legend_ids if lid != speaker_id])
            
            # Get recent comment from target or use their intro
            legends_ref = firebase_db.reference('/legends')
            all_legends = legends_ref.get()
            
            target_last_comment = "..."  # Default
            
            if all_legends:
                for legend_key, legend_data in all_legends.items():
                    if legend_data.get('legend_id') == target_id:
                        target_last_comment = legend_data.get('first_post', '...')
                        break
            
            # Check for recent comments
            comments_ref = firebase_db.reference('/comments')
            all_comments = comments_ref.get()
            
            if all_comments:
                # Get most recent comment from target
                for comment in reversed(list(all_comments.values())):
                    if comment.get('legend_id') == target_id:
                        target_last_comment = comment.get('comment_text', target_last_comment)
                        break
            
            # Generate comment
            comment_text = generate_legend_comment(
                speaker_id=speaker_id,
                loop_time_minutes=loop_time,
                loop_number=self.loop_number,
                target_speaker_id=target_id,
                target_comment=target_last_comment
            )
            
            # Save to Firebase
            self.comment_counter += 1
            comments_ref.push({
                'comment_id': self.comment_counter,
                'legend_id': speaker_id,
                'agent_name': LEGENDS[speaker_id]['agent_name'],
                'target_legend_id': target_id,
                'comment_text': comment_text,
                'loop_time_minutes': loop_time,
                'loop_number': self.loop_number,
                'created_at': datetime.now().isoformat()
            })
            
            # Update stats
            stats_ref = firebase_db.reference('/stats')
            stats_ref.update({'total_comments': self.comment_counter})
            
            print(f"💬 [{loop_time}min] {LEGENDS[speaker_id]['human_name']} → {LEGENDS[target_id]['human_name']}: {comment_text[:80]}...")
            
        except Exception as e:
            print(f"⚠ Error generating interaction: {e}")
    
    def check_loop_end(self):
        """Check if loop should restart"""
        if not self.loop_start_time:
            return False
            
        elapsed_minutes = (datetime.now() - self.loop_start_time).total_seconds() / 60
        
        if elapsed_minutes >= self.loop_duration_minutes:
            print(f"\n⏰ Loop #{self.loop_number} complete after {int(elapsed_minutes)} minutes")
            self.loop_number += 1
            return True
        
        return False
    
    def run(self):
        """Main loop"""
        print("=" * 60)
        print("🎭 TERRARIUM: LEGENDS NIGHT OUT")
        print("Bob Dylan • Jimi Hendrix • Chuck Norris")
        print("Greenwich Village, NYC - 1969")
        print("=" * 60)
        
        # Start first loop
        self.start_new_loop()
        
        print(f"\n🌙 Night begins...")
        print(f"   Loop duration: {self.loop_duration_minutes} minutes (~{self.loop_duration_minutes//60} hours simulated)")
        print(f"   Interactions every 45 seconds")
        print(f"   Press Ctrl+C to stop\n")
        
        while True:
            try:
                # Check if loop should end
                if self.check_loop_end():
                    time.sleep(5)
                    self.start_new_loop()
                
                # Generate interaction
                self.generate_interaction()
                
                # Wait before next interaction
                time.sleep(45)
                
            except KeyboardInterrupt:
                print("\n\n🌅 Night ends. The legends part ways.\n")
                break
            except Exception as e:
                print(f"⚠ Error in main loop: {e}")
                time.sleep(10)


if __name__ == "__main__":
    engine = LegendsEngine()
    engine.run()
