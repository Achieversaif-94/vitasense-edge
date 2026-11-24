from pathlib import Path

import joblib
import numpy as np
from onnxruntime import InferenceSession
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.pipeline import Pipeline


def main():
    model = joblib.load("ml/models/isolation_forest.pkl")
    scaler = joblib.load("ml/models/scaler.pkl")

    pipe = Pipeline([("scaler", scaler), ("iforest", model)])

    onnx_model = convert_sklearn(
        pipe,
        initial_types=[("input", FloatTensorType([None, 4]))],
        target_opset={"": 15, "ai.onnx.ml": 3},
    )

    out_path = Path("ml/models/isolation_forest.onnx")
    out_path.write_bytes(onnx_model.SerializeToString())
    print(f"Exported ONNX -> {out_path} ({out_path.stat().st_size} bytes)")

    sess = InferenceSession(str(out_path), providers=["CPUExecutionProvider"])
    print("ONNX inputs :", [(i.name, i.shape) for i in sess.get_inputs()])
    print("ONNX outputs:", [(o.name, o.shape) for o in sess.get_outputs()])

    X = np.array(
        [[2050.0, 75.0, 98.0, 36.8], [2250.0, 170.0, 88.0, 39.5]],
        dtype=np.float32,
    )

    output_names = [o.name for o in sess.get_outputs()]
    result = sess.run(None, {"input": X})
    print("")
    print("Raw ONNX output:")
    for i, name in enumerate(output_names):
        print(f"  {name}: {result[i]}")


if __name__ == "__main__":
    main()
