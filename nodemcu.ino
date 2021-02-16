
#include <DHTesp.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

#ifdef ESP32
#error Select ESP8266 board.
#endif

DHTesp dht;

#define wifi_ssid "SSID"
#define wifi_password "WIFIPASS"

WiFiClient espClient;
ESP8266WebServer server(80);

void setup()
{
  Serial.begin(115200);

  server.on("/", handle_OnConnect);
  server.onNotFound(handle_NotFound);

  server.begin();
  Serial.println("HTTP server started");

  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  
  Serial.println();
  Serial.println("Status\tHumidity (%)\tTemperature (C)\t(F)\tHeatIndex (C)\t(F)");

  dht.setup(D4, DHTesp::DHT22);
}

void setup_wifi() {
  delay(10);
  WiFi.begin(wifi_ssid, wifi_password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
}

void loop() {
    server.handleClient();
}

void handle_OnConnect() {
  delay(dht.getMinimumSamplingPeriod());
  float humidity = dht.getHumidity();
  float temperature = dht.getTemperature();
  server.send(200, "text/html", SendHTML(temperature, humidity));
}

void handle_NotFound() {
  server.send(404, "text/plain", "Not found");
}

String SendHTML(float Temperaturestat, float Humiditystat) {
  String ptr = "";
  ptr += Temperaturestat;
  ptr += ",";
  ptr += Humiditystat;
  return ptr;
}
