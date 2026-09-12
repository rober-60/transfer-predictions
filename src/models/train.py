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

    feature_cols = ["days_since_last_snapshot", "age", "value_change_180d", "slope", "club_change", "num_snapshots_before_t"]

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

    importances = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False)
    print(importances)

    y_pred = model.predict(X_test)

    return accuracy_score(Y_test, y_pred), classification_report(Y_test, y_pred, target_names=["loss", "stable", "increase"])
    
if __name__ == "__main__":
    acc, report = train_model("data/training_examples.csv")
    print(f"Accuracy: {acc}")
    print(report)
    