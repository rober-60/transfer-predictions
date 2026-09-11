import requests

class TransfermarktClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def _get(self, path):
        resp = requests.get(self.base_url + f"{path}")
        resp.raise_for_status()
        return resp.json()

    def get_player_profile(self, player_id):
        return self._get(f"/players/{player_id}/profile")

    def get_market_value_history(self, player_id):
        data = self._get(f"/players/{player_id}/market_value")

        all_vals = data.get("marketValueHistory")
        return all_vals
    
    def get_club_players(self, club_id):
        data = self._get(f"/clubs/{club_id}/players")
        return data.get("players")

    def get_clubs_from_competitions(self, competition_id):
        data = self._get(f"/competitions/{competition_id}/clubs")
        return data.get("clubs")