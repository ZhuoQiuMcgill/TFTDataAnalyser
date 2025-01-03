import os
import json
import requests
from dotenv import load_dotenv
from data.db_manager import *

# Load environment variables
load_dotenv()
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

# Define paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
CACHE_DIR = os.path.join(BASE_DIR, 'data', 'cache')

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

BASE_URL = 'https://americas.api.riotgames.com'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com"
}


def get_puuid(game_name: str, tag_line: str) -> str:
    """
    Retrieve the PUUID for a given player using their Riot ID.
    First checks the database; if not found, fetches from Riot API and saves to the database.

    Args:
        game_name (str): The player's Riot ID name, e.g., 'Manon Win'.
        tag_line (str): The player's tag, e.g., '236KK'.

    Returns:
        str: The PUUID if found, otherwise an empty string.
    """
    try:
        # Check if player exists in the database
        if check_player_exists(game_name, tag_line):
            print("Fetching puuid information from database...")
            return fetch_player_puuid(game_name, tag_line)  # Use db_manager function to fetch PUUID

        # Fetch from Riot API if not in database
        print("Getting puuid information from Riot Api...")
        url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?api_key={RIOT_API_KEY}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        puuid = response.json().get('puuid', '')

        # Save to database
        if puuid:
            print("Saving puuid information to database...")
            save_player_info(game_name, tag_line, puuid)

        return puuid

    except Exception as e:
        print(f"Error fetching PUUID: {e}")
        return ""


def get_tft_matches_by_puuid(puuid: str, count: int = 20) -> list:
    """
    Retrieve TFT match IDs for a given player using their PUUID.

    Args:
        puuid (str): The player's PUUID.
        count (int): Number of matches to fetch (default is 20).

    Returns:
        list: A list of match IDs if successful, otherwise an empty list.
    """
    try:
        url = f"{BASE_URL}/tft/match/v1/matches/by-puuid/{puuid}/ids?count={count}&api_key={RIOT_API_KEY}"

        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"Error fetching TFT matches: {e}")
        return []


def get_tft_match_info(match_id: str) -> dict:
    """
    Retrieve detailed TFT match information using match ID.

    Args:
        match_id (str): Match ID to fetch details.

    Returns:
        dict: Match details or an empty dictionary if an error occurs.
    """
    try:
        url = f"{BASE_URL}/tft/match/v1/matches/{match_id}"
        headers = {"X-Riot-Token": RIOT_API_KEY}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching match info for {match_id}: {e}")
        return {}


def save_match(match_id: str):
    """
    Save TFT match data to local cache if it is not already stored.

    Args:
        match_id (str): Match ID to save.
    """
    try:
        # Check if match_id already exists in DB
        if is_match_cached(match_id):
            print(f"Match {match_id} is already cached.")
            return

        # Fetch and save match data
        print(f'Getting match:{match_id} from Riot Api...')
        match_data = get_tft_match_info(match_id)
        os.makedirs(CACHE_DIR, exist_ok=True)
        file_path = os.path.join(CACHE_DIR, f"{match_id}.json")
        with open(file_path, 'w') as file:
            json.dump(match_data, file)

        # Verify file saved correctly
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Failed to save match data at {file_path}")

        # Save match ID and path to DB
        save_match_to_db(match_id, file_path)
        print(f"Match {match_id} saved to cache.")
    except Exception as e:
        print(f"Error saving match {match_id}: {e}")
