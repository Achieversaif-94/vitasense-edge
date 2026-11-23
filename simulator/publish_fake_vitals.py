import json
import random
import sys
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "vitasense/vitals"

FAST = "--fast" in sys.argv
INTERVAL = 0.5 if FAST else 5


def generate_vitals():
    anomaly = random.random() < 0.05
    if anomaly:
        bpm = random.randint(150, 180)
        spo2 = random.uniform(85, 92)
        temp = random.uniform(38.5, 40.0)
        ecg = random.randint(1800, 2300)
    else:
        bpm = random.randint(65, 95)
        spo2 = random.uniform(95, 99)
        temp = random.uniform(36.3, 37.2)
        ecg = random.randint(1950, 2150)
    return {
        "ecg": ecg,
        "bpm": round(bpm, 1),
        "spo2": round(spo2, 1),
        "temp": round(temp, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "anomaly": anomaly,
    }


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    mode = "FAST" if FAST else "normal"
    print(f"[{mode}] Publishing to '{TOPIC}' every {INTERVAL}s. Ctrl+C to stop.")
    try:
        while True:
            v = generate_vitals()
            client.publish(TOPIC, json.dumps(v))
            tag = "ANOMALY" if v["anomaly"] else "normal "
            print(f"[{tag}] bpm={v['bpm']:>5}  spo2={v['spo2']:>4}  temp={v['temp']:>4}")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
