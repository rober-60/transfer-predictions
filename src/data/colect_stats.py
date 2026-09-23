import time
from src.data.db import get_session, Player, PlayerStats, MarketValueSnapshot, init_db
from src.data.api_football_client import ApiFootballClient
from src.data.matching import match_player
from src.config import CLUB_ID_MAPPING

MAX_REQUESTS_PER_DAY = 100
SEASON = 2023


def collect_stats_for_club(transfermarkt_club_id: str, session, client, requests_used: int) -> int:
    """Zwraca zaktualizowaną liczbę zużytych zapytań."""
    club_info = CLUB_ID_MAPPING.get(transfermarkt_club_id)
    if club_info is None:
        print(f"Brak mapowania dla klubu {transfermarkt_club_id}, pomijam")
        return requests_used
    api_team_id = club_info["api_id"]
    club_name = club_info["name"]

    squad = client.get_team_squad(api_team_id)
    requests_used+=1

    db_players = (session.query(Player).join(MarketValueSnapshot).filter(MarketValueSnapshot.club_name == club_name).distinct().all())

    for player in db_players:
        if requests_used >= MAX_REQUESTS_PER_DAY:
            print("Limit dzienny osiągnięty, przerywam")
            return requests_used

        match, score = match_player(player.name, squad, threshold=85)
        if match is None:
            print(f"{player.name}: brak dopasowania")
            continue

        player.api_football_id = str(match["id"])
        session.flush()

        stats_response = client.get_player_season_stats(match["id"], season=SEASON)
        requests_used+=1

        league_stats = None
        for stat_entry in stats_response["response"][0]["statistics"]:
            if stat_entry["league"]["name"] == "Premier League":
                league_stats = stat_entry
                break

        if league_stats is None:
            print(f"{player.name}: brak statystyk ligowych")
            continue

        session.add(PlayerStats(
                                player_id=player.id,
                                appearences=league_stats["games"]["appearences"],
                                minutes=league_stats["games"]["minutes"],
                                total_goals=league_stats["goals"]["total"],
                                assists=league_stats["goals"]["assists"],
                                rating=float(league_stats["games"]["rating"]) if league_stats["games"]["rating"] else None,
                                season=SEASON,
                            ))
        
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