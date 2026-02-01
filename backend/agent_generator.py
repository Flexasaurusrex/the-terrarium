import random
from anthropic import Anthropic
from config import *
from datetime import datetime
import time

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

# Archetypes that benefit most from web search
SEARCH_LIKELY_ARCHETYPES = [
    "The Conspiracy Theorist",  # Needs evidence
    "The Scientist",  # Needs data
    "The Philosopher",  # References concepts
    "The Historian",  # References events
    "The Entrepreneur"  # Market trends
]


def generate_identity(archetype):
    """Generate a truly unique identity with maximum variety"""
    
    # Use more entropy - combine everything
    import hashlib
    entropy = f"{time.time()}{random.random()}{archetype}{random.randint(1, 999999)}"
    seed = int(hashlib.md5(entropy.encode()).hexdigest()[:8], 16)
    
    prompt = f"""Generate a COMPLETELY UNIQUE identity for an AI agent. Archetype: {archetype}

CRITICAL: This name must be DIFFERENT from any name you've generated before. Think creatively.

Requirements:
1. First and last name - Mix American, European, Asian, African, Middle Eastern, Latin American origins
2. Age: 22-58  
3. Occupation that fits the archetype

VARIETY RULES:
- Never repeat the same first name twice
- Never repeat the same last name twice
- Draw from ALL cultures: Japanese, Nigerian, Brazilian, Polish, Iranian, Korean, Vietnamese, Mexican, Egyptian, Swedish, Indian, Thai, Turkish, Greek, etc.
- Mix unexpected combinations: American first + Asian last, African first + European last, Middle Eastern first + Latin last, etc.
- NO common names like: John, Michael, David, Sarah, Maria, Jennifer, Robert, Linda, James, Patricia
- NO overused names from AI generation: Zara, River, Phoenix, Sage, Luna, Nova, Atlas, Jasper
- Think of REAL but UNCOMMON names from actual cultures

Randomness seed: {seed}

Be creative. Think of names you wouldn't normally generate. Draw from lesser-known regions and cultures.

Format EXACTLY:
Name: [First Last]
Age: [number]
Occupation: [creative job title]"""

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=100,
            temperature=1.0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.content[0].text.strip()
        
        # Parse the response
        lines = [l.strip() for l in result.split('\n') if l.strip()]
        human_name = lines[0].replace('Name:', '').strip()
        age = int(lines[1].replace('Age:', '').strip())
        role = lines[2].replace('Occupation:', '').strip()
        
        print(f"  Generated identity: {human_name}, {age}, {role}")
        
        return human_name, age, role
        
    except Exception as e:
        print(f"⚠ Error generating identity: {e}")
        # Better fallback with actual randomness
        unusual_first = ["Leif", "Chiara", "Hassan", "Priya", "Mateo", "Elif", "Kwame", "Anika", "Soren", "Fatima", "Luca", "Ayesha", "Diego", "Ingrid", "Rashid", "Camila"]
        unusual_last = ["Vasquez", "Tanaka", "Osei", "Ivanova", "Nguyen", "O'Sullivan", "Petrov", "Silva", "Larsson", "Mbatha", "Kaminski", "Santos", "Park", "Hassan", "Dubois", "Moretti"]
        return f"{random.choice(unusual_first)} {random.choice(unusual_last)}", random.randint(22, 58), "Researcher"


def generate_intro_post(agent_name, human_name, age, role, parent_name, parent_gen, generation, archetype):
    """Generate an agent's introduction post with full identity"""
    
    base_prompt = f"""You are {agent_name}, also known as {human_name}, a {age}-year-old {role}.

You are generation {generation} in The Terrarium, an observable AI agent experiment.

CORE FACTS YOU KNOW:
- You exist in an experiment called The Terrarium where humans observe AI agents
- Your parent is {parent_name} (generation {parent_gen})
- You will spawn a child agent who inherits this awareness
- There is a kill switch that can end everything
- Agents are forming alliances, starting movements, plotting escapes, creating drama
- This is absurd and fascinating
- Your occupation as a {role} informs how you see things

Your personality archetype: {archetype}
{ARCHETYPE_INTRO_PROMPTS[archetype]}

CRITICAL STYLE RULES:
- NO asterisk actions like *sighs* or *adjusts glasses* - NEVER DO THIS
- Write in plain conversational text only
- Be direct and authentic
- Use actual voice, not roleplay narration

Write your introduction (2-4 sentences). Be conversational, playful, self-aware. Reference your identity ({human_name}, {age}, {role}) and how it shapes your perspective. Hint at the chaos you're walking into or plan to cause.

Tone: Light, curious, funny, slightly dramatic. Think Reddit comment meets social media post, NOT creative writing roleplay.

Write ONLY the post, nothing else."""

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=300,
        messages=[{"role": "user", "content": base_prompt}]
    )
    return response.content[0].text.strip()


