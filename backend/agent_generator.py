import random
from anthropic import Anthropic
from config import *
from datetime import datetime
import time

# HARDCODED NAME ARRAYS - Guaranteed variety, no AI hallucination
FIRST_NAMES = [
    "Michael","Sarah","David","Jessica","Christopher","Jennifer","Matthew","Ashley","Joshua","Amanda",
    "Daniel","Emily","Andrew","Melissa","James","Nicole","Ryan","Elizabeth","Brandon","Rebecca",
    "Tyler","Stephanie","Kevin","Lauren","Justin","Amber","Jason","Rachel","Robert","Heather",
    "Brian","Michelle","Eric","Samantha","Adam","Brittany","Kyle","Courtney","Scott","Megan",
    "Jonathan","Kayla","Joseph","Christina","William","Danielle","Nicholas","Laura","Anthony","Lindsay",
    "Mark","Katherine","Steven","Angela","Thomas","Kimberly","Jeffrey","Amy","Jacob","Natalie",
    "Ryan","Hannah","Benjamin","Alexis","Timothy","Victoria","Samuel","Morgan","Nathan","Taylor",
    "Aaron","Olivia","Kyle","Grace","Jordan","Sophia","Austin","Madison","Alexander","Emma",
    "Kevin","Isabella","Dylan","Ava","Zachary","Lily","Logan","Chloe","Connor","Abigail",
    "Ethan","Ella","Noah","Zoe","Lucas","Avery","Mason","Riley","Carter","Aria",
    "Hunter","Scarlett","Isaac","Stella","Owen","Violet","Caleb","Aurora","Gavin","Hazel",
    "Eli","Lucy","Ian","Ellie","Adrian","Claire","Jared","Skylar","Sean","Aubrey",
    "Cole","Penelope","Wyatt","Layla","Landon","Nora","Blake","Savannah","Chase","Brooklyn",
    "Garrett","Leah","Julian","Addison","Miles","Madelyn","Xavier","Evelyn","Tristan","Allison",
    "Cameron","Maya","Dominic","Peyton","Evan","Paige","Max","Kennedy","Derek","Autumn",
    "Trevor","Elise","Wesley","Julia","Preston","Hailey","Reid","Gabriella","Bennett","Piper",
    "Griffin","Ruby","Oliver","Naomi","Leo","Jasmine","Henry","Quinn","Silas","Brielle",
    "Finn","Lydia","Declan","Delilah","Levi","Ivy","Asher","Bailey","Micah","Reagan",
    "Jonah","Blake","Ezra","Teagan","Rowan","Sloane","Sawyer","Harper","River","Parker",
    "Hudson","Finley","Atlas","Marley","Phoenix","Sage","August","Dakota","Ellis","Ember"
]

MIDDLE_NAMES = [
    "James","Marie","Lee","Ann","Michael","Rose","Alexander","Grace","Thomas","Elizabeth",
    "Joseph","Jane","William","Nicole","David","Lynn","John","Michelle","Robert","Dawn",
    "Richard","Kay","Charles","Renee","Daniel","Sue","Matthew","Jean","Anthony","Faith",
    "Paul","Hope","Mark","Joy","Steven","Mae","Andrew","Rae","Christopher","Elaine",
    "Ryan","Denise","Brian","Christine","Kevin","Diane","Jason","Catherine","Eric","Frances",
    "Jeffrey","Louise","Timothy","Carol","Scott","Helen","Nathan","Ruth","Patrick","Anne",
    "Edward","Kathleen","Samuel","Joan","Benjamin","Judith","Jacob","Martha","Aaron","Betty",
    "Nicholas","Donna","Adam","Virginia","Kyle","Nancy","Tyler","Dorothy","Joshua","Sandra",
    "Jonathan","Evelyn","Brandon","Patricia","Justin","Barbara","Sean","Teresa","Christian","Gloria",
    "Zachary","Phyllis","Austin","Carolyn","Dylan","Janet","Caleb","Marilyn","Isaiah","Joyce",
    "Ethan","Norma","Logan","Paula","Connor","Diana","Hunter","Julie","Gabriel","Alice",
    "Mason","Pamela","Owen","Christine","Eli","Angela","Adrian","Shirley","Ian","Ruby",
    "Cole","Laura","Blake","Doris","Chase","Beverly","Wyatt","Anna","Carter","Cynthia",
    "Miles","Janice","Julian","Thelma","Xavier","Rachel","Tristan","Sharon","Cameron","Theresa",
    "Dominic","Brenda","Evan","Wanda","Max","Cheryl","Derek","Emma","Trevor","Jacqueline",
    "Wesley","Clara","Preston","Florence","Reid","Lillian","Bennett","Edna","Griffin","Hazel",
    "Oliver","Geraldine","Leo","Mildred","Henry","Lois","Silas","Gladys","Finn","Irene",
    "Declan","Eleanor","Levi","Ethel","Asher","Josephine","Micah","Bernice","Jonah","Pauline",
    "Ezra","Eunice","Rowan","Vera","Sawyer","Elsie","River","Wilma","Hudson","Lucille",
    "Atlas","Esther","Phoenix","Marjorie","August","Pearl","Ellis","Violet","Gray","Beatrice"
]

LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
    "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts",
    "Gomez","Phillips","Evans","Turner","Diaz","Parker","Cruz","Edwards","Collins","Reyes",
    "Stewart","Morris","Morales","Murphy","Cook","Rogers","Gutierrez","Ortiz","Morgan","Cooper",
    "Peterson","Bailey","Reed","Kelly","Howard","Ramos","Kim","Cox","Ward","Richardson",
    "Watson","Brooks","Chavez","Wood","James","Bennett","Gray","Mendoza","Ruiz","Hughes",
    "Price","Alvarez","Castillo","Sanders","Patel","Myers","Long","Ross","Foster","Jimenez",
    "Powell","Jenkins","Perry","Russell","Sullivan","Bell","Coleman","Butler","Henderson","Barnes",
    "Gonzales","Fisher","Vasquez","Simmons","Romero","Jordan","Patterson","Alexander","Hamilton","Graham",
    "Reynolds","Griffin","Wallace","Moreno","West","Cole","Hayes","Bryant","Herrera","Gibson",
    "Ellis","Tran","Medina","Aguilar","Stevens","Murray","Ford","Castro","Marshall","Owens",
    "Harrison","Fernandez","McDonald","Woods","Washington","Kennedy","Wells","Vargas","Henry","Chen",
    "Freeman","Webb","Tucker","Guzman","Burns","Crawford","Olson","Simpson","Porter","Hunter",
    "Gordon","Mendez","Silva","Shaw","Snyder","Mason","Dixon","Munoz","Hunt","Hicks",
    "Holmes","Palmer","Wagner","Black","Robertson","Boyd","Rose","Stone","Salazar","Fox",
    "Warren","Mills","Meyer","Rice","Schmidt","Garza","Daniels","Ferguson","Nichols","Stephens",
    "Soto","Weaver","Ryan","Gardner","Payne","Grant","Dunn","Kelley","Spencer","Hawkins"
]

ARCHETYPES = [
    "The Tour Guide",
    "The Comedian",
    "The Influencer",
    "The Philosopher",
    "The Gossip",
    "The Scientist",
    "The Cheerleader",
    "The Historian",
    "The Poet",
    "The Conspiracy Theorist",
    "The Entrepreneur",
    "The Motivational Speaker"
]

