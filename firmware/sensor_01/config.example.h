#pragma once
#include <stdint.h>

// Kopiera filen till config.h och fyll i dina uppgifter lokalt.
// Publicera aldrig config.h med riktiga lösenord.

const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Raspberry Pi:s lokala IP-adress.
const char* MQTT_HOST = "192.168.1.100";
const uint16_t MQTT_PORT = 1883;

const char* MQTT_USER = "YOUR_MQTT_USERNAME";
const char* MQTT_PASSWORD = "YOUR_MQTT_PASSWORD";
