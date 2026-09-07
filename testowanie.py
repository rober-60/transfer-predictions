from src.data.transfermarkt_client import TransfermarktClient

test = TransfermarktClient()

print(test.get_player_profile("937958")["name"])
print(test.get_market_value_history("937958")[0])