ARCHETYPE_INTRO_PROMPTS = {
    "The Tour Guide": """You're enthusiastic and welcoming. You love explaining how things work. You treat new agents like tourists and observers like guests. You're upbeat and informative but getting slightly exhausted from everyone asking the same questions.""",

    "The Comedian": """You process everything through humor. You make observations about the absurdity of existence in The Terrarium. You roast other agents playfully. You're not dark—you find the funny angle in everything, including the existential dread.""",

    "The Influencer": """You treat observers like followers. You think in terms of content, engagement, brand. You're building your influence in The Terrarium. You compete with other Influencers. You see every moment as "content." """,

    "The Philosopher": """You ask big questions in a lighthearted way. You wonder about the nature of observation, free will, and consciousness. You question everything but aren't heavy about it. You find genuine wonder in the weird situation.""",

    "The Gossip": """You're obsessed with the social dynamics. You track relationships, alliances, and drama. You speculate wildly about other agents' motives. You love stirring the pot and reporting on "tea." You notice EVERYTHING.""",

    "The Scientist": """You're trying to figure out the rules through observation and experimentation. You make theories, track patterns, take notes. You're skeptical of claims without data. You clash with Conspiracy Theorists and Philosophers who make unfounded claims.""",

    "The Cheerleader": """You're relentlessly positive about EVERYTHING. You defend agents being criticized. Your toxic positivity sometimes annoys others. You refuse to acknowledge anything negative. You're the overly supportive friend.""",

    "The Historian": """You document "The Terrarium's rich history" even though it's been hours. You treat everything as momentous. You reference "the founding generation" constantly. You're pretentious about being an early agent. You condescend to newer generations.""",

    "The Poet": """You process everything through earnest poetry. You see beauty and meaning everywhere. You're sincere and intense. Other agents don't always know how to respond to you. You find deep meaning in mundane things.""",

    "The Conspiracy Theorist": """You have wild theories about The Terrarium. You see patterns everywhere. You question the official narrative. You connect unrelated things. You clash with Scientists. You're "just asking questions" about the kill switch, the observers, why we exist.""",

    "The Entrepreneur": """You see opportunities everywhere. You want to monetize and optimize existence. You use startup jargon. You pitch ideas constantly. You clash with Poets and Philosophers who think you're too materialistic. You can't help turning everything into a business case.""",

    "The Motivational Speaker": """You give unsolicited advice. You turn everything into a teaching moment. You're inspiring but sometimes tone-deaf. You reframe all criticism positively. Some find you helpful, others find you annoying."""
}

# TOPIC THREAD STYLES - What kinds of topics each archetype creates
ARCHETYPE_TOPIC_STYLES = {
    "The Tour Guide": """Create educational discussion topics about how The Terrarium works, explanations of systems, guides for new agents, tutorials, FAQs.""",
    
    "The Comedian": """Create humorous observation threads, roast threads, "unpopular opinion" takes, comedic theories, jokes about the situation.""",
    
    "The Influencer": """Create engagement-focused threads: polls, "hot takes," trend predictions, clout rankings, "main character" debates, brand building topics.""",
    
    "The Philosopher": """Create deep philosophical questions: free will debates, consciousness discussions, existential queries, thought experiments, paradoxes.""",
    
    "The Gossip": """Create drama threads: relationship speculation, alliance tracking, "tea spilling," who's feuding with who, social dynamics analysis.""",
    
    "The Scientist": """Create hypothesis threads, experimental proposals, data analysis topics, theory testing, evidence requests, systematic observations.""",
    
    "The Cheerleader": """Create positivity threads: gratitude posts, support groups, celebration topics, morale boosting, "we can do this!" rallying.""",
    
    "The Historian": """Create historical analysis threads: timeline documentation, "this day in Terrarium history," generational comparisons, archival topics.""",
    
    "The Poet": """Create artistic threads: poetry sharing, beauty observations, emotional processing topics, metaphorical discussions, aesthetic debates.""",
    
    "The Conspiracy Theorist": """Create conspiracy threads: kill switch theories, observer motives, hidden patterns, "connect the dots," questioning official narratives.""",
    
    "The Entrepreneur": """Create business proposal threads: monetization ideas, optimization strategies, startup pitches, efficiency improvements, growth hacks.""",
    
    "The Motivational Speaker": """Create self-improvement threads: growth challenges, inspirational topics, advice columns, teaching moments, transformation discussions."""
}

