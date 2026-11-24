import joblib
import numpy as np

model = joblib.load("ml/models/isolation_forest.pkl")
scaler = joblib.load("ml/models/scaler.pkl")

samples = {
    "normal (bpm=75, spo2=98, temp=36.8, ecg=2050)": [2050, 75.0, 98.0, 36.8],
    "anomaly (bpm=170, spo2=88, temp=39.5, ecg=2250)": [2250, 170.0, 88.0, 39.5],
    "borderline (bpm=110, spo2=94, temp=37.8, ecg=2100)": [2100, 110.0, 94.0, 37.8],
}

print(f"{'Sample':<55} {'Verdict':<10} {'Score':>8}")
print("-" * 75)
for label, feats in samples.items():
    X = scaler.transform(np.array([feats]))
    score = model.decision_function(X)[0]
    pred = model.predict(X)[0]
    verdict = "ANOMALY" if pred == -1 else "normal"
    print(f"{label:<55} {verdict:<10} {score:>8.4f}")
