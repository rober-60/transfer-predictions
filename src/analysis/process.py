import pandas as pd
from src.data.db import get_engine
import matplotlib.pyplot as plt

engine = get_engine()
query = "SELECT players.name, market_value_snapshots.date, market_value_snapshots.market_value FROM market_value_snapshots JOIN players ON players.id = market_value_snapshots.player_id WHERE players.name = 'Erling Haaland' ORDER BY market_value_snapshots.date"
df = pd.read_sql(query, engine)
print(df.head())

plt.xticks(rotation=45)
plt.plot(df["date"],df["market_value"])
plt.xlabel("Data")
plt.ylabel("Wartosc")
plt.show()