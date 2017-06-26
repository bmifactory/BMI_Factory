#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define SSID_name  "bmi-net"
#define SSID_passwd  "00000000"

#define mqtt_server "192.168.0.8"
#define mqtt_port 1883
#define mqtt_user "lee"
#define mqtt_password "1111"

#define DC_PWMA    14
#define DC_AIN2    12
#define DC_AIN1    13
#define DC_STBY    15 

#define Myo_TH     100 

const char* ssid = SSID_name;
const char* password = SSID_passwd;

WiFiClient espClient;
PubSubClient mqttClient(espClient);

void setup() {
  pinMode(DC_PWMA, OUTPUT);
  pinMode(DC_AIN2, OUTPUT);
  pinMode(DC_AIN1, OUTPUT);
  pinMode(DC_STBY, OUTPUT);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(callback);
}

void loop() {
  if (!mqttClient.connected()) {
    if (mqttClient.connect("spiderClient0", mqtt_user, mqtt_password)) {
      mqttClient.subscribe("myo");
    } else {
      delay(5000);
      return;
    }
  }
  mqttClient.loop();
}

void callback(char* topic, byte* payload, unsigned int length) {
  int myo_value=0;
  String msg = "";
  int i=0;
  while (i<length) msg += (char)payload[i++];
  myo_value = msg.toInt();  
  if (myo_value > Myo_TH ) {
     analogWrite(DC_PWMA, 1000);
     digitalWrite(DC_AIN2, HIGH); 
     digitalWrite(DC_AIN1, LOW); 
     digitalWrite(DC_STBY, HIGH); 
  } else {
     digitalWrite(DC_STBY, LOW);
     myo_value=0;
  }     
}
