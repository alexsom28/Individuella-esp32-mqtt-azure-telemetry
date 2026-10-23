Trådlös telemetri med ESP32, MQTT och Azure IoT Hub

I arbetet har jag byggt en lösning som samlar in temperatur och luftfuktighet från två ESP32-enheter med varsin DHT11-sensor. Den första enheten skickar temperatur och den andra skickar luftfuktighet.

Enheterna ansluter via WiFi och publicerar mätvärden var 60:e sekund till en Mosquitto-broker på Raspberry Pi. Varje enhet har ett unikt deviceId och ett eget MQTT-topic. Meddelandena skickas som JSON och innehåller enhets-ID, typ av mätning, värde och mätenhet.

På Raspberry Pi körs en gatewayapplikation i Python som prenumererar på båda enheternas topics. Gatewayen skickar meddelandena vidare till Azure IoT Hub via HTTPS och använder den registrerade enhetsidentiteten pi-gateway. Sensorernas ursprungliga enhets-ID och mätvärden bevaras. Om Azure inte kan nås sparas mottagna meddelanden i en lokal SQLite-kö för senare leverans.

En lokal MQTT-konsument visar värden från brokern, medan en separat Azure-konsument läser och visar meddelanden från molnet. Lösningen har verifierats genom att båda sensorernas värden visats samtidigt på Raspberry Pi med mosquitto_sub och därefter i Azure-konsumenten.

WiFi- och MQTT-inställningar hanteras i lokala konfigurationsfiler för ESP32-enheterna.
