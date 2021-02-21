#include <ESP8266HTTPClient.h>

#include "MQ135.h"
#include <ESP8266WiFi.h>
//#include <Arduino_JSON.h>
//#include <HTTPClient.h>
#include <ArduinoJson.h>

#ifndef STASSID
#define STASSID "TP-LINK_1A16"
#define STAPSK  "shakirpro"
#endif

const char* ssid = STASSID;
const char* password = STAPSK;
int mq135 = A0;
int data = 0;
String device_key = "8";

// The certificate is stored in PMEM


// Create an instance of the server
// specify the port to listen on as an argument

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
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

void loop() {
   if (WiFi.status() == WL_CONNECTED) {

  MQ135 gasSensor = MQ135(A0);
  float air_quality = gasSensor.getPPM();
  float ana_read = analogRead(A0);



  StaticJsonBuffer<200> jsonBuffer;
  JsonObject &root = jsonBuffer.createObject();
                  
  root["key"] = device_key;
  root["value"] = ana_read;
  String requestBody;
  char json_str[100];
   root.prettyPrintTo(json_str, sizeof(json_str));
    HTTPClient http;
    http.begin("http://192.168.0.100:5000/v1/insert");
  
  int httpCode = http.POST(json_str);
  String payload = http.getString();                  //Get the response payload
 
    Serial.println(httpCode);   //Print HTTP return code
    Serial.println(payload);    //Print request response payload
 
    http.end();  //Close conne
  Serial.println(ana_read); 
  Serial.println();
   }
   else{
    Serial.println("Error in WiFi connection");
    }
  delay(4000);
  
  
  }
