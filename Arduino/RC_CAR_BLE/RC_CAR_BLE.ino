#include <SoftwareSerial.h>

SoftwareSerial softSerial(11, 12); // RX | TX

#define   BAUDRATE_BLE       57600
#define   BAUDRATE_soft      9600
#define   Theshold_min       60
#define   Theshold_max       80
#define   Theshold_end       120
#define   EEG_AVG            60
#define   LED1               3
#define   Button             2    //push Button
#define   STBY               7    //Motor standby
//Motor A
#define   PWMA               10   //Speed control 
#define   AIN1               8    //Direction
#define   AIN2               9    //Direction
//Motor B
#define   PWMB               4    //Speed control
#define   BIN1               6    //Direction
#define   BIN2               5    //Direction

byte checksum = 0, generatedchecksum = 0;
unsigned long payloadDataS[5]  = {0};
unsigned long payloadDataB[32] = {0};
unsigned long Avg_Raw, Temp, Temp_Avg;
unsigned int  Raw_data, Raw_EEG, Poorquality, Attention, Plength, On_Flag = 0, Off_Flag = 1, EyeBlink = 0;
unsigned int  Attn_Temp, Att_Avg, Attn_On_Flag = 1, Attn_Off_Flag = 0;
unsigned int  j, k = 0, n = 0;
unsigned int  EyeFlag1 = 0, EyeFlag2 = 0, EyeFlag3 = 0, Sel_Device = 0;
int wheel_speed;

void setup() {
  Serial.begin(BAUDRATE_BLE);
  softSerial.begin(BAUDRATE_soft);
  softSerial.println("Start");

  pinMode(Button, OUTPUT);
  pinMode(LED1, OUTPUT);

  //For wheel_PWMA, PWMB
  pinMode(STBY, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
}

byte ReadOneByte() {
  int ByteRead;
  while (!Serial.available());
  ByteRead = Serial.read();
  return ByteRead;
}

void loop() {
  if (ReadOneByte() == 170) {      // AA 1 st Sync data
    if (ReadOneByte() == 170) {     // AA 2 st Sync data
      Plength = ReadOneByte();
      if (Plength == 32) {  // Big Packet
        Big_Packet(Plength);
      } else if (Plength == 4) { // Small Packet
        Raw_EEG = Small_Packet(Plength);
        softSerial.println(Raw_EEG);    // Print Raw data to soft serial
        if (j < 512) {
          Temp += Raw_EEG;
          j++;
        } else {
          Avg_Raw = Temp / 512;
          softSerial.print("Rawdata :");   // Print Raw data to soft serial every one second
          softSerial.println(Avg_Raw);

          // something 구동 함수
          run_something(Avg_Raw);

          j = 0;
          Temp = 0;
        }
      }
    }
  }
}

void run_something(int data) {
  if (Theshold_max >= data) { //60~80 (Theshold_min < data) && (
    digitalWrite(LED1, HIGH);
    wheel_speed = data * 6;
    if (digitalRead(Button) == HIGH) {
      run_wheel(1, 160 , 1); //motor 2, full speed, left=1 //255-130
      run_wheel(2, 130 , 1); //motor 2, full speed, left=1
    } else {
      stop_all_wheel();
    }
  } else if ((Theshold_max < data) && (Theshold_end >= data)) {//80~100
    digitalWrite(LED1, HIGH);
    wheel_speed = 100;
    if (digitalRead(Button) == HIGH) { //오른쪽 왼쪽 같은 speed로 구동
      run_wheel(1, 160 , 0); //motor 2, full speed, left=1
      run_wheel(2, 130 , 0); //motor 2, full speed, left=1 130 이상 speed에서 동작
    } else {
      stop_all_wheel();
    }
  } else {
    digitalWrite(LED1, LOW);
    stop_all_wheel();
  }
}

void Big_Packet(byte data) {
  generatedchecksum = 0;
  for (int i = 0; i < data; i++)    {
    payloadDataB[i]     = ReadOneByte();      //Read payload into memory
    generatedchecksum  += payloadDataB[i] ;
  }
  generatedchecksum = 255 - generatedchecksum;
  checksum  = ReadOneByte();
  if (checksum == generatedchecksum)  {     // Varify Checksum
    Poorquality = payloadDataB[1];
    Attention   = payloadDataB[29];
  }
}

unsigned long Small_Packet (byte data) {
  generatedchecksum = 0;
  for (int i = 0; i < data; i++)    {
    payloadDataS[i]     = ReadOneByte();      //Read payload into memory
    generatedchecksum  += payloadDataS[i] ;
  }
  generatedchecksum = 255 - generatedchecksum;
  checksum  = ReadOneByte();
  if (checksum == generatedchecksum) {      // Varify Checksum
    Raw_data  = ((payloadDataS[2] << 8) | payloadDataS[3]);
    if (Raw_data & 0xF000) {
      Raw_data = (((~Raw_data) & 0xFFF) + 1);
    } else {
      Raw_data = (Raw_data & 0xFFF);
    }
    return Raw_data;
  }
}

void run_wheel(int motor, int speed, int direction) {
  digitalWrite(STBY, HIGH); //disable standby

  boolean inPin1 = LOW;
  boolean inPin2 = HIGH;

  if (direction == 1) {
    inPin1 = HIGH;
    inPin2 = LOW;
  } else {
    inPin1 = LOW;
    inPin2 = HIGH;
  }

  if (motor == 1) {
    digitalWrite(AIN1, inPin1);
    digitalWrite(AIN2, inPin2);
    analogWrite(PWMA, speed);
  } else {
    digitalWrite(BIN1, inPin1);
    digitalWrite(BIN2, inPin2);
    analogWrite(PWMB, speed);
  }
}

void stop_all_wheel()
{
  digitalWrite(STBY, LOW);
}

