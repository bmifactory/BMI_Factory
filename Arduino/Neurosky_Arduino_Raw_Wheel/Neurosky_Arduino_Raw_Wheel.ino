#include <SoftwareSerial.h>

SoftwareSerial softSerial(11, 12); // RX | TX

#define   BAUDRATE_BLE       57600
#define   BAUDRATE_soft      9600
#define   Theshold           120 
#define   EEG_AVG            60
#define   LED1               3
#define   left_For  7 // assigns pin 7 to variable Left Forward pwm
#define   left_Rev  8 // assigns pin 8 to variable Left Rev pwm
#define   right_For 9 // assigns pin 9 to variable Right Forward pwm
#define   right_Rev 10 // assigns pin 10 to variable Right Rev pwm
#define   button 4 // push button

byte checksum=0,generatedchecksum=0;
unsigned long payloadDataS[5]  = {0}; 
unsigned long payloadDataB[32] = {0}; 
unsigned long Avg_Raw,Temp,Temp_Avg; 
unsigned int  Raw_data,Raw_EEG,Poorquality,Attention,Plength,On_Flag=0,Off_Flag=1,EyeBlink=0; 
unsigned int  Attn_Temp,Att_Avg,Attn_On_Flag=1,Attn_Off_Flag=0;
unsigned int  j,k=0,n=0;
unsigned int  EyeFlag1=0,EyeFlag2=0,EyeFlag3=0,Sel_Device=0; 

void setup() {
  Serial.begin(BAUDRATE_BLE);
  softSerial.begin(BAUDRATE_soft);
  softSerial.println("Start");
  pinMode(LED1, OUTPUT);
  //For wheel   
  pinMode(left_For, OUTPUT); // declares pin 7 as output
  pinMode(left_Rev, OUTPUT); // declares pin 8 as output
  pinMode(right_For, OUTPUT); // declares pin 9 as output
  pinMode(right_Rev, OUTPUT); // declares pin 10 as output
  pinMode(button, OUTPUT); // declares pin 10 as input
}

byte ReadOneByte(){
  int ByteRead;   
  while(!Serial.available());   
  ByteRead = Serial.read();   
  return ByteRead;
}

void loop() {  
  if(ReadOneByte() == 170) {       // AA 1 st Sync data   
    if(ReadOneByte() == 170) {      // AA 2 st Sync data
      Plength = ReadOneByte();       
      if(Plength == 32) {   // Big Packet
        Big_Packet (Plength);       
      } else if(Plength == 4) {  // Small Packet                
        Raw_EEG = Small_Packet (Plength); 
        //softSerial.println(Raw_EEG);    // Print Raw data to soft serial
        if (j<512) { 
          Temp += Raw_EEG;
          j++;
        } else {
          Avg_Raw = Temp/512;   
          softSerial.print("Rawdata :");   // Print Raw data to soft serial every one second
          softSerial.println(Avg_Raw);             
          if(Avg_Raw>Theshold){
            digitalWrite(LED1, HIGH);
            int wheel_speed=255;
            run_left_wheel(0,wheel_speed);
            run_right_wheel(0,wheel_speed);
          } else {
            digitalWrite(LED1, LOW);
            stop_all_wheel();
          }
          if(digitalRead(button)==HIGH) {
            int wheel_speed=255;
            run_left_wheel(0,wheel_speed);
            run_right_wheel(0,wheel_speed);
          } else {
            stop_all_wheel();
          }        
          j=0;             
          Temp=0; 
        }
      }        
    }
  }    
}

void Big_Packet(byte data) {   
  generatedchecksum = 0;   
  for(int i = 0; i < data; i++)    { 
    payloadDataB[i]     = ReadOneByte();      //Read payload into memory
    generatedchecksum  += payloadDataB[i] ;  
  }   
  generatedchecksum = 255 - generatedchecksum;   
  checksum  = ReadOneByte();   
  if(checksum == generatedchecksum)  {      // Varify Checksum
    Poorquality = payloadDataB[1];     
    Attention   = payloadDataB[29];   
  } 
}

unsigned long Small_Packet (byte data) {
  generatedchecksum = 0;  
  for(int i = 0; i < data; i++)    {       
    payloadDataS[i]     = ReadOneByte();      //Read payload into memory
    generatedchecksum  += payloadDataS[i] ; 
  }  
  generatedchecksum = 255 - generatedchecksum;
  checksum  = ReadOneByte();
  if(checksum == generatedchecksum) {       // Varify Checksum 
     Raw_data  = ((payloadDataS[2] <<8)| payloadDataS[3]);
     if(Raw_data&0xF000){
       Raw_data = (((~Raw_data)&0xFFF)+1);
     } else { 
       Raw_data = (Raw_data&0xFFF);
     }
     return Raw_data;
  }     
}

void run_left_wheel(int dir, int wheel_speed)
{
    if(dir==0) {
        analogWrite(left_For, wheel_speed); 
        digitalWrite(left_Rev, LOW);
    } else {
        analogWrite(left_Rev, wheel_speed); 
        digitalWrite(left_For, LOW);       
    }
}

void run_right_wheel(int dir, int wheel_speed)
{
    if(dir==0) {
        analogWrite(right_Rev, wheel_speed); 
        digitalWrite(right_For, LOW);     
    } else {
        analogWrite(right_For, wheel_speed); 
        digitalWrite(right_Rev, LOW);  
    }
}

void stop_all_wheel()
{
    digitalWrite(left_For, LOW); 
    digitalWrite(left_Rev, LOW); 
    digitalWrite(right_For, LOW); 
    digitalWrite(right_Rev, LOW);    
}
