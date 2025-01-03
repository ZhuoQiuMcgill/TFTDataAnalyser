import os
import json
import requests
from dotenv import load_dotenv
from data.db_manager import *
import config.settings.dev

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
            if config.settings.dev.CACHE_DEBUG_LOGGING:
                print("Fetching puuid information from database...")
            return fetch_player_puuid(game_name, tag_line)  # Use db_manager function to fetch PUUID

        # Fetch from Riot API if not in database
        if config.settings.dev.CACHE_DEBUG_LOGGING:
            print("Getting puuid information from Riot Api...")
        url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?api_key={RIOT_API_KEY}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        puuid = response.json().get('puuid', '')

        # Save to database
        if puuid:
            if config.settings.dev.CACHE_DEBUG_LOGGING:
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
        if config.settings.dev.CACHE_DEBUG_LOGGING:
            print("Getting match list from Riot Api...")
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


def get_match(match_id: str) -> dict:
    """
    Retrieve TFT match data, saving it to the local cache if not already stored.

    Args:
        match_id (str): Match ID to retrieve.

    Returns:
        dict: The match data.
    """
    try:
        # Check if match_id already exists in DB
        if is_match_cached(match_id):
            # Load match data from cache
            relative_path = fetch_match_cache_path(match_id)
            file_path = os.path.join(BASE_DIR, relative_path)
            if config.settings.dev.CACHE_DEBUG_LOGGING:
                print(f'Getting match:{match_id} from cache...')
            with open(file_path, 'r') as file:
                return json.load(file)

        # Fetch match data from Riot API
        if config.settings.dev.CACHE_DEBUG_LOGGING:
            print(f'Getting match:{match_id} from Riot Api...')
        match_data = get_tft_match_info(match_id)
        save_match(match_id, match_data)
        return match_data

    except Exception as e:
        print(f"Error retrieving match {match_id}: {e}")
        return {}


def save_match(match_id: str, match_data: dict):
    """
    Save TFT match data to local cache and database.

    Args:
        match_id (str): Match ID to save.
        match_data (dict): Match data to save.
    """
    try:
        # Save match data to local cache
        os.makedirs(CACHE_DIR, exist_ok=True)
        file_path = os.path.join(CACHE_DIR, f"{match_id}.json")
        with open(file_path, 'w') as file:
            json.dump(match_data, file)

        # Verify file saved correctly
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Failed to save match data at {file_path}")

        # Save match ID and relative path to DB
        relative_path = os.path.relpath(file_path, BASE_DIR)
        save_match_to_db(match_id, relative_path)

        if config.settings.dev.CACHE_DEBUG_LOGGING:
            print(f"Match {match_id} saved to cache.")
    except Exception as e:
        print(f"Error saving match {match_id}: {e}")


def get_player_info_in_match_by_puuid(puuid: str, match_id: str) -> dict:
    """
    Retrieve the player's information in a specific match by their PUUID.

    Args:
        puuid (str): The player's PUUID.
        match_id (str): The match ID.

    Returns:
        dict: The player's in-match information if found, otherwise an empty dictionary.
    """
    try:

        # Get match data
        match_data = get_match(match_id)
        if not match_data:
            print(f"Match data not found for match ID: {match_id}.")
            return {}

        # Find player info in participants
        participants = match_data["info"]["participants"]
        for participant in participants:
            if participant["puuid"] == puuid:
                return participant

        print(f"Player {puuid} not found in match {match_id}.")
        return {}

    except Exception as e:
        print(f"Error retrieving player info in match {match_id}: {e}")
        return {}
