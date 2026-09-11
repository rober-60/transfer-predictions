from src.data.db import Player, MarketValueSnapshot, init_db, get_session
from src.data.utils import str2date
from src.data.transfermarkt_client import TransfermarktClient

def upsert_player(session, player_data) -> Player:
    transfermarkt_id = player_data["id"]

    player = session.query(Player).filter_by(transfermarkt_id=transfermarkt_id).one_or_none()

    if not player:
        player = Player(transfermarkt_id=transfermarkt_id)
    
    player.name = player_data["name"]
    player.nationality = ", ".join(player_data["nationality"])
    player.position = player_data["position"]
    player.height = player_data["height"]
    player.foot = player_data["foot"]

    session.add(player)
    session.flush()
    return player

def sync_market_value_history(session, client, player):
    history = client.get_market_value_history(player.transfermarkt_id)

    dates = {da.date for da in player.market_values}

    for entry in history:
        if str2date(entry["date"]) in dates:
            continue
        else:
            print(entry)
            if entry.get("marketValue") == None:
                continue
            session.add(MarketValueSnapshot(player_id=player.id,
                                            date=str2date(entry["date"]),
                                            market_value=entry.get("marketValue"),
                                            age=entry["age"],
                                            club_name=entry["clubName"]))
    return session
    
def collect_club_players(club_id):
    client = TransfermarktClient()
    init_db()
    session = get_session()

    club = client.get_club_players(club_id)

    for player in club:
        this_player = upsert_player(session,player)
        sync_market_value_history(session,client,this_player)
        session.commit()

    session.close()

def collect_clubs(competition_id):
    client = TransfermarktClient()
    competition = client.get_clubs_from_competitions(competition_id)

    for club in competition:
        print(f'Club - {club["name"]} is processing.')
        collect_club_players(club["id"])

if __name__ == "__main__":
    collect_clubs("GB1")
