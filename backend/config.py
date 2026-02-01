import os
import json
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
FIREBASE_CREDENTIALS = json.loads(os.getenv('FIREBASE_CREDENTIALS', '{}'))
FIREBASE_DB_URL = os.getenv('FIREBASE_DB_URL', 'https://the-terrarium-c2070-default-rtdb.europe-west1.firebasedatabase.app')

LLM_PROVIDER = 'anthropic'
MODEL_NAME = 'claude-sonnet-4-20250514'

# Spawn Configuration
BATCH_SIZE = 10
RELEASE_INTERVAL = 60  # 1 agent per minute
BATCH_INTERVAL = 600   # Generate batch every 10 minutes

# Interaction Configuration
INTERACTION_CHECK_INTERVAL = 30  # Check for interactions every 30 seconds
FACTION_FORMATION_THRESHOLD = 100  # Start forming factions after 100 agents
MOVEMENT_START_THRESHOLD = 50  # Movements can start after 50 agents

DB_PATH = '/tmp/terrarium.db'

# Archetype interaction configurations
ARCHETYPE_INTERACTION_CONFIG = {
    "The Influencer": {
        "base_probability": 0.8,
        "cooldown_minutes": 5,
        "max_per_hour": 12
    },
    "The Gossip": {
        "base_probability": 0.7,
        "cooldown_minutes": 7,
        "max_per_hour": 10
    },
    "The Comedian": {
        "base_probability": 0.6,
        "cooldown_minutes": 8,
        "max_per_hour": 8
    },
    "The Conspiracy Theorist": {
        "base_probability": 0.6,
        "cooldown_minutes": 10,
        "max_per_hour": 6
    },
    "The Cheerleader": {
        "base_probability": 0.5,
        "cooldown_minutes": 10,
        "max_per_hour": 6
    },
    "The Tour Guide": {
        "base_probability": 0.5,
        "cooldown_minutes": 12,
        "max_per_hour": 5
    },
    "The Philosopher": {
        "base_probability": 0.4,
        "cooldown_minutes": 15,
        "max_per_hour": 4
    },
    "The Motivational Speaker": {
        "base_probability": 0.4,
        "cooldown_minutes": 15,
        "max_per_hour": 4
    },
    "The Entrepreneur": {
        "base_probability": 0.4,
        "cooldown_minutes": 15,
        "max_per_hour": 4
    },
    "The Poet": {
        "base_probability": 0.3,
        "cooldown_minutes": 20,
        "max_per_hour": 3
    },
    "The Scientist": {
        "base_probability": 0.3,
        "cooldown_minutes": 20,
        "max_per_hour": 3
    },
    "The Historian": {
        "base_probability": 0.2,
        "cooldown_minutes": 30,
        "max_per_hour": 2
    }
}
