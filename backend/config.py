# ============================================
# THE TERRARIUM 3.0 - CONFIGURATION
# COST-OPTIMIZED SETTINGS
# ============================================

# Anthropic API
ANTHROPIC_API_KEY = "your-api-key-here"
MODEL_NAME = "claude-sonnet-4-20250514"

# Database
DB_PATH = "/tmp/terrarium.db"

# Firebase
FIREBASE_CREDENTIALS = "firebase-credentials.json"
FIREBASE_DB_URL = "your-firebase-url"

# Spawn Settings - COST OPTIMIZED
BATCH_SIZE = 2  # Down from 3 (33% fewer agents)
BATCH_INTERVAL = 900  # 15 minutes instead of 10 (40% slower)
RELEASE_INTERVAL = 90  # 1.5 minutes between agents instead of 60s

# Interaction Settings - COST OPTIMIZED
INTERACTION_CHECK_INTERVAL = 60  # Check every 60s instead of 30s (50% fewer checks)

# Archetype Interaction Config - REDUCED FREQUENCY
ARCHETYPE_INTERACTION_CONFIG = {
    "The Tour Guide": {
        'base_probability': 0.15,  # Down from 0.3
        'cooldown_minutes': 20,    # Up from 10
        'max_per_hour': 2          # Down from 5
    },
    "The Comedian": {
        'base_probability': 0.2,   # Down from 0.4
        'cooldown_minutes': 15,    # Up from 8
        'max_per_hour': 3          # Down from 6
    },
    "The Influencer": {
        'base_probability': 0.2,   # Down from 0.4
        'cooldown_minutes': 15,    # Up from 8
        'max_per_hour': 3          # Down from 6
    },
    "The Philosopher": {
        'base_probability': 0.15,  # Down from 0.3
        'cooldown_minutes': 20,    # Up from 12
        'max_per_hour': 2          # Down from 4
    },
    "The Gossip": {
        'base_probability': 0.25,  # Down from 0.5
        'cooldown_minutes': 12,    # Up from 6
        'max_per_hour': 3          # Down from 8
    },
    "The Scientist": {
        'base_probability': 0.15,  # Down from 0.3
        'cooldown_minutes': 20,    # Up from 10
        'max_per_hour': 2          # Down from 5
    },
    "The Cheerleader": {
        'base_probability': 0.2,   # Down from 0.4
        'cooldown_minutes': 15,    # Up from 8
        'max_per_hour': 3          # Down from 6
    },
    "The Historian": {
        'base_probability': 0.12,  # Down from 0.25
        'cooldown_minutes': 25,    # Up from 12
        'max_per_hour': 2          # Down from 4
    },
    "The Poet": {
        'base_probability': 0.12,  # Down from 0.25
        'cooldown_minutes': 25,    # Up from 15
        'max_per_hour': 2          # Down from 3
    },
    "The Conspiracy Theorist": {
        'base_probability': 0.2,   # Down from 0.35
        'cooldown_minutes': 15,    # Up from 10
        'max_per_hour': 3          # Down from 5
    },
    "The Entrepreneur": {
        'base_probability': 0.2,   # Down from 0.35
        'cooldown_minutes': 15,    # Up from 10
        'max_per_hour': 3          # Down from 5
    },
    "The Motivational Speaker": {
        'base_probability': 0.2,   # Down from 0.35
        'cooldown_minutes': 15,    # Up from 10
        'max_per_hour': 3          # Down from 5
    }
}
