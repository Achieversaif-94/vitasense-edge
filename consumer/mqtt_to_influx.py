import json
import os
from datetime import datetime

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

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


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
    except json.JSONDecodeError as e:
        print(f"Bad JSON: {e}")
        return

    point = (
        Point("vitals")
        .tag("source", "simulator")
        .field("ecg", int(data["ecg"]))
        .field("bpm", float(data["bpm"]))
        .field("spo2", float(data["spo2"]))
        .field("temp", float(data["temp"]))
        .field("anomaly", bool(data.get("anomaly", False)))
        .time(datetime.fromisoformat(data["timestamp"]))
    )

    try:
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print(f"wrote: bpm={data['bpm']} spo2={data['spo2']} temp={data['temp']} anomaly={data.get('anomaly')}")
    except Exception as e:
        print(f"Influx write failed: {e}")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    print(f"Consumer running. MQTT {MQTT_BROKER}:{MQTT_PORT} -> InfluxDB {INFLUX_URL} bucket '{INFLUX_BUCKET}'")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nConsumer stopped.")
    finally:
        influx.close()


if __name__ == "__main__":
    main()
