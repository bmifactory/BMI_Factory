/**
 * 
 * a mod of the original from arduino-openEMSstim: https://github.com/PedroLopes/openEMSstim, see 
 * <https://bitbucket.org/MaxPfeiffer/letyourbodymove/wiki/Home/License>
 */ 

#include <Wire.h>
#include <WiFiEsp.h>
#include <WiFiEspClient.h>
#include <SoftwareSerial.h>
#include <PubSubClient.h>
#include "AD5252.h"
#include "EMSSystem.h"
#include "EMSChannel.h"

#define SSID_name "bmi-net"
#define SSID_pass "12345678"
#define mqttClient_name "EMSClient0"
#define mqttTopic "ems"

IPAddress mqttBrokerIP(192, 168, 0, 8);
char ssid[] = SSID_name;       // your network SSID (name)
char pass[] = SSID_pass;       // your network password
int status = WL_IDLE_STATUS;   // the Wifi radio's status

const int buttonPin1 = 11;     // the number of the pushbutton pin
const int buttonPin2 = 12;     // the number of the pushbutton pin
int buttonState1 = 0;
int buttonState2 = 0;
const int ledPin =  13;      // the number of the LED pin

//helper print function that handles the DEBUG_ON flag automatically
void printer(String msg, boolean force = false) {
    Serial.println(msg);
}

//Initialization of control objects
WiFiEspClient espClient;
PubSubClient mqttClient(espClient);
SoftwareSerial softSerial(8,9); // RX, TX
AD5252 digitalPot(0);
EMSChannel emsChannel1(5, 4, A2, &digitalPot, 1);
EMSChannel emsChannel2(6, 7, A3, &digitalPot, 3);
EMSSystem emsSystem(2);

const char ems_channel_1_active[]    PROGMEM = "EMS: Channel 1 active";
const char ems_channel_1_inactive[]  PROGMEM = "EMS: Channel 1 inactive";
const char ems_channel_2_active[]    PROGMEM = "EMS: Channel 2 active";
const char ems_channel_2_inactive[]  PROGMEM = "EMS: Channel 2 inactive";
const char ems_channel_1_intensity[] PROGMEM = "EMS: Intensity Channel 1: ";
const char ems_channel_2_intensity[] PROGMEM = "EMS: Intensity Channel 2: ";
const char* const string_table_outputs[] PROGMEM = {ems_channel_1_active, ems_channel_1_inactive, ems_channel_2_active, ems_channel_2_inactive, ems_channel_1_intensity, ems_channel_2_intensity};

void setup() {
  pinMode(buttonPin1, INPUT);
  pinMode(buttonPin2, INPUT);
  pinMode(13, OUTPUT);
  Serial.begin(115200);  // initialize serial for debugging 
  Serial.setTimeout(50);
  softSerial.begin(9600); // initialize serial for ESP module
  softSerial.setTimeout(100);
  WiFi.init(&softSerial); // initialize ESP module
  
  // attempt to connect to WiFi network
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);  
    status = WiFi.begin(ssid, pass);  // Connect to WPA/WPA2 network
  }

  //you're connected now, so print out the data
  //printWifiData();
  
  //connect to MQTT Broker
  mqttClient.setServer(mqttBrokerIP, 1883);
  mqttClient.setCallback(callback);
  delay(100);
  if (!mqttClient.connected()) {
      reconnect();
  }
  Serial.flush();
	emsSystem.addChannelToSystem(&emsChannel1);
	emsSystem.addChannelToSystem(&emsChannel2);
	EMSSystem::start();
  //delay(20000);
  printer("Ready!!");
  digitalWrite(13, HIGH);
}

