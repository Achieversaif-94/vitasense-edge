import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"RECEIVED {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("vitasense/vitals")
print("Subscribed to vitasense/vitals. Waiting...")
client.loop_forever()
