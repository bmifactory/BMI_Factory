//라이브러리 설정
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

//와이파이 설정
const char* ssid = "bmi-net"; //무선 공유기 ssid
const char* password = "12345678"; //무선 공유기 비밀번호

//mqtt 설정
#define mqtt_server "192.168.0.8" //mqtt 서버
#define mqtt_port 1883 //mqtt 포트
#define mqtt_user "lee" //mqtt user 아이디
#define mqtt_password "1111" //mqtt password

//클라이언트 설정
WiFiClient espClient;
PubSubClient client(espClient);

//핀 설정
const int analogIn = A0; //analogIn-GPIO A0 핀 연결
const int ledPin = 2; //led-GIPO 4 핀 연결

void setup() {
  //핀 모드 설정
  pinMode(analogIn, INPUT);
  pinMode(ledPin, OUTPUT);

  //시리얼 속도 및 프린터 설정
  Serial.begin(9600);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  //와이파이 시작
  WiFi.begin(ssid, password);

  //와이파이 연결하는 동안 내부led 깜빡이기
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    digitalWrite(ledPin, HIGH);
    delay(500);
    digitalWrite(ledPin, LOW);
    delay(500);
  }

  //와이파이 연결 확인 프린트
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  //mqtt 셋팅
  client.setServer(mqtt_server, mqtt_port); //mqtt 서버 포트 셋팅
}

void loop() {
  int inputValue = analogRead(analogIn); //myo 아날로그 신호를 inputValue 인수에 저장

  //mqtt 연결 될때까지 loop
  if (!client.connected()) { //mqtt 연결 됐을 때
    Serial.print("Attempting MQTT connection...");
    if (client.connect("Myoware1", mqtt_user, mqtt_password)) {
      Serial.println("connected");
      client.subscribe("myo");
    } else { //mqtt 연결에 실패했을 때
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
      return;
    }
  }
  client.loop();

  //신호(inputValue)를 char로 변환
  String data = String(inputValue, DEC);
  int length = data.length();
  char msgBuffer[length];

  //myo값 publish
  if (inputValue > 100) { //myo 신호가 100보다 클 때,
    data.toCharArray(msgBuffer, length + 1);
    Serial.println("AnaloginputValue: ");
    Serial.println(inputValue);
    client.publish("myo", msgBuffer);
    delay(100);
  } else if (inputValue < 20) { //myo 신호가 100보다 작을 때,
    Serial.println("AnaloginputValue: ");
    Serial.println(inputValue);
    client.publish("myo", "low signal");
    delay(100);
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  String msg = "";
  int i = 0;
  while (i < length) msg += (char)payload[i++];
  if (msg == "PUSH") {
    //   digitalWrite(14, (msg == "PUSH" ? LOW : HIGH));
    //   digitalWrite(12, (msg == "LEDON" ? LOW : HIGH));
    //   Serial.println("Send !");
    return;
  } else {
    //   digitalWrite(14, (msg == "LEDON" ? LOW : HIGH));
    //   digitalWrite(12, (msg == "TALK" ? LOW : HIGH));
  }
  Serial.println(msg);
}
