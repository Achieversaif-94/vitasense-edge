from pathlib import Path

import numpy as np
from onnxruntime import InferenceSession

MODEL_PATH = Path("ml/models/isolation_forest.onnx")


class VitalAnomalyDetector:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.session = InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, ecg: float, bpm: float, spo2: float, temp: float) -> dict:
        X = np.array([[ecg, bpm, spo2, temp]], dtype=np.float32)
        result = self.session.run(None, {self.input_name: X})
        label = int(result[0][0][0])
        score = float(result[1][0][0])
        return {
            "is_anomaly": label == -1,
            "label": label,
            "score": round(score, 4),
        }


if __name__ == "__main__":
    det = VitalAnomalyDetector()
    print(f"Loaded ONNX model from {MODEL_PATH}")
    print("")
    tests = [
        ("normal   ", 2050, 75.0, 98.0, 36.8),
        ("anomaly  ", 2250, 170.0, 88.0, 39.5),
        ("borderline", 2100, 110.0, 94.0, 37.8),
    ]
    for name, ecg, bpm, spo2, temp in tests:
        r = det.predict(ecg, bpm, spo2, temp)
        verdict = "ANOMALY" if r["is_anomaly"] else "normal "
        print(f"  {name}  bpm={bpm:>5} spo2={spo2:>4} temp={temp:>4}  ->  {verdict}  score={r['score']:>8.4f}")
