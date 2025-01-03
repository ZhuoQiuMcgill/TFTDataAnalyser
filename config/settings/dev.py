import os
from dotenv import load_dotenv

# Explicitly load .env file from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))
# Retrieve Riot API key
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
