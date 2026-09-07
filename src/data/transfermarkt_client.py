import requests

class TransfermarktClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def _get(self, path):
        # TODO: zrób requests.get(self.base_url + path)
        # sprawdź status (resp.raise_for_status()) i zwróć resp.json()
        resp = requests.get(self.base_url + f"{path}")
        resp.raise_for_status()
        return resp.json()

    def get_player_profile(self, player_id):
        # TODO: wywołaj self._get(...) na odpowiedniej ścieżce
        return self._get(f"/players/{player_id}/profile")

    def get_market_value_history(self, player_id):
        # TODO: to samo, ale zwróć konkretnie listę spod klucza
        # "marketValueHistory" z odpowiedzi (nie całą odpowiedź)
        data = self._get(f"/players/{player_id}/market_value")

        all_vals = data.get("marketValueHistory")
        return all_vals