import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils.class_weight import compute_sample_weight

def most_one(file):
    df = pd.read_csv(file)
    df["date"] = pd.to_datetime(df["date"])
    df_sorted = df.sort_values(by="date", ascending=True)
    point = df_sorted["date"].quantile(0.8)

    train = df[df["date"] < point]
    test = df[df["date"] >= point]
    labels = train["label"].value_counts()

    most_common_count = labels.iloc[0]
    most_common_label = labels.index[0]

    ptc = (test["label"]==most_common_label).sum()/len(test)
    return ptc, most_common_label, most_common_count 

def train_model(file):
    df = pd.read_csv(file)
    df["date"] = pd.to_datetime(df["date"])
    df_sorted = df.sort_values(by="date")
    point = df_sorted["date"].quantile(0.8)

    train = df[df["date"] < point]
    test = df[df["date"] >= point]

    feature_cols = ["days_since_last_snapshot", "age", "value_change_180d", "club_change", "num_snapshots_before_t"]

    # TODO 1: wydziel X_train, y_train, X_test, y_test z train/test, używając feature_cols i "label"
    # TODO 2: club_change to bool/None - XGBoost woli liczby; zamień na float (True->1, False->0, None zostaje NaN)
    # TODO 3: stwórz model = XGBClassifier(...), wytrenuj przez model.fit(X_train, y_train)
    # TODO 4: zrób predykcje: y_pred = model.predict(X_test)
    # TODO 5: wypisz accuracy_score(y_test, y_pred) i classification_report(y_test, y_pred)
    label_map = {"loss": 0, "stable": 1, "increase": 2}

    X_train = train[feature_cols].copy()
    Y_train = train["label"].map(label_map)
    X_test = test[feature_cols].copy()
    Y_test = test["label"].map(label_map)

    X_train["club_change"] = X_train["club_change"].astype(float)
    X_test["club_change"] = X_test["club_change"].astype(float)

    model = XGBClassifier()
    sample_weights = compute_sample_weight(class_weight="balanced", y=Y_train)
    model.fit(X_train, Y_train, sample_weight=sample_weights)

    y_pred = model.predict(X_test)

    return accuracy_score(Y_test, y_pred), classification_report(Y_test, y_pred, target_names=["loss", "stable", "increase"])
    
if __name__ == "__main__":
    acc, report = train_model("data/training_examples.csv")
    print(f"Accuracy: {acc}")
    print(report)
    