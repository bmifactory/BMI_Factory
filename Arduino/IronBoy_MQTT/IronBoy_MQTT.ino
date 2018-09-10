/**
 * 
 */ 

#include <Wire.h>
#include <WiFiEsp.h>
#include <WiFiEspClient.h>
#include <SoftwareSerial.h>
#include <PubSubClient.h>
#include <IronBoyController.h>

#define SSID_name "bmi-net"
#define SSID_pass "12345678"
#define mqttClient_name "IronBoy0"
#define mqttTopic "robot"

#define DELAY_TIME        2000
#define LED_ALL_BRIGHT    255
#define LED_RED_BRIGHT    255
#define LED_GREEN_BRIGHT  255
#define LED_BLUE_BRIGHT   255
#define LED_OFF           0
#define MOTION_LIBARY_STAND         106
#define MOTION_LIBARY_SIT_DOWN      107
#define MOTION_LIBARY_SIDE_KICK_L   113
#define MOTION_LIBARY_WAVE          133
#define MOTION_LIBARY_HEART         89
#define MOTION_LIBARY_BOW_DOWN      116
#define MOTION_LIBARY_WING_FLAP_L   120
#define MOTION_LIBARY_CELEBRATE_THE_VICTORY       115

IPAddress mqttBrokerIP(192, 168, 0, 8);
char ssid[] = SSID_name;       // your network SSID (name)
char pass[] = SSID_pass;       // your network password
int status = WL_IDLE_STATUS;   // the Wifi radio's status

//helper print function that handles the DEBUG_ON flag automatically
void printer(String msg, boolean force = false) {
    Serial.println(msg);
}

//Initialization of control objects
WiFiEspClient espClient;
PubSubClient mqttClient(espClient);
SoftwareSerial softSerial(8,9); // RX, TX
IronBoyController IronBoyControl(ROBOT_CONTROLLER_COM_PORT_UART);

IBC_Motion_Status_t m_status;

void setup() {
  delay(DELAY_TIME);
  IronBoyControl.begin();  
  delay(DELAY_TIME);
  m_status = IronBoyControl.Motion.Play(MOTION_LIBARY_STAND);
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
  //printWifiData();
  
  //connect to MQTT Broker
  mqttClient.setServer(mqttBrokerIP, 1883);
  mqttClient.setCallback(callback);
  delay(100);
  if (!mqttClient.connected()) {
      reconnect();
  }
  Serial.flush();

  // put your setup code here, to run once:
  printer("Ready!!");
  delay(DELAY_TIME);
  m_status = IronBoyControl.Motion.Play(MOTION_LIBARY_BOW_DOWN);
  delay(DELAY_TIME);
}

void loop() {
  if (!mqttClient.loop()) {
     Serial.println("Client disconnected");
     reconnect();
  }
  //mqttClient.loop();
}

//print any message received for subscribed topic
void callback(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  int i=0;
  while (i<length) msg += (char)payload[i++];
  if (msg=="red") {
    Serial.println(msg);
    IronBoyControl.Led.ChestFullColor(LED_ALL_BRIGHT, LED_RED_BRIGHT, LED_OFF,  LED_OFF);
    delay(DELAY_TIME);
  }
  else if (msg=="green") {
    Serial.println(msg);
    IronBoyControl.Led.ChestFullColor(LED_ALL_BRIGHT, LED_OFF,  LED_GREEN_BRIGHT, LED_OFF);
    delay(DELAY_TIME);
  }
  else if (msg=="blue") {
    Serial.println(msg);
    IronBoyControl.Led.ChestFullColor(LED_ALL_BRIGHT, LED_OFF,  LED_OFF,  LED_BLUE_BRIGHT);
    delay(DELAY_TIME);
  }
  else if (msg=="off") {
    Serial.println(msg);
    IronBoyControl.Led.ChestFullColor(LED_ALL_BRIGHT, LED_OFF,  LED_OFF,  LED_OFF);
    delay(DELAY_TIME);
  }
  else if (msg=="stand") {
    Serial.println(msg);
    m_status = IronBoyControl.Motion.Play(MOTION_LIBARY_STAND);
    delay(DELAY_TIME);
  }
  else if (msg=="sit-down") {
    Serial.println(msg);
    m_status = IronBoyControl.Motion.Play(MOTION_LIBARY_SIT_DOWN);
    delay(DELAY_TIME);
  }
  else if (msg=="wave") {
    Serial.println(msg);
    m_status = IronBoyControl.Motion.Play(MOTION_LIBARY_WAVE);
    delay(DELAY_TIME);
  }
  else if (msg=="heart") {
    Serial.println(msg);
    m_status = IronBoyControl.Motion.Play(MOTION_LIBARY_HEART);
    delay(DELAY_TIME);
  }
  else if (msg=="side-kick") {
    Serial.println(msg);
    m_status = IronBoyControl.Motion.Play(MOTION_LIBARY_SIDE_KICK_L);
    delay(DELAY_TIME);
  }
  else if (msg=="bow") {
    Serial.println(msg);
    m_status = IronBoyControl.Motion.Play(MOTION_LIBARY_BOW_DOWN);
    delay(DELAY_TIME);
  }
  else if (msg=="victory") {
    Serial.println(msg);
    m_status = IronBoyControl.Motion.Play(MOTION_LIBARY_CELEBRATE_THE_VICTORY);
    delay(DELAY_TIME);
  }
  else if (msg=="wing") {
    Serial.println(msg);
    m_status = IronBoyControl.Motion.Play(MOTION_LIBARY_WING_FLAP_L);
    delay(DELAY_TIME);
  }  
  else {
    Serial.println("Wrong message");            
  }
  //Serial.print("Message arrived [");
  //Serial.print(topic);
  //Serial.print("] ");
  //Serial.print(msg);
  //Serial.println("");
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
      //mqttClient.publish("robot","hello world");
      mqttClient.subscribe("robot");
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
