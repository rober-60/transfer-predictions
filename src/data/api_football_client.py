import requests
from src.config import API_FOOTBALL_KEY

class ApiFootballClient:
    def __init__(self, base_url="https://v3.football.api-sports.io"):
        self.base_url = base_url
        self.headers = {"x-apisports-key": API_FOOTBALL_KEY}

    def _get(self, path, params=None):
        resp = requests.get(self.base_url + f"{path}", headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.json()
    
    def search_player(self, name):
        return self._get("/players/profiles", params={"search": name})

    def get_player_season_stats(self, player_id, season=2023):
        return self._get("/players", params={"id": player_id, "season": season})

    def get_team_squad(self,team_id):
        resp = self._get("/players/squads", params={"team": team_id})
        return resp.get("response")[0].get("players")
