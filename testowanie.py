# from src.data.transfermarkt_client import TransfermarktClient
from datetime import datetime

# test = TransfermarktClient()

# print(test.get_player_profile("937958")["name"])
# print(test.get_market_value_history("937958")[0])

def str2date(data_tekst:str):
    data_obiekt = datetime.strptime(data_tekst, "%Y-%m-%d").date()
    return data_obiekt

print(str2date("2005-03-28"))