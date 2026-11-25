import json
import os
import sys
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ml.infer_onnx import VitalAnomalyDetector

load_dotenv()

INFLUX_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUX_ORG = os.getenv("INFLUXDB_ORG")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET")

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "vitasense/vitals"

influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx.write_api(write_options=SYNCHRONOUS)
detector = VitalAnomalyDetector()


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
    except json.JSONDecodeError as e:
        print(f"Bad JSON: {e}")
        return

    pred = detector.predict(
        ecg=float(data["ecg"]),
        bpm=float(data["bpm"]),
        spo2=float(data["spo2"]),
        temp=float(data["temp"]),
    )

    point = (
        Point("vitals")
        .tag("source", "simulator")
        .field("ecg", int(data["ecg"]))
        .field("bpm", float(data["bpm"]))
        .field("spo2", float(data["spo2"]))
        .field("temp", float(data["temp"]))
        .field("anomaly", bool(data.get("anomaly", False)))
        .field("onnx_anomaly", bool(pred["is_anomaly"]))
        .field("onnx_score", float(pred["score"]))
        .time(datetime.fromisoformat(data["timestamp"]))
    )

    try:
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        tag = "PRED-ANOM" if pred["is_anomaly"] else "pred-norm"
        print(f"wrote: bpm={data['bpm']:>5} score={pred['score']:+.4f} {tag}")
    except Exception as e:
        print(f"Influx write failed: {e}")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    print(f"Consumer running (ONNX). InfluxDB {INFLUX_URL} bucket '{INFLUX_BUCKET}'")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nConsumer stopped.")
    finally:
        influx.close()


if __name__ == "__main__":
    main()
