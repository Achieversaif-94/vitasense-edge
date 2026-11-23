# VitaSense Edge

**Real-Time Biomedical Edge AI & IoT Anomaly Detection System**

ESP32 streams ECG, heart rate, SpO2, and body temperature over MQTT into a
time-series pipeline; an Isolation Forest anomaly detector exported to ONNX
flags anomalies in real time via Grafana.

## Architecture

See [docs/architecture.md](docs/architecture.md).

    Sensors -> ESP32 -> MQTT (Mosquitto) -> Python consumer -> InfluxDB -> Grafana
                                          -> ONNX inference (edge)

## Status

- [x] Phase 1a - Docker scaffold (InfluxDB + Grafana)
- [x] Phase 1b - MQTT broker + simulator + consumer
- [x] Phase 1c - Data collection for ML
- [ ] Phase 2  - Isolation Forest training + ONNX export
- [ ] Phase 3  - Edge inference + real hardware

## Stack

ESP32 - Python - MQTT (Mosquitto) - InfluxDB - Grafana - Scikit-learn - ONNX Runtime - Docker

## Quick start

    cp .env.example .env    # fill in values
    docker compose up -d
    pip install -r requirements.txt

    # in separate terminals:
    python consumer\mqtt_to_influx.py
    python simulator\publish_fake_vitals.py

- InfluxDB: http://localhost:8086
- Grafana:  http://localhost:3001
