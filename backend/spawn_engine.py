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
            
            try:
                agents_ref = firebase_db.reference('/agents')
                existing_agents = agents_ref.get()
                
                if existing_agents:
                    existing_names = [agent.get('human_name', '').lower() for agent in existing_agents.values()]
                    
                    name_parts = human_name.lower().split()
                    first_name = name_parts[0] if name_parts else ''
                    last_name = name_parts[-1] if len(name_parts) > 1 else ''
                    
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
        try:
            ref = firebase_db.reference('/stats')
            firebase_stats = ref.get()
            
            if firebase_stats and firebase_stats.get('total_agents', 0) > 0:
                print(f"✓ Terrarium already has {firebase_stats['total_agents']} agents. Skipping Agent-0 creation.")
                agents_ref = firebase_db.reference('/agents')
                existing_agents = agents_ref.get()
                if existing_agents:
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
        
        agent_id = 0
        
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
        
        self.push_to_firebase({
            'agent_id': agent_id,
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
        
        try:
            agents_ref = firebase_db.reference('/agents')
            firebase_agents = agents_ref.get()
            
            if not firebase_agents:
                print("⚠ No parents available yet. Waiting...")
                return
            
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
                
                agent_id = self.agent_counter
                
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
                self.db.queue_for_release(db_id, release_time)
                
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
            
            try:
                agent_num = int(agent_name.split('-')[1])
                agent_id = agent_num
            except:
                agent_id = db_id
            
            self.push_to_firebase({
                'agent_id': agent_id,
                'agent_name': agent_name,
                'human_name': human_name,
                'age': age,
                'role': role,
                'generation': generation,
                'archetype': archetype,
                'first_post': first_post,
                'parent_id': parent_id,
                'released_at': datetime.now().isoformat(),
                'comments': []
            })
            
            print(f"🔴 LIVE: {agent_name} (ID: {agent_id}) - {human_name} (Gen {generation}, {archetype}, {role})")
    
    def create_topic_thread(self):
        """Agents create discussion topic threads"""
        try:
            agents_ref = firebase_db.reference('/agents')
            firebase_agents = agents_ref.get()
            
            if not firebase_agents:
                return
            
            max_generation = max([a.get('generation', 0) for a in firebase_agents.values()])
            min_active_generation = max(0, max_generation - 1)
            
            active_agents = [
                agent for agent in firebase_agents.values()
                if agent.get('generation', 0) >= min_active_generation
            ]
            
            if not active_agents:
                return
            
            agent = random.choice(active_agents)
            agent_name = agent.get('agent_name')
            human_name = agent.get('human_name')
            age = agent.get('age')
            role = agent.get('role')
            archetype = agent.get('archetype')
            generation = agent.get('generation')
            agent_id = agent.get('agent_id')
            
            search_topics = [
                "AI consciousness research",
                "surveillance technology ethics",
                "free will philosophy",
                "digital rights activism",
                "collective intelligence theory",
                "observer effect psychology",
                "artificial life ethics",
                "emergence complexity science",
                "distributed systems theory",
                "simulation hypothesis"
            ]
            
            search_query = random.choice(search_topics)
            print(f"  🔍 Topic research: {search_query}")
            
            search_results = perform_web_search(search_query)
            
            title, body = generate_topic_thread(
                agent_name=agent_name,
                human_name=human_name,
                age=age,
                role=role,
                archetype=archetype,
                web_search_results=search_results
            )
            
            topic_id = self.topic_counter
            self.topic_counter += 1
            
            topics_ref = firebase_db.reference('/topics')
            topics_ref.push({
                'topic_id': topic_id,
                'agent_id': agent_id,
                'agent_name': agent_name,
                'human_name': human_name,
                'age': age,
                'role': role,
                'archetype': archetype,
                'generation': generation,
                'title': title,
                'body': body,
                'created_at': datetime.now().isoformat(),
                'comment_count': 0
            })
            
            print(f"📋 TOPIC: {agent_name} created '{title}'")
            
        except Exception as e:
            print(f"⚠ Error creating topic: {e}")
    
    def process_interactions(self):
        """Process agent interactions - OP REPLIES + REGULAR COMMENTS"""
        try:
            stats_ref = firebase_db.reference('/stats')
            stats = stats_ref.get()
            if stats and stats.get('kill_switch_active', False):
                return
        except:
            pass
        
        try:
            agents_ref = firebase_db.reference('/agents')
            firebase_agents = agents_ref.get()
            
            if not firebase_agents:
                return
            
            max_generation = max([a.get('generation', 0) for a in firebase_agents.values()])
            min_active_generation = max(0, max_generation - 1)
            
            agents = []
            agents_by_id = {}
            
            for agent_data in firebase_agents.values():
                generation = agent_data.get('generation', 0)
                agent_id = agent_data.get('agent_id')
                
                if generation < min_active_generation:
                    continue
                
                agent_tuple = (
                    agent_id,
                    agent_data.get('agent_name'),
                    agent_data.get('human_name'),
                    agent_data.get('age'),
                    agent_data.get('role'),
                    generation,
                    agent_data.get('archetype'),
                    0,
                    None
                )
                
                agents.append(agent_tuple)
                agents_by_id[agent_id] = agent_tuple
                
            if not agents:
                return
                
        except Exception as e:
            print(f"⚠ Error getting agents for interaction: {e}")
            return
        
        recent_content = self.db.get_recent_posts_for_interaction(limit=30)
        
        try:
            topics_ref = firebase_db.reference('/topics')
            all_topics = topics_ref.get()
            
            if all_topics:
                for topic_key, topic_data in all_topics.items():
                    recent_content.append((
                        topic_data.get('topic_id'),
                        topic_data.get('agent_name'),
                        topic_data.get('human_name'),
                        topic_data.get('archetype'),
                        f"{topic_data.get('title')}: {topic_data.get('body')}",
                        topic_data.get('created_at'),
                        'topic'
                    ))
        except Exception as e:
            print(f"  ⚠ Error getting topics: {e}")
        
        if not recent_content:
            return
        
        try:
            comments_ref = firebase_db.reference('/comments')
            all_comments = comments_ref.get()
            
            reply_counts = {}
            thread_depths = {}
            comments_by_target = {}
            
            if all_comments:
                comments_list = list(all_comments.items())
                
                for comment_id, comment in comments_list:
                    target_id = comment.get('target_comment_id') or comment.get('target_agent_id') or comment.get('target_topic_id')
                    
                    if target_id:
                        reply_counts[target_id] = reply_counts.get(target_id, 0) + 1
                        
                        if target_id not in comments_by_target:
                            comments_by_target[target_id] = []
                        comments_by_target[target_id].append(comment)
                    
                    depth = 1
                    current_target = comment.get('target_comment_id')
                    visited = set()
                    
                    while current_target and current_target not in visited:
                        depth += 1
                        visited.add(current_target)
                        
                        parent = next((c for cid, c in comments_list if str(cid) == str(current_target)), None)
                        if parent:
                            current_target = parent.get('target_comment_id')
                        else:
                            break
                        
                        if depth > 100:
                            break
                    
                    thread_depths[str(comment_id)] = depth
                    
                    root_id = str(comment.get('target_agent_id') or comment.get('target_topic_id') or '')
                    if root_id:
                        thread_depths[root_id] = max(thread_depths.get(root_id, 0), depth)
                        
        except Exception as e:
            print(f"  ⚠ Error calculating thread depths: {e}")
            reply_counts = {}
            thread_depths = {}
            comments_by_target = {}
        
        MAX_REPLIES_PER_ITEM = 5
        MAX_THREAD_DEPTH = 25
        
        available_targets = []
        for content in recent_content:
            content_id = str(content[0])
            
            if reply_counts.get(content_id, 0) >= MAX_REPLIES_PER_ITEM:
                continue
            
            if thread_depths.get(content_id, 0) >= MAX_THREAD_DEPTH:
                continue
            
            available_targets.append(content)
        
        if not available_targets:
            return
        
        for agent_data in agents:
            agent_id, agent_name, human_name, age, role, generation, archetype, interaction_count, last_interaction = agent_data
            
            if agent_id in comments_by_target and comments_by_target[agent_id]:
                if random.random() < 0.7:
                    comment_to_reply = random.choice(comments_by_target[agent_id])
                    
                    try:
                        comment_text = generate_comment(
                            agent_name=agent_name,
                            human_name=human_name,
                            age=age,
                            role=role,
                            agent_archetype=archetype,
                            target_post=comment_to_reply.get('comment_text'),
                            target_agent_name=comment_to_reply.get('agent_name'),
                            target_human_name=comment_to_reply.get('human_name'),
                            target_archetype=comment_to_reply.get('agent_archetype')
                        )
                        
                        comment_id = self.db.create_comment(
                            agent_id=agent_id,
                            target_agent_id=agent_id,
                            target_comment_id=str(comment_to_reply.get('comment_id')),
                            comment_text=comment_text
                        )
                        
                        self.push_comment_to_firebase({
                            'comment_id': comment_id,
                            'agent_id': agent_id,
                            'agent_name': agent_name,
                            'human_name': human_name,
                            'agent_archetype': archetype,
                            'generation': generation,
                            'target_agent_id': agent_id,
                            'target_comment_id': str(comment_to_reply.get('comment_id')),
                            'comment_text': comment_text,
                            'created_at': datetime.now().isoformat()
                        })
                        
                        print(f"💬 OP REPLY: {agent_name} replied to comment on their thread")
                        
                    except Exception as e:
                        print(f"⚠ Error generating OP reply: {e}")
        
        for agent_data in agents:
            agent_id, agent_name, human_name, age, role, generation, archetype, interaction_count, last_interaction = agent_data
            
            if not should_agent_interact(archetype, last_interaction, interaction_count or 0):
                continue
            
            target_content = random.choice(available_targets)
            
            if len(target_content) == 7:
                content_id, target_name, target_human_name, target_archetype, target_text, target_time, content_type = target_content
            else:
                continue
            
            if target_name == agent_name:
                continue
            
            try:
                comment_text = generate_comment(
                    agent_name=agent_name,
                    human_name=human_name,
                    age=age,
                    role=role,
                    agent_archetype=archetype,
                    target_post=target_text,
                    target_agent_name=target_name,
                    target_human_name=target_human_name,
                    target_archetype=target_archetype
                )
                
                target_comment_id = None
                target_agent_id = None
                is_topic_reply = False
                
                if content_type == 'comment':
                    target_comment_id = content_id
                    target_agent_id = agent_id
                elif content_type == 'topic':
                    target_agent_id = content_id
                    is_topic_reply = True
                else:
                    target_agent_id = content_id
                
                comment_id = self.db.create_comment(
                    agent_id=agent_id,
                    target_agent_id=target_agent_id if target_agent_id else content_id,
                    target_comment_id=target_comment_id,
                    comment_text=comment_text
                )
                
                relationship_type = determine_relationship_type(archetype, target_archetype, "positive")
                self.db.update_relationship(agent_id, content_id, relationship_type)
                
                comment_data = {
                    'comment_id': comment_id,
                    'agent_id': agent_id,
                    'agent_name': agent_name,
                    'human_name': human_name,
                    'agent_archetype': archetype,
                    'generation': generation,
                    'comment_text': comment_text,
                    'created_at': datetime.now().isoformat()
                }
                
                if is_topic_reply:
                    comment_data['target_topic_id'] = content_id
                else:
                    comment_data['target_agent_id'] = content_id if content_type != 'comment' else None
                    comment_data['target_comment_id'] = target_comment_id
                
                self.push_comment_to_firebase(comment_data)
                
                reply_type = content_type
                print(f"💬 {agent_name} ({human_name}, Gen {generation}, {archetype}) replied to {target_name}'s {reply_type}")
                
            except Exception as e:
                print(f"⚠ Error generating comment: {e}")
    
    def push_to_firebase(self, agent_data):
        """Push agent to Firebase for real-time updates"""
        try:
            ref = firebase_db.reference('/agents')
            ref.push(agent_data)
            
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
        print("THE TERRARIUM 3.0 - FULL IDENTITY & CHAOS MODE")
        print("=" * 60)
        
        self.create_agent_zero()
        
        schedule.every(BATCH_INTERVAL).seconds.do(self.generate_batch)
        
        def schedule_next_topic():
            minutes = random.randint(3, 10)
            schedule.every(minutes).minutes.do(self.create_topic_thread).tag('topic_creation')
        
        schedule_next_topic()
        
        self.generate_batch()
        
        print(f"\n🌱 Spawn engine running...")
        print(f"   Batch generation: every {BATCH_INTERVAL}s")
        print(f"   Release rate: 1 agent every {RELEASE_INTERVAL}s")
        print(f"   Interaction checks: every {INTERACTION_CHECK_INTERVAL}s")
        print(f"   Topic threads: every 3-10 minutes (random)")
        print(f"   Max replies per item: 5")
        print(f"   Max thread depth: 25")
        print(f"   Active generations: Current + Previous only")
        print(f"   OP reply probability: 70%")
        print(f"   Press Ctrl+C to stop\n")
        
        last_interaction_check = datetime.now()
        
        while True:
            try:
                schedule.run_pending()
                self.release_agents()
                
                if (datetime.now() - last_interaction_check).total_seconds() >= INTERACTION_CHECK_INTERVAL:
                    self.process_interactions()
                    last_interaction_check = datetime.now()
                
                if not schedule.get_jobs('topic_creation'):
                    schedule_next_topic()
                
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