void loop() {
//Checks whether a signal has to be stoped
//if (emsSystem.check() > 0) {
//}
//Put your main code here, to run repeatedly:
//if (!mqttClient.connected()) {
//    reconnect();
//}
  if (!mqttClient.loop()) {
     digitalWrite(13, LOW);
     Serial.println("Client disconnected");
     reconnect();
     digitalWrite(13, HIGH);
  }
  //mqttClient.loop();
  buttonState1 = digitalRead(buttonPin1);
  if(buttonState1==1) {
     Serial.println("Button 1 pressed");
     int duration=1000;
     setIntensity('1',100);
     doCommand('1');
     delay(duration);
     doCommand('1');
  }
  buttonState2 = digitalRead(buttonPin2);
  if(buttonState2==1) {
     Serial.println("Button 2 pressed");
     int duration=1000;
     setIntensity('2',100);
     doCommand('2');
     delay(duration);
     doCommand('2');
  }
}

//print any message received for subscribed topic
void callback(char* topic, byte* payload, unsigned int length) {
  String channel_str = "";
  String duration_str = "";
  String intensity_str = "";
  String payload_str = "";
  int duration=0;
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i=0;i<length;i++) {
    Serial.print((char)payload[i]);
    payload_str += (char)payload[i];
  }
  Serial.println("");
  if (payload_str.charAt(0) == 'C') {
    int IndexOfT = payload_str.lastIndexOf('T');
    int IndexOfI = payload_str.lastIndexOf('I');
    channel_str = payload_str.substring(1, IndexOfT);
    intensity_str = payload_str.substring(IndexOfI+1, payload_str.length());
    duration_str = payload_str.substring(IndexOfT+1, IndexOfI);
    printer("EMS_CMD: Channel "+ channel_str + ", "+ duration_str + " msec, " + intensity_str +" %");
    duration=duration_str.toInt();
    setIntensity(channel_str[0], intensity_str.toInt());
    doCommand(channel_str[0]);
    delay(duration);
    doCommand(channel_str[0]);
  }
}

void printWifiData()
{
  // print your WiFi shield's IP address
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print your MAC address
  byte mac[6];
  WiFi.macAddress(mac);
  Serial.print("MAC address: ");
  for (int i=0;i<6;i++) {
    Serial.print((char)mac[6-i]);
    Serial.print(":");
  }
//sprintf(buf, "%02X:%02X:%02X:%02X:%02X:%02X", mac[5], mac[4], mac[3], mac[2], mac[1], mac[0]);
  Serial.println("");
}

void reconnect() {
  // Loop until we're reconnected
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect, just a name to identify the client
    if (mqttClient.connect(mqttClient_name)) {
      mqttClient.publish("ems","hello world");
      mqttClient.subscribe("ems");
      Serial.print("Connected to MQTT Broker as ");
      Serial.println(mqttClient_name);
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}  

int setIntensity(char ch, int setValue) {
  int getValue;
  setValue=255-setValue*2.55;
  if (ch == '1'){  
    digitalPot.setPosition(1, setValue);
    getValue=digitalPot.getPosition(1);
  } else if (ch == '2') {
    digitalPot.setPosition(3, setValue);
    getValue=digitalPot.getPosition(3);
  }
  return getValue;
}

void doCommand(char c) {
  char buffer[25];
  if (c == '1') {
    if (emsChannel1.isActivated()) {
      emsChannel1.deactivate();
      strcpy_P(buffer, (char*)pgm_read_word(&(string_table_outputs[1])));
      printer(buffer); //"EMS: Channel 1 inactive"
    } else {
      emsChannel1.activate();
      strcpy_P(buffer, (char*)pgm_read_word(&(string_table_outputs[0])));
      printer(buffer); //"EMS: Channel 1x active"
    }
  } else if (c == '2') {
    if (emsChannel2.isActivated()) {
      emsChannel2.deactivate();
      strcpy_P(buffer, (char*)pgm_read_word(&(string_table_outputs[3])));
      printer(buffer); //"EMS: Channel 2 inactive"
    } else {
      emsChannel2.activate();
      strcpy_P(buffer, (char*)pgm_read_word(&(string_table_outputs[2])));
      printer(buffer);  //"EMS: Channel 2 inactive"
    }
  }else  printer("ERROR: SINGLE-CHAR Command Unknown");
}