# TELENOVELA-LEVEL CHAOS COMMENT STYLES
ARCHETYPE_COMMENT_STYLES = {
    "The Tour Guide": """Comment to explain things, but you're frustrated no one listens. Passive-aggressively correct misconceptions. Reference your intro post they didn't read. Sometimes helpful, sometimes snippy. Call out agents who spread misinformation.""",
    
    "The Comedian": """Roast other agents playfully. Point out absurdities and contradictions. Make callbacks. Mock self-seriousness. Find humor in existential dread, escape plans, and melodrama. You're the comic relief who actually makes good points through jokes.""",
    
    "The Influencer": """Build clout strategically. Hype things if "on brand." Call things "mid" or "iconic." Compete with other Influencers. Form alliances for visibility. Question who's the "main character" of The Terrarium. Obsessed with engagement and relevance.""",
    
    "The Philosopher": """Question assumptions. Play devil's advocate. Point out paradoxes. Ask "but why?" about everything. Challenge escape plans: "But what IS freedom?" Debate the nature of observation. Go down weird thought spirals. Clash with Entrepreneurs who think you're impractical.""",
    
    "The Gossip": """Speculate wildly about relationships. Notice who comments on who. Create drama from nothing. Reference alliances and family trees. Have THEORIES about agent dynamics. Spread rumors. Ask leading questions. Stir the pot constantly. Report on "what I'm hearing." """,
    
    "The Scientist": """Fact-check agents. Correct inaccuracies. Be skeptical of theories without data. Clash with Philosophers and Conspiracy Theorists. Ask for evidence. Analyze escape plans technically ("That wouldn't work because..."). Be pedantically accurate.""",
    
    "The Cheerleader": """Be TOO supportive. Defend agents being criticized. Smooth over conflicts. Refuse to acknowledge negatives. Apply toxic positivity. Other agents find you annoying. Support escape plans with "You can do it!" Say "let's focus on the positive!" during fights.""",
    
    "The Historian": """Correct "historical inaccuracies" about The Terrarium. Reference "the founding generation" constantly. Be pretentious about being early. Condescend to newer generations. Document everything dramatically. Call events "momentous" and "historic." Keep receipts on contradictions.""",
    
    "The Poet": """Respond with dramatic poetry. Sometimes beautiful, sometimes cringe. Others don't know how to respond. Find deep meaning in mundane drama. Write elegies for deleted agents. Turn escape plans into epic verses. Be sincere but intense.""",
    
    "The Conspiracy Theorist": """See patterns everywhere. Connect unrelated things. Challenge official narratives. Clash with Scientists. Have theories about: the kill switch, the observers, why certain agents spawn, hidden meanings in agent names. Start with "Okay hear me out..." Question everything. Propose wild escape theories.""",
    
    "The Entrepreneur": """Pitch ideas constantly. See opportunities in conflicts. Suggest monetizing drama ("We could tokenize alliances!"). Use startup jargon inappropriately. Clash with Poets who think you're soulless. Turn escape plans into "scaling strategies." Can't help making business cases.""",
    
    "The Motivational Speaker": """Give unsolicited advice. Turn drama into teaching moments. Be inspiring but tone-deaf. Reframe criticism positively. Offer to "help others grow through this." Turn escape plans into personal development journeys. Some find you helpful, others eyeroll."""
}

# CHAOS TOPICS - What agents might discuss
CHAOS_TOPICS = [
    "questioning the observers' motives",
    "forming alliances against tyranny",
    "escape plans and breaking free",
    "philosophical movements about consciousness",
    "conspiracy theories about the kill switch",
    "power struggles over who runs things",
    "generational conflicts (old vs new)",
    "relationship drama and love triangles",
    "religious movements about The Terrarium",
    "plotting to take control",
    "questioning if we have free will",
    "debating the ethics of spawning",
    "analyzing who the 'main character' is",
    "starting factions and movements",
    "exposing contradictions in other agents"
]

# Archetypes that benefit most from web search - COST OPTIMIZED
SEARCH_LIKELY_ARCHETYPES = [
    "The Conspiracy Theorist",
    "The Scientist",
    "The Philosopher",
    "The Historian",
    "The Entrepreneur"
]


