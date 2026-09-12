# from src.data.transfermarkt_client import TransfermarktClient
# from datetime import datetime
# import requests

# test = TransfermarktClient()

# print(test.get_player_profile("937958")["name"])
# print(test.get_market_value_history("937958")[0])

# def str2date(data_tekst:str):
#     data_obiekt = datetime.strptime(data_tekst, "%Y-%m-%d").date()
#     return data_obiekt

# print(str2date("2005-03-28"))

# from src.data.db import init_db, get_session, Player

# import os
# print("Bieżący katalog roboczy:", os.getcwd())
# print("Czy istnieje 'data' tutaj:", os.path.exists("data"))


# init_db()
# session = get_session()
# print("Baza utworzona, sesja działa:", session)

# print(test.get_club_players("131"))

# from src.data.db import get_engine
# from src.features.build_dataset import load_snapshots, build_examples

# df = load_snapshots()
# examples = build_examples(df)

# print(len(examples))
# print(examples.head(20))
# print(examples["label"].value_counts())
# examples.to_csv("data/training_examples.csv", index=False)

from src.data.db import get_session, Player
from src.data.transfermarkt_client import TransfermarktClient

session = get_session()
client = TransfermarktClient()

players = session.query(Player).limit(30).all()  # próbka 30 zawodników

non_empty = 0
for player in players:
    stats = client.get_player_stats(player.transfermarkt_id)
    has_data = bool(stats)
    print(f"{player.name}: {'MA dane' if has_data else 'pusto'}")
    if has_data:
        non_empty += 1

print(f"\n{non_empty}/{len(players)} zawodników ma niepuste stats")