#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// Replace the next variables with your SSID/Password combination
const char* ssid = "hqsw";
const char* password = "hqswhqsw";

// Add your MQTT Broker IP address, example:
const char* mqtt_server = "10.0.1.156";

WiFiClient espClient;
PubSubClient client(espClient);

long lastMsg = 0;
int adc_value = 0;
int ADC_PIN = 33;


void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
}

void setup() {
  Serial.begin(9600);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("pick_n_plaser")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 1000) {
    lastMsg = now;

    adc_value = analogRead(ADC_PIN);

    // Convert the value to a char array
    char adc_string[8];
    dtostrf(adc_value, 1, 0, adc_string);
    Serial.print("ADCValue: ");
    Serial.println(adc_string);
    client.publish("pick_n_plaser/light_sensor", adc_string);
  }
}