import os
import sys
from dotenv import load_dotenv

# Set project root directory relative to the scripts folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(project_root, '.env'))

RIOT_NAME = "Manon Win#236KK"
GAME_NAME = RIOT_NAME.split("#")[0]
TAG_LINE = RIOT_NAME.split("#")[1]


def main():
    print("Running tests...")

    # Run tests
    # api_key_test()
    # test_save_matches()
    test_game_stats_analyser()


def api_key_test():
    try:
        # Retrieve API key from settings
        api_key = os.getenv('RIOT_API_KEY')

        # Check if the API key exists and is valid
        if api_key and len(api_key) > 0:
            print(f"API Key Loaded Successfully: {api_key[:5]}******")
        else:
            print("API Key is empty or not found in the environment variables.")
    except AttributeError:
        print("Error: RIOT_API_KEY is not defined in the settings.")
    except Exception as e:
        print(f"An error occurred while loading the API Key: {e}")


def test_get_match_id():
    try:
        from tft_match_v1 import get_puuid, get_tft_matches_by_puuid
        puuid = get_puuid(GAME_NAME, TAG_LINE)
        match_id = get_tft_matches_by_puuid(puuid)
        print(match_id)

    except ImportError as e:
        print(f"ImportError: {e}")
    except Exception as e:
        print(f"Error during test_get_match_id: {e}")


def test_get_puuid():
    try:
        from api.tft_match_v1 import get_puuid
        result = get_puuid(GAME_NAME, TAG_LINE)

        print(f"Test get_puuid result: {result}")

    except ImportError as e:
        print(f"ImportError: {e}")
    except Exception as e:
        print(f"Error during test_get_puuid: {e}")


def test_save_matches():
    try:
        from api.tft_match_v1 import get_puuid, get_tft_matches_by_puuid, get_match
        puuid = get_puuid(GAME_NAME, TAG_LINE)
        matches = get_tft_matches_by_puuid(puuid, count=20)
        for match_id in matches:
            participants = get_match(match_id)["info"]["participants"]
            for participant in participants:
                if participant["puuid"] == puuid:
                    print(f'Placement: {participant["placement"]}')

    except ImportError as e:
        print(f"ImportError: {e}")
    except Exception as e:
        print(f"Error during test_save_matches: {e}")


def test_game_stats_analyser():
    from analysers.game_stats_analyser import GameStatsAnalyser

    count = 10
    gs_analyser = GameStatsAnalyser(GAME_NAME, TAG_LINE, count)
    gs_analyser.log_information()


if __name__ == "__main__":
    main()
