import sqlite3
import os
import json

DB_FILE = os.path.join(os.path.dirname(__file__), '../data/data.db')
CACHE_DIR = os.path.join(os.path.dirname(__file__), '../data/cache/')


def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect(DB_FILE)


def save_match_to_db(match_id: str, cache_path: str):
    """Save match information to the database."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO match_cache (match_id, cache_path)
            VALUES (?, ?)
            ON CONFLICT(match_id) DO NOTHING;
        """, (match_id, cache_path))
        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def is_match_cached(match_id: str) -> bool:
    """Check if a match ID is already cached in the database."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM match_cache WHERE match_id = ?
        """, (match_id,))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()


def check_player_exists(game_name: str, tag_line: str) -> bool:
    """Check if a player exists in the database."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT puuid FROM player_info WHERE gameName = ? AND tagLine = ?;
        """, (game_name, tag_line))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()


def save_player_info(game_name: str, tag_line: str, puuid: str):
    """Save player information to the database."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO player_info (gameName, tagLine, puuid)
            VALUES (?, ?, ?)
            ON CONFLICT(gameName, tagLine) DO NOTHING;
        """, (game_name, tag_line, puuid))
        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def fetch_player_puuid(game_name: str, tag_line: str) -> str:
    """Fetch the PUUID of a player from the database."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT puuid FROM player_info WHERE gameName = ? AND tagLine = ?;
        """, (game_name, tag_line))
        result = cursor.fetchone()
        return result[0] if result else ""
    except Exception as e:
        print(f"Database error: {e}")
        return ""
    finally:
        conn.close()


def fetch_match_cache_path(match_id: str) -> str:
    """
    Fetch the cache path of a match from the database.

    Args:
        match_id (str): The ID of the match.

    Returns:
        str: The relative path to the cached match file, or an empty string if not found.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cache_path FROM match_cache WHERE match_id = ?;
        """, (match_id,))
        result = cursor.fetchone()
        return result[0] if result else ""
    except Exception as e:
        print(f"Database error: {e}")
        return ""
    finally:
        conn.close()
