import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "vitasense/vitals"
INTERVAL = 5  # seconds


def generate_vitals():
    # 5% chance of an anomaly spike, for demo variation
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
    print(f"Connected to {BROKER}:{PORT}  ->  topic '{TOPIC}'  every {INTERVAL}s")
    try:
        while True:
            vitals = generate_vitals()
            client.publish(TOPIC, json.dumps(vitals))
            tag = "ANOMALY" if vitals["anomaly"] else "normal "
            print(f"[{tag}] bpm={vitals['bpm']:>5}  spo2={vitals['spo2']:>4}  "
                  f"temp={vitals['temp']:>4}  ecg={vitals['ecg']}")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
