import time
from src.data.db import get_session, Player, PlayerStats, init_db
from src.data.api_football_client import ApiFootballClient
from src.data.matching import match_player
from config import CLUB_ID_MAPPING

MAX_REQUESTS_PER_DAY = 100
SEASON = 2023


def collect_stats_for_club(transfermarkt_club_id: str, session, client, requests_used: int) -> int:
    """Zwraca zaktualizowaną liczbę zużytych zapytań."""
    api_team_id = CLUB_ID_MAPPING.get(transfermarkt_club_id)
    if api_team_id is None:
        print(f"Brak mapowania dla klubu {transfermarkt_club_id}, pomijam")
        return requests_used

    # TODO 1: pobierz skład z API-Football (client.get_team_squad(api_team_id))
    #         to +1 zapytanie -> zwiększ requests_used
    squad = client.get_team_squad(api_team_id)
    requests_used+=1

    # TODO 2: pobierz z własnej bazy zawodników TEGO klubu (Player, filtrowani po ich club_name
    #         albo po transfermarkt_club_id - zależy jak to masz zapisane)
    club_name = CLUB_ID_MAPPING[transfermarkt_club_id]["name"]
    db_players = (session.query(Player).join(MarketValueSnapshot).filter(MarketValueSnapshot.club_name == club_name).distinct().all())

    for player in db_players:
        # PILNOWANIE LIMITU - sprawdź PRZED każdym zapytaniem, nie po
        if requests_used >= MAX_REQUESTS_PER_DAY:
            print("Limit dzienny osiągnięty, przerywam")
            return requests_used

        match, score = match_player(player.name, squad, threshold=85)
        if match is None:
            print(f"{player.name}: brak dopasowania")
            continue

        # TODO 3: zapisz match["id"] jako player.api_football_id (i zrób session.flush() jak poprzednio)
        player.api_football_id = match["id"]
        session.flush()

        # TODO 4: wywołaj client.get_player_season_stats(match["id"], season=SEASON)
        #         to +1 zapytanie -> zwiększ requests_used
        stats_response = client.get_player_season_stats(match["id"], season=SEASON)
        requests_used+=1

        # TODO 5: wyciągnij z odpowiedzi TYLKO wpis dla ligi krajowej (league.name == "Premier League")
        #         ze statistics - pamiętaj, że to lista wielu rozgrywek naraz (widziałeś to u Bruno Fernandesa)
        league_stats = None
        for stat_entry in stats_response["response"][0]["statistics"]:
            if stat_entry["league"]["name"] == "Premier League":
                league_stats = stat_entry
                break

        if league_stats is None:
            print(f"{player.name}: brak statystyk ligowych")
            continue

        # TODO 6: stwórz PlayerStats(...) z odpowiednich pól league_stats, session.add(...)
        session.commit()
        print(f"{player.name}: zapisano statystyki")

        time.sleep(1)

    return requests_used


if __name__ == "__main__":
    init_db()
    session = get_session()
    client = ApiFootballClient()

    requests_used = 0
    for club_id in CLUB_ID_MAPPING:
        requests_used = collect_stats_for_club(club_id, session, client, requests_used)

    session.close()
    print(f"Zużyto {requests_used} zapytań")