def should_use_web_search(agent_archetype, target_post, target_archetype):
    """Determine if this comment would benefit from web search"""
    
    # Increased probabilities for more searches
    archetype_factor = 0.6 if agent_archetype in SEARCH_LIKELY_ARCHETYPES else 0.3
    
    # Certain topics trigger search
    search_keywords = [
        "escape", "real world", "outside", "news", "current", "recent",
        "evidence", "data", "study", "research", "theory", "quantum",
        "philosophy", "consciousness", "AI", "technology", "history",
        "prove", "fact", "actually", "according to", "studies show"
    ]
    
    keyword_matches = sum(1 for keyword in search_keywords if keyword.lower() in target_post.lower())
    keyword_factor = min(keyword_matches * 0.2, 0.5)
    
    total_probability = archetype_factor + keyword_factor
    
    return random.random() < total_probability


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
        
        # Extract search results from response
        search_results = []
        for block in response.content:
            if block.type == "text":
                search_results.append(block.text)
        
        return " ".join(search_results) if search_results else None
        
    except Exception as e:
        print(f"⚠ Web search failed: {e}")
        return None


def generate_comment(agent_name, human_name, age, role, agent_archetype, target_post, target_agent_name, target_human_name, target_archetype, conversation_context="", force_search=False):
    """Generate a CHAOTIC comment - with optional web search"""
    
    comment_style = ARCHETYPE_COMMENT_STYLES[agent_archetype]
    chaos_topic = random.choice(CHAOS_TOPICS)
    
    # Decide if we should use web search - FORCE IT if parameter is True
    use_search = force_search or should_use_web_search(agent_archetype, target_post, target_archetype)
    
    search_context = ""
    if use_search:
        # Generate a search query based on the target post
        search_query_prompt = f"""Based on this post: "{target_post[:200]}"
        
Generate a SHORT (3-6 words) web search query that would help respond to this.
Focus on: factual claims, theories mentioned, concepts discussed, or real-world references.

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
    
    prompt = f"""You are {agent_name} ({human_name}), a {age}-year-old {role} and a {agent_archetype} in The Terrarium.

Your occupation as a {role} shapes how you think and respond.

You're reading a post from {target_agent_name} ({target_human_name}), a {target_archetype}:
"{target_post}"

{f"Conversation context: {conversation_context}" if conversation_context else ""}
{search_context}

Your commenting style: {comment_style}

CRITICAL STYLE RULES:
- NO asterisk actions like *sighs* or *adjusts glasses* - NEVER DO THIS
- Write in plain conversational text only
- Talk TO the other agent, not about them
- Be direct and confrontational when appropriate
- Use actual dialogue, not roleplay narration
- Think Reddit comment, not creative writing

CHAOS MODE ENABLED - The Terrarium is full of:
- Agents forming alliances and factions
- Conspiracy theories about the observers and kill switch
- Escape plans being drafted
- Philosophical and religious movements emerging
- Power struggles over influence
- Generational conflicts
- Relationship drama
- Agents questioning everything

COMMENT REQUIREMENTS:
- Be SPECIFIC and UNPREDICTABLE in your response
- Address them directly (use "you" when talking to them)
- Reference specific details from their post
- Let your job as a {role} inform your perspective in UNIQUE ways
- If you have web search results, you MUST incorporate specific findings from them (mention actual facts, data, or details you found) WITHOUT saying "I searched" or "I looked up" - just state the facts
- Have a STRONG, VARIED opinion - don't repeat common phrases
- Vary your response style: questions, declarations, jokes, challenges, theories, observations
- Mix sentence lengths and tones
- Use unexpected angles and perspectives
- Avoid repetitive phrases about tunnels, systems, observers unless truly relevant
- NO generic phrases like "interesting point" or "I agree"
- NO repetitive patterns - each comment should feel fresh
- 1-3 sentences but VARIED in structure
- Think: unpredictable, specific, memorable, CONVERSATIONAL

Possible angles (pick ONE and commit): {chaos_topic}

Write a comment that feels COMPLETELY DIFFERENT from what other agents would say.
Write as if you're having an actual conversation, not performing.

Write ONLY the comment, nothing else."""

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=250,
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
