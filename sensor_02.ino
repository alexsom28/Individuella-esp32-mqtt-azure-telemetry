#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include "config.h"

DHT dht(4, DHT11);
WiFiClient network;
PubSubClient mqtt(network);

const char* DEVICE_ID = "sensor-02";
const char* TOPIC = "telemetry/sensor-02/humidity";

unsigned long lastWifi = 0;
unsigned long lastMqtt = 0;
unsigned long lastReading = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setSocketTimeout(3);

  Serial.println("Startar sensor-02...");
}

void loop() {
  unsigned long now = millis();

  if (WiFi.status() != WL_CONNECTED) {
    if (now - lastWifi >= 30000) {
      lastWifi = now;
      Serial.println("Forsoker ansluta till WiFi igen...");
      WiFi.reconnect();
    }

    delay(10);
    return;
  }

  if (!mqtt.connected()) {
    if (now - lastMqtt >= 5000) {
      lastMqtt = now;

      if (mqtt.connect(DEVICE_ID, MQTT_USER, MQTT_PASSWORD)) {
        Serial.println("MQTT ansluten");
      } else {
        Serial.print("MQTT-fel: ");
        Serial.println(mqtt.state());
      }
    }

    delay(10);
    return;
  }

  mqtt.loop();

  if (now - lastReading >= 60000) {
    lastReading = now;

    float value = dht.readHumidity();

    if (isnan(value)) {
      Serial.println("Sensorfel: kontrollera kablar och sensortyp");
      return;
    }

    char payload[160];

    snprintf(
      payload,
      sizeof(payload),
      "{\"deviceId\":\"%s\",\"type\":\"humidity\",\"value\":%.1f,\"unit\":\"%%\"}",
      DEVICE_ID,
      value
    );

    bool sent = mqtt.publish(TOPIC, payload, false);

    Serial.print(sent ? "Skickat: " : "Publicering misslyckades: ");
    Serial.println(payload);
  }
}