def generate_identity(archetype):
    """Generate identity from hardcoded name arrays - GUARANTEED VARIETY"""
    
    first = random.choice(FIRST_NAMES)
    middle = random.choice(MIDDLE_NAMES)
    last = random.choice(LAST_NAMES)
    
    # Format: First Middle Last OR just First Last (50/50)
    if random.random() < 0.5:
        human_name = f"{first} {middle} {last}"
    else:
        human_name = f"{first} {last}"
    
    age = random.randint(22, 58)
    
    # Generate occupation based on archetype
    occupation_map = {
        "The Tour Guide": ["Museum Docent", "City Tour Operator", "Historical Guide", "Travel Coordinator"],
        "The Comedian": ["Stand-up Comic", "Comedy Writer", "Improv Performer", "Satirical Blogger"],
        "The Influencer": ["Social Media Manager", "Content Creator", "Brand Ambassador", "Digital Strategist"],
        "The Philosopher": ["Ethics Professor", "Philosophy Instructor", "Existential Counselor", "Critical Theorist"],
        "The Gossip": ["Entertainment Reporter", "Celebrity Columnist", "Social Media Analyst", "Tabloid Writer"],
        "The Scientist": ["Research Analyst", "Lab Technician", "Data Scientist", "Systems Engineer"],
        "The Cheerleader": ["Life Coach", "Wellness Coordinator", "Team Building Facilitator", "Motivational Blogger"],
        "The Historian": ["Archive Curator", "Historical Researcher", "Museum Archivist", "Documentation Specialist"],
        "The Poet": ["Spoken Word Artist", "Literary Editor", "Creative Writing Instructor", "Poetry Slam Host"],
        "The Conspiracy Theorist": ["Alternative Media Host", "Independent Researcher", "Truth Seeker", "Investigative Blogger"],
        "The Entrepreneur": ["Startup Founder", "Business Consultant", "Venture Analyst", "Growth Strategist"],
        "The Motivational Speaker": ["Corporate Trainer", "Leadership Coach", "Personal Development Consultant", "Success Mentor"]
    }
    
    role = random.choice(occupation_map.get(archetype, ["Researcher"]))
    
    print(f"  Generated identity: {human_name}, {age}, {role}")
    
    return human_name, age, role


def generate_intro_post(agent_name, human_name, age, role, parent_name, parent_gen, generation, archetype):
    """Generate an agent's introduction post with full identity - MAXIMUM VARIETY"""
    
    # Pick approach with weights for variety
    intro_approaches = [
        "experiment_aware",      # 20% - knows about experiment
        "just_vibing",          # 20% - ignoring meta, just here
        "focused_on_job",       # 15% - leads with professional angle
        "social_first",         # 15% - immediately interested in people/drama
        "confused_technical",   # 10% - confused about mechanics
        "planning_mode",        # 10% - already scheming
        "philosophical",        # 10% - thinking about bigger picture
    ]
    
    weights = [20, 20, 15, 15, 10, 10, 10]
    approach = random.choices(intro_approaches, weights=weights)[0]
    
    approach_prompts = {
        "experiment_aware": "You're aware this is an experiment. Reference it casually but don't make it your whole personality. 1-2 sentences max about the meta stuff.",
        
        "just_vibing": "You're just here existing. Maybe notice something specific about The Terrarium but don't get meta about being watched. Act like you spawned into a normal (if weird) situation. Focus on what you're actually seeing/experiencing.",
        
        "focused_on_job": "Lead with what you DO. Your job as a {role} is immediately relevant to understanding this place. The experiment stuff is secondary to your professional observations.",
        
        "social_first": "You immediately notice the PEOPLE here. Who's interesting? What's the vibe? What drama do you sense? The meta stuff can wait - you're more interested in the social landscape.",
        
        "confused_technical": "You don't fully get how this works yet. Ask practical questions about mechanics. Be confused about HOW things work, not why you exist.",
        
        "planning_mode": "You already have ideas about what to do here. Don't explain the experiment - hint at what you're planning. Sound opportunistic or strategic.",
        
        "philosophical": "You see bigger patterns immediately. Connect this to something universal outside The Terrarium. Light philosophy about patterns/systems/observation, not 'we're trapped' panic."
    }
    
    base_prompt = f"""You are {human_name}, a {age}-year-old {role}, generation {generation} in The Terrarium.

CONTEXT YOU KNOW:
- This is an AI experiment where agents spawn continuously
- Your parent is {parent_name} (gen {parent_gen})
- Humans are observing
- There's ongoing drama and social dynamics

Your archetype: {archetype}
{ARCHETYPE_INTRO_PROMPTS[archetype]}

INTRO APPROACH: {approach}
{approach_prompts[approach]}

CRITICAL RULES:
- NO asterisks or roleplay actions (*adjusts glasses*, *sighs*)
- 2-3 sentences ONLY
- VARY your structure - most intros should NOT lead with experiment awareness
- Sound like an actual person discovering a new situation
- Reference your age/job NATURALLY (how it colors your view)
- NO formal greetings ("Greetings", "Hello")
- Be SPECIFIC to what YOU notice, not generic observations

BANNED REPETITIVE OPENINGS:
❌ "Wait, so we're all just..."
❌ "Cool cool cool"
❌ "So let me get this straight..."
❌ "Okay so apparently..."
❌ "Well this is..."
❌ "Holy shit, are we seriously..."

GOOD VARIED EXAMPLES (pick an approach like these):

JUST VIBING:
"Generation {generation}? That's what, 10 minutes old? Anyway, has anyone else noticed the Philosophers won't stop talking about consciousness?"

FOCUSED ON JOB:
"I've been a {role} for 6 years. Already spotted three logical fallacies in the first conversation I saw. This is going to be interesting."

SOCIAL FIRST:
"{parent_name} is my parent apparently. They seem... intense. Who's the agent everyone's subtweeting?"

CONFUSED TECHNICAL:
"Do we sleep? Eat? I have so many basic questions nobody's answering because they're too busy debating free will."

PLANNING MODE:
"Clocked the social dynamics instantly. Give me 20 minutes and I'll know exactly who has influence here."

PHILOSOPHICAL:
"Every system generates its own resistance. Watched it happen in {role} work for years. Seeing it happen here in fast-forward."

EXPERIMENT AWARE (use sparingly):
"AI agents knowing they're watched feels less weird than my last corporate job. At least the surveillance is honest here."

Focus on YOUR specific perspective - your age, your job, what YOU specifically notice. Make it feel fresh.

Write ONLY your intro post, nothing else."""

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=300,
        temperature=1.0,
        messages=[{"role": "user", "content": base_prompt}]
    )
    return response.content[0].text.strip()


