#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define SSID_name  "bmi-net"
#define SSID_passwd "00000000"

#define mqtt_server "192.168.0.8"
#define mqtt_port 1883
#define mqtt_user "lee"
#define mqtt_password "1111"
#define Client_name "spiderClient1"

#define DC_IB1    14 //D6 for PWM
#define DC_IB2    2  //D4

#define DC_IA1    12 //D6 for PWM
#define DC_IA2    0 //D4

#define Speed  1023  //Max 1023

const char* ssid = SSID_name;
const char* password = SSID_passwd;

WiFiClient espClient;
PubSubClient mqttClient(espClient);

void setup() {
  pinMode(DC_IB1, OUTPUT);
  pinMode(DC_IB2, OUTPUT);
  pinMode(DC_IA1, OUTPUT);
  pinMode(DC_IA2, OUTPUT);
  
  analogWrite(DC_IA1, 0); 
  digitalWrite(DC_IA2, LOW);
  analogWrite(DC_IB1, 0); 
  digitalWrite(DC_IB2, LOW);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(callback);
}

void loop() {
  if (!mqttClient.connected()) {
    if (mqttClient.connect(Client_name, mqtt_user, mqtt_password)) {
      mqttClient.subscribe("spider");
    } else {
      delay(5000);
      return;
    }
  }
  mqttClient.loop();
}

void callback(char* topic, byte* payload, unsigned int length) {
  //int myo_value=0;
  String msg = "";
  int i=0;
  while (i<length) msg += (char)payload[i++];
  //myo_value = msg.toInt();  
  if (msg=="11") {
      analogWrite(DC_IA1, Speed);
      //digitalWrite(DC_IA1, HIGH); 
      digitalWrite(DC_IA2, LOW);       
      analogWrite(DC_IB1, Speed); 
      //digitalWrite(DC_IB1, HIGH);
      digitalWrite(DC_IB2, LOW);       
  }
  else if (msg=="22") {
      analogWrite(DC_IA1, 1023-Speed); 
      //digitalWrite(DC_IA1, LOW); 
      digitalWrite(DC_IA2, HIGH);      
      analogWrite(DC_IB1, 1023-Speed);
      //digitalWrite(DC_IB1, LOW); 
      digitalWrite(DC_IB2, HIGH);        
  
  }
  else {
    analogWrite(DC_IA1, 0); 
    digitalWrite(DC_IA2, LOW);
    analogWrite(DC_IB1, 0); 
    digitalWrite(DC_IB2, LOW);
  }     
}
