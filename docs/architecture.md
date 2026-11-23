# VitaSense Edge - Architecture

## Data Flow

    [ Sensors ]                  [ Edge Node ]         [ Broker ]        [ Backend ]                  [ UI ]
    ECG  (AD8232)   -+
    SpO2 (MAX30100) -+- > ESP32 --(MQTT)--> Mosquitto --> Python consumer --> InfluxDB --> Grafana
    Temp (MLX90614) -+    (or simulator)     :1883        |                   :8086        :3001
    OLED (local)                                        +--> ONNX inference
                                                        +--> anomaly flag -> InfluxDB

## Components

| Layer | Component | Role | Port |
|-------|-----------|------|------|
| Sensing | ESP32 + AD8232 + MAX30100 + MLX90614 | Reads biosignals | - |
|         | Simulator (Python) | Fake ESP32 for dev/testing | - |
| Broker | Eclipse Mosquitto | MQTT pub/sub | 1883 |
| Storage | InfluxDB 2.7 | Time-series DB (biomedical bucket) | 8086 |
| Backend | consumer/mqtt_to_influx.py | MQTT -> InfluxDB bridge | - |
| ML | Isolation Forest -> ONNX | Anomaly detection | - |
| UI | Grafana 10.4 | Live dashboard | 3001 |

## Topic & Schema

- MQTT topic: vitasense/vitals
- Payload (JSON):

    {
      "ecg": 2043,
      "bpm": 78.0,
      "spo2": 97.2,
      "temp": 36.82,
      "timestamp": "2026-11-23T14:32:01.234Z",
      "anomaly": false
    }

## Deployment

All backend services run via Docker Compose:

    docker compose up -d

Services started: mosquitto, influxdb, grafana.
Secrets are loaded from .env (gitignored). .env.example is the template.

## Phases

- Phase 1 (done): software pipeline with simulated data
- Phase 2 (in progress): ML anomaly detection
- Phase 3 (planned): ONNX edge inference + real hardware integration
