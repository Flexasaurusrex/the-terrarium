# ============================================
# THE TERRARIUM 3.0 - CONFIGURATION
# COST-OPTIMIZED SETTINGS
# ============================================

import os

# Read from Railway environment variables
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
MODEL_NAME = "claude-sonnet-4-20250514"
DB_PATH = os.environ.get('DB_PATH', '/tmp/terrarium.db')
FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS', 'firebase-credentials.json')
FIREBASE_DB_URL = os.environ.get('FIREBASE_DB_URL')

# Spawn Settings - COST OPTIMIZED
BATCH_SIZE = 2
BATCH_INTERVAL = 900
RELEASE_INTERVAL = 90

# Interaction Settings - COST OPTIMIZED
INTERACTION_CHECK_INTERVAL = 60

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
