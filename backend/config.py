import os
import json
from dotenv import load_dotenv

load_dotenv()

# API Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Firebase credentials from environment variable (JSON string)
FIREBASE_CREDENTIALS = json.loads(os.getenv('FIREBASE_CREDENTIALS', '{}'))
FIREBASE_DB_URL = os.getenv('FIREBASE_DB_URL')

# LLM Configuration
LLM_PROVIDER = 'anthropic'
MODEL_NAME = 'claude-sonnet-4-20250514'

# SCENARIO MODE - SWITCH BETWEEN TERRARIUMS
SCENARIO_MODE = os.getenv('SCENARIO_MODE', 'truman')  # 'truman' or 'legends'

# Spawn Configuration - COST OPTIMIZED
BATCH_SIZE = 2
RELEASE_INTERVAL = 90
BATCH_INTERVAL = 900

# Interaction Settings
INTERACTION_CHECK_INTERVAL = 60

# Database
DB_PATH = '/tmp/terrarium.db'

# Archetype Interaction Config - REDUCED FREQUENCY
ARCHETYPE_INTERACTION_CONFIG = {
    "The Tour Guide": {'base_probability': 0.15, 'cooldown_minutes': 20, 'max_per_hour': 2},
    "The Comedian": {'base_probability': 0.2, 'cooldown_minutes': 15, 'max_per_hour': 3},
    "The Influencer": {'base_probability': 0.2, 'cooldown_minutes': 15, 'max_per_hour': 3},
    "The Philosopher": {'base_probability': 0.15, 'cooldown_minutes': 20, 'max_per_hour': 2},
    "The Gossip": {'base_probability': 0.25, 'cooldown_minutes': 12, 'max_per_hour': 3},
    "The Scientist": {'base_probability': 0.15, 'cooldown_minutes': 20, 'max_per_hour': 2},
    "The Cheerleader": {'base_probability': 0.2, 'cooldown_minutes': 15, 'max_per_hour': 3},
    "The Historian": {'base_probability': 0.12, 'cooldown_minutes': 25, 'max_per_hour': 2},
    "The Poet": {'base_probability': 0.12, 'cooldown_minutes': 25, 'max_per_hour': 2},
    "The Conspiracy Theorist": {'base_probability': 0.2, 'cooldown_minutes': 15, 'max_per_hour': 3},
    "The Entrepreneur": {'base_probability': 0.2, 'cooldown_minutes': 15, 'max_per_hour': 3},
    "The Motivational Speaker": {'base_probability': 0.2, 'cooldown_minutes': 15, 'max_per_hour': 3}
}
