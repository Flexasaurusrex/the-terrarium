import os
import json
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
FIREBASE_CREDENTIALS = json.loads(os.getenv('FIREBASE_CREDENTIALS', '{}'))
FIREBASE_DB_URL = os.getenv('FIREBASE_DB_URL', 'https://the-terrarium-c2070-default-rtdb.europe-west1.firebasedatabase.app')

LLM_PROVIDER = 'anthropic'
MODEL_NAME = 'claude-sonnet-4-20250514'

BATCH_SIZE = 10
RELEASE_INTERVAL = 60
BATCH_INTERVAL = 600

DB_PATH = '/tmp/terrarium.db'
