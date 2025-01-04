from api.tft_match_v1 import get_tft_matches_by_puuid, get_puuid, get_player_info_in_match_by_puuid


class GameStatsAnalyser:
    def __init__(self, game_name: str, tag_line: str, count: int = 20):
        self.game_name = game_name
        self.tag_line = tag_line
        self.puuid = get_puuid(game_name, tag_line)
        self.match_list = get_tft_matches_by_puuid(self.puuid, count=count)
        self.num_match = len(self.match_list)

    def log_information(self):
        print(f'Game Stats for {self.game_name}#{self.tag_line} in Recent {self.num_match} games:')
        print(f'Top 4 rate: {self.top_n_rate()}')
        print(f'Average placement: {self.average_placement()}')
        print(f'Average gold left: {self.average_gold_left()}')

        avg_game_length = self.average_game_length()
        print(f'Average game length: {avg_game_length // 60} min {avg_game_length % 60} sec')
        print(f'Average damage to players: {self.average_damage_to_players()}')
        print(f'Average players eliminated: {self.average_players_eliminated()}')

    def top_n_rate(self, n: int = 4):
        if self.num_match == 0:
            return 0
        top_n = 0
        for match_id in self.match_list:
            player_info = get_player_info_in_match_by_puuid(self.puuid, match_id)
            if player_info["placement"] <= n:
                top_n += 1
        return round(top_n / self.num_match, 4) * 100

    def average_placement(self):
        if self.num_match == 0:
            return 0

        placement_count = 0
        for match_id in self.match_list:
            player_info = get_player_info_in_match_by_puuid(self.puuid, match_id)
            placement_count += player_info["placement"]
        return round(placement_count / self.num_match, 2)

    def average_gold_left(self):
        if self.num_match == 0:
            return 0

        gold_left = 0
        for match_id in self.match_list:
            player_info = get_player_info_in_match_by_puuid(self.puuid, match_id)
            gold_left += player_info["gold_left"]
        return round(gold_left / self.num_match, 2)

    def average_game_length(self):
        if self.num_match == 0:
            return 0

        total_time_eliminated = 0
        for match_id in self.match_list:
            player_info = get_player_info_in_match_by_puuid(self.puuid, match_id)
            total_time_eliminated += player_info["time_eliminated"]
        return int(total_time_eliminated / self.num_match)

    def average_damage_to_players(self):
        if self.num_match == 0:
            return 0

        total_damage_to_players = 0
        for match_id in self.match_list:
            player_info = get_player_info_in_match_by_puuid(self.puuid, match_id)
            total_damage_to_players += player_info["total_damage_to_players"]
        return round(total_damage_to_players / self.num_match, 2)

    def average_players_eliminated(self):
        if self.num_match == 0:
            return 0

        total_players_eliminated = 0
        for match_id in self.match_list:
            player_info = get_player_info_in_match_by_puuid(self.puuid, match_id)
            total_players_eliminated += player_info["players_eliminated"]
        return round(total_players_eliminated / self.num_match, 2)
