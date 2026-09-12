import pandas as pd
from src.data.db import get_engine
import numpy as np

def load_snapshots() -> pd.DataFrame:
    engine = get_engine()
    query = "SELECT players.id, players.name, market_value_snapshots.age, market_value_snapshots.club_name, players.position, market_value_snapshots.date, market_value_snapshots.market_value FROM market_value_snapshots JOIN players ON players.id = market_value_snapshots.player_id ORDER BY market_value_snapshots.player_id, market_value_snapshots.date"
    df = pd.read_sql(query, engine)
    df["date"] = pd.to_datetime(df["date"])
    return df

def build_examples(df: pd.DataFrame, horizon_days: int = 180, stability_threshold: float = 0.15) -> pd.DataFrame:
    """Dla każdego zawodnika, dla każdego snapshotu t, zbuduj wiersz cech + etykietę."""
    rows = []

    for player_id, group in df.groupby("id"):
        group = group.sort_values("date").reset_index(drop=True)

        for i, row_t in group.iterrows():
            past = group[group["date"] < row_t["date"]]

            future_date = row_t["date"] + pd.Timedelta(days=horizon_days)
            future = group[group["date"] >= future_date]
            if future.empty:
                continue
            future_row = future.iloc[0]  # najbliższy dostępny wpis >= future_date

            if not past.empty:
                days_since_last_snapshot = (row_t["date"] - past.iloc[-1]["date"]).days
            else:
                days_since_last_snapshot = None

            age = row_t["age"]

            past_date_target = row_t["date"] - pd.Timedelta(days=horizon_days)
            past_candidate = group[group["date"] <= past_date_target]

            if not past_candidate.empty:
                reference_row = past_candidate.iloc[-1]
                value_change_180d = (row_t["market_value"] -reference_row["market_value"])/reference_row["market_value"]
                club_change = row_t["club_name"] != reference_row["club_name"]
            else:
                value_change_180d = None
                club_change = None

            num_snapshots_before_t = len(past)

            future_change = (future_row["market_value"] - row_t["market_value"])/row_t["market_value"]
            if future_change >stability_threshold:
                label = "increase"
            elif future_change <-stability_threshold:
                label = "loss"
            else:
                label = "stable"

            recent = past.tail(4)
            if len(recent) >= 2:
                x = (recent["date"] - recent["date"].min()).dt.days
                y = recent["market_value"]
                slope = np.polyfit(x, y, 1)[0]
            else:
                slope = None

            rows.append({"days_since_last_snapshot":days_since_last_snapshot, "date": row_t["date"], "player_id":player_id, "age":age, "value_change_180d":value_change_180d, "slope": slope, "label": label, "club_change":club_change, "num_snapshots_before_t":num_snapshots_before_t})

    return pd.DataFrame(rows)