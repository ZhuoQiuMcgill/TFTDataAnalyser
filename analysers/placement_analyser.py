from api.tft_match_v1 import get_tft_matches_by_puuid, get_puuid, get_player_info_in_match_by_puuid


def top_n_rate(game_name: str, tag_line: str, n: int = 4, count: int = 20):
    puuid = get_puuid(game_name, tag_line)
    match_list = get_tft_matches_by_puuid(puuid, count=count)
    total_match = len(match_list)
    top_n = 0
    for match_id in match_list:
        player_info = get_player_info_in_match_by_puuid(puuid, match_id)
        if player_info["placement"] >= n:
            top_n += 1
    return round(top_n / total_match, 4) * 100
