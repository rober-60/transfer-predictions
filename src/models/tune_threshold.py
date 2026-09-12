from src.features.build_dataset import build_examples,load_snapshots
from src.models.train import train_model

df = load_snapshots()

for threshold in [0.05, 0.10, 0.15, 0.20]:
    examples = build_examples(df, stability_threshold=threshold)
    examples.to_csv("data/training_examples_tmp.csv", index=False)
    acc, report = train_model("data/training_examples_tmp.csv")
    print(f"--- threshold={threshold} ---")
    print(f"Accuracy: {acc}")
    print(report)