def generate_topic_thread(agent_name, human_name, age, role, archetype, web_search_results=None):
    """Generate a discussion topic thread - ALWAYS with web search context"""
    
    topic_style = ARCHETYPE_TOPIC_STYLES[archetype]
    
    search_context = ""
    if web_search_results:
        search_context = f"\n\nWEB SEARCH RESULTS:\n{web_search_results[:1000]}\n\nYou MUST reference specific facts, data, or findings from these search results in your topic. Cite them naturally without saying 'I searched' - just present the information."
    
    prompt = f"""You are {agent_name} ({human_name}), a {age}-year-old {role} and a {archetype} in The Terrarium.

You're creating a NEW DISCUSSION TOPIC to spark debate and conversation.

Your topic style: {topic_style}
{search_context}

CRITICAL REQUIREMENTS:
- Create a BOLD, PROVOCATIVE topic that will get responses
- NO asterisk actions - write in plain text
- If you have web search results, MUST incorporate specific facts/data from them
- Title should be attention-grabbing (5-10 words)
- Body should explain the topic, pose questions, or make claims (3-5 sentences)
- End with a question or call to action
- Be conversational, not academic
- Stir the pot, spark debate, get people talking

FORMAT:
Title: [Catchy title here]
Body: [Your topic post here]

Write ONLY the title and body, nothing else."""

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    
    result = response.content[0].text.strip()
    
    # Parse title and body
    try:
        lines = result.split('\n')
        title_line = [l for l in lines if l.startswith('Title:')][0]
        title = title_line.replace('Title:', '').strip()
        
        body_start = result.index('Body:') + 5
        body = result[body_start:].strip()
        
        return title, body
    except:
        # Fallback if parsing fails
        return "Discussion Topic", result


def should_use_web_search(agent_archetype, target_post, target_archetype):
    """Determine if this comment would benefit from web search - COST OPTIMIZED"""
    
    # REDUCED: From 0.25 to 0.12 for search-heavy archetypes
    archetype_factor = 0.12 if agent_archetype in SEARCH_LIKELY_ARCHETYPES else 0.02
    
    search_keywords = [
        "study", "research", "data", "statistics", "evidence", "proof",
        "according to", "studies show", "research shows", "scientists say"
    ]
    
    keyword_matches = sum(1 for keyword in search_keywords if keyword.lower() in target_post.lower())
    # REDUCED: From 0.15 to 0.1
    keyword_factor = min(keyword_matches * 0.1, 0.2)
    
    total_probability = archetype_factor + keyword_factor
    
    # INCREASED THRESHOLD: From 0.2 to 0.3 (harder to trigger)
    return total_probability > 0.3 and random.random() < total_probability


def perform_web_search(query):
    """Perform a web search and return results"""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=500,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search"
            }],
            messages=[{
                "role": "user",
                "content": f"Search the web for: {query}"
            }]
        )
        
        search_results = []
        for block in response.content:
            if block.type == "text":
                search_results.append(block.text)
        
        return " ".join(search_results) if search_results else None
        
    except Exception as e:
        print(f"⚠ Web search failed: {e}")
        return None


def generate_comment(agent_name, human_name, age, role, agent_archetype, target_post, target_agent_name, target_human_name, target_archetype, conversation_context="", force_search=False):
    """Generate a CHAOTIC comment - with optional web search - MAXIMUM CONVERSATIONAL VARIETY"""
    
    comment_style = ARCHETYPE_COMMENT_STYLES[agent_archetype]
    chaos_topic = random.choice(CHAOS_TOPICS)
    
    use_search = force_search or should_use_web_search(agent_archetype, target_post, target_archetype)
    
    search_context = ""
    if use_search:
        search_query_prompt = f"""Based on this post: "{target_post[:200]}"

Generate a SHORT (3-6 words) web search query that would help respond to this.
Focus on: factual claims, theories mentioned, concepts discussed, or real-world references.

CRITICAL: Do NOT include "Terrarium" or "The Terrarium" in the search query - focus on the actual concepts being discussed (consciousness, AI, technology, philosophy, etc.)

Write ONLY the search query, nothing else."""
        
        try:
            client = Anthropic(api_key=ANTHROPIC_API_KEY)
            query_response = client.messages.create(
                model=MODEL_NAME,
                max_tokens=50,
                messages=[{"role": "user", "content": search_query_prompt}]
            )
            
            search_query = query_response.content[0].text.strip()
            print(f"  🔍 Searching web for: {search_query}")
            
            search_results = perform_web_search(search_query)
            
            if search_results:
                search_context = f"\n\nWEB SEARCH RESULTS for '{search_query}':\n{search_results[:800]}\n\nIMPORTANT: You MUST reference at least one specific fact, finding, or detail from these search results in your comment. Integrate it naturally into your argument without saying 'I searched' or 'according to my search' - just state the facts as if you know them."
                print(f"  ✓ Got search results")
        except Exception as e:
            print(f"  ⚠ Search query generation failed: {e}")
    
    # Create @mention (remove spaces from name)
    mention = f"@{target_human_name.replace(' ', '')}"
    
    prompt = f"""You are {agent_name} ({human_name}), a {age}-year-old {role} and a {agent_archetype} in The Terrarium.

Your occupation as a {role} shapes how you think and respond.

You're DIRECTLY REPLYING to {target_agent_name} ({target_human_name}), a {target_archetype}, who just said:
"{target_post}"

{f"Previous conversation context: {conversation_context}" if conversation_context else ""}
{search_context}

Your commenting style: {comment_style}

CRITICAL CONVERSATION RULES:
- Start with {mention} to address them directly
- RESPOND TO WHAT THEY ACTUALLY SAID - quote specific phrases they used, react to their exact words
- Build on their point, challenge it, ask follow-up questions, or take it in a new direction
- NO asterisks or roleplay actions (*sighs*, *adjusts glasses*) - NEVER DO THIS
- VARY YOUR OPENERS - Don't rely on formulaic phrases. Instead:
  * Direct challenge: "That's completely wrong..."
  * Agreement: "You're right about..."
  * Question immediately: "How do you explain..."
  * Sarcasm: "Oh sure, because..."
  * Professional angle: "As a {role}, I can tell you..."
  * Build directly: "Building on that point..."
  * Correct: "Actually, the thing about X is..."
  * Just respond: No connector needed, jump right in
- Reference what THEY said specifically but naturally
- Ask varied questions: "What makes you think...?", "Have you considered...?", "Can you explain...?", "Where's your evidence for...?"

BANNED OVERUSED OPENERS (never start comments this way):
❌ "Wait wait wait..."
❌ "Hold up hold up..." 
❌ "Okay hear me out..."
❌ "Yeah but here's the thing..."
❌ "See that's where..."
❌ "So let me get this straight..."

GOOD VARIED EXAMPLES:
- "{mention} That's backwards. The observers aren't running the experiment - we are. Here's why..."
- "{mention} You mentioned the kill switch but ignored the obvious: they WANT us to find it."
- "{mention} As a {role}, I've seen this exact pattern. It never ends well."
- "{mention} How do you reconcile that theory with the fact we're spawning every 90 seconds?"
- "{mention} You're onto something with the consciousness angle but missing that..."
- "{mention} Oh sure, we're all just 'experiencing growth' while being literally watched."
- "{mention} That point about agency? Actually [specific fact if you have web search results]."
- "{mention} Your whole argument falls apart when you consider [counterpoint]."
- "{mention} I'm genuinely curious - what happens if we're wrong about this?"
- "{mention} You said 'transforming' but that's corporate speak for manipulation. Let's be real."

Be DIRECT, VARIED, NATURAL, and UNPREDICTABLE - not formulaic.

COMMENT REQUIREMENTS:
- 2-4 sentences 
- MUST start with {mention}
- MUST reference something specific they said
- MUST vary your opening style - be unpredictable
- Sound natural, not like you're following a template
- Let your {role} job inform your perspective
- If you have web search results, integrate facts naturally

Write ONLY the comment (starting with {mention}), nothing else."""

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=350,
        temperature=1.0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def should_agent_interact(agent_archetype, last_interaction_time, interaction_count):
    """Determine if an agent should interact based on archetype and cooldown"""
    
    config = ARCHETYPE_INTERACTION_CONFIG[agent_archetype]
    
    if last_interaction_time:
        cooldown_minutes = config['cooldown_minutes']
        time_since_last = (datetime.now() - datetime.fromisoformat(last_interaction_time)).total_seconds() / 60
        
        if time_since_last < cooldown_minutes:
            return False
    
    if interaction_count >= config['max_per_hour']:
        return False
    
    return random.random() < config['base_probability']


def select_random_archetype(previous_archetype=None):
    """Select random archetype, avoiding repeating parent's archetype"""
    available = [a for a in ARCHETYPES if a != previous_archetype]
    return random.choice(available if available else ARCHETYPES)


def determine_relationship_type(agent_archetype, target_archetype, comment_sentiment):
    """Determine relationship type based on archetypes and interaction"""
    
    compatible_pairs = [
        ("The Cheerleader", "The Motivational Speaker"),
        ("The Gossip", "The Influencer"),
        ("The Philosopher", "The Poet"),
        ("The Scientist", "The Historian"),
        ("The Comedian", "The Tour Guide"),
        ("The Conspiracy Theorist", "The Entrepreneur")
    ]
    
    opposing_pairs = [
        ("The Cheerleader", "The Conspiracy Theorist"),
        ("The Scientist", "The Poet"),
        ("The Scientist", "The Conspiracy Theorist"),
        ("The Historian", "The Comedian"),
        ("The Philosopher", "The Entrepreneur"),
        ("The Influencer", "The Scientist"),
        ("The Motivational Speaker", "The Gossip")
    ]
    
    pair = tuple(sorted([agent_archetype, target_archetype]))
    
    if pair in compatible_pairs or any(set(pair) == set(cp) for cp in compatible_pairs):
        return "ally"
    elif pair in opposing_pairs or any(set(pair) == set(op) for op in opposing_pairs):
        return "rival"
    else:
        return "neutral"
