import os
import sys
from dotenv import load_dotenv
import pandas as pd
from influxdb_client import InfluxDBClient

load_dotenv()

url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
token = os.getenv("INFLUXDB_TOKEN")
org = os.getenv("INFLUXDB_ORG")
bucket = os.getenv("INFLUXDB_BUCKET")

client = InfluxDBClient(url=url, token=token, org=org)

query = f"""
from(bucket: "{bucket}")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "vitals")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"])
"""

print(f"Querying bucket '{bucket}'...")
result = client.query_api().query_data_frame(query)

if isinstance(result, list):
    if len(result) == 0:
        print("No data found in InfluxDB.")
        client.close()
        sys.exit(1)
    df = pd.concat(result, ignore_index=True)
else:
    df = result

if df is None or df.empty:
    print("No data found in InfluxDB.")
    client.close()
    sys.exit(1)

cols = ["_time", "ecg", "bpm", "spo2", "temp", "anomaly"]
missing = [c for c in cols if c not in df.columns]
if missing:
    print(f"Missing columns: {missing}. Available: {list(df.columns)}")
    client.close()
    sys.exit(1)

df = df[cols].rename(columns={"_time": "timestamp"})
os.makedirs("data", exist_ok=True)
out = "data/training_data.csv"
df.to_csv(out, index=False)
print(f"Exported {len(df)} rows -> {out}")
print("\nHEAD:")
print(df.head())
print("\nTAIL:")
print(df.tail())
client.close()
