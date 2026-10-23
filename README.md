# Telemetri med ESP32, MQTT och Azure IoT Hub

## Lösningens delar

Två ESP32-enheter med varsin DHT11 skickar sensorvärden via WiFi
och MQTT till Mosquitto på Raspberry Pi.

- `sensor_01.ino` skickar temperatur i °C.
- `sensor_02.ino` skickar luftfuktighet i %.
- `gateway.py` tar emot MQTT-meddelanden och skickar dem till Azure
  IoT Hub via HTTPS. Mottagna meddelanden köas lokalt vid avbrott.
- `local_consumer.py` visar värden från den lokala MQTT-brokern.
- `azure_consumer.py` läser och visar värden från Azure.
- `common.py` innehåller gemensam konfiguration och datavalidering.

Varje ESP32 har ett unikt deviceId och ett eget topic.
Meddelandena skickas som JSON med bland annat deviceId, value och unit.
Båda enheterna skickar var 60:e sekund.

## Förberedelser

### ESP32

Installera ESP32-kortpaketet och biblioteken DHT sensor library,
Adafruit Unified Sensor och PubSubClient i Arduino IDE.

Kopiera `config.example.h` till `config.h` i respektive sensormapp.
Fyll i WiFi, Pi:ns IP-adress och MQTT-inloggning.
Ladda upp respektive `.ino`-fil till rätt ESP32.

Sensorernas signal är ansluten till GPIO 4.
Båda ESP32-enheterna måste ha ström.

### Raspberry Pi och Azure

Mosquitto ska vara igång på Pi:n på port 1883.

Gatewayen använder den registrerade Azure-enheten `pi-gateway`.
Azure-konsumenten använder IoT Hubs Event Hub-kompatibla
anslutningssträng med behörigheten Service connect.

Skapa en lokal `.env`-fil i projektmappen:

```ini
MQTT_HOST=127.0.0.1
MQTT_PORT=1883
MQTT_USER=YOUR_USERNAME
MQTT_PASSWORD=YOUR_PASSWORD
AZURE_DEVICE_CONNECTION_STRING=YOUR_DEVICE_CONNECTION_STRING
EVENTHUB_CONNECTION_STRING=YOUR_EVENTHUB_CONNECTION_STRING
EVENTHUB_CONSUMER_GROUP=$Default
```

## Installation och start

Kör i projektmappen på Raspberry Pi:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Öppna tre terminaler i projektmappen och aktivera miljön i varje:

```bash
source .venv/bin/activate
```

Starta ett program i varje terminal:

```bash
python local_consumer.py
```

```bash
python azure_consumer.py
```

```bash
python gateway.py
```

Vänta upp till 60 sekunder på nya sensorvärden.
Avsluta programmen med Ctrl+C.
