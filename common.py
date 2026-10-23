"""Gemensam konfiguration och kontroll av datakontraktet."""
import json
import math
import os
from pathlib import Path
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv(Path(__file__).with_name('.env'))
EXPECTED = {
    'telemetry/sensor-01/temperature': ('sensor-01', 'temperature', '°C'),
    'telemetry/sensor-02/humidity': ('sensor-02', 'humidity', '%'),
}

def validate(payload, topic=None):
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError('JSON måste vara ett objekt')
    identity = (data.get('deviceId'), data.get('type'), data.get('unit'))
    if topic is not None:
        if topic not in EXPECTED or identity != EXPECTED[topic]:
            raise ValueError('Topic och enhetsuppgifter stämmer inte')
    elif identity not in EXPECTED.values():
        raise ValueError('Okänd enhet eller mätenhet')
    value = data.get('value')
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('value måste vara ett ändligt tal')
    return data

def display(source, data):
    print(f"[{source}] {data['deviceId']} {data['type']}: {data['value']} {data['unit']}", flush=True)

def local_client(name, on_message):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=name)
    user = os.getenv('MQTT_USER', '')
    if user:
        client.username_pw_set(user, os.getenv('MQTT_PASSWORD', ''))
    def connected(c, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print('MQTT-anslutning nekad:', reason_code, flush=True)
            return
        for topic in EXPECTED:
            c.subscribe(topic, qos=1)
        print('Prenumererar på båda enheterna', flush=True)
    client.on_connect = connected
    client.on_message = on_message
    client.reconnect_delay_set(1, 30)
    client.connect_async(os.getenv('MQTT_HOST', '127.0.0.1'), int(os.getenv('MQTT_PORT', '1883')), 60)
    return client
