import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

FEATURES = ["ecg", "bpm", "spo2", "temp"]


def main():
    df = pd.read_csv("data/training_data.csv")
    print(f"Loaded {len(df)} rows from data/training_data.csv")

    X = df[FEATURES].values
    y_true = df["anomaly"].astype(int).values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_scaled)

    y_pred = (model.predict(X_scaled) == -1).astype(int)

    print("\n=== Evaluation on training data ===")
    print(classification_report(y_true, y_pred, target_names=["normal", "anomaly"]))
    print("Confusion matrix:")
    print(confusion_matrix(y_true, y_pred))

    out_dir = Path("ml/models")
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_dir / "isolation_forest.pkl")
    joblib.dump(scaler, out_dir / "scaler.pkl")

    meta = {
        "features": FEATURES,
        "n_estimators": 100,
        "contamination": 0.05,
        "trained_on_rows": int(len(df)),
        "anomaly_rate_actual": float(y_true.mean()),
    }
    with open(out_dir / "model_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nSaved model  -> {out_dir / 'isolation_forest.pkl'}")
    print(f"Saved scaler -> {out_dir / 'scaler.pkl'}")
    print(f"Saved meta   -> {out_dir / 'model_meta.json'}")


if __name__ == "__main__":
    main()
