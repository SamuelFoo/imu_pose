#include "BluetoothSerial.h"
#include <Wire.h>
#include "SparkFun_BNO080_Arduino_Library.h"

String BT_DEVICE_NAME = "ESP32-BT-Slave";

BluetoothSerial SerialBT;
BNO080 myIMU;

const int motorPin = 5;
const bool DEBUG = true;

void setup() {
  if (DEBUG) {
    Serial.begin(115200);
  }
  SerialBT.begin(BT_DEVICE_NAME); //Bluetooth device name

  // IMU Setup
  Wire.begin();
  delay(100); //  Wait for BNO to boot
  // Start i2c and BNO080
  Wire.flush();   // Reset I2C
  myIMU.begin(0x4B, Wire);
  Wire.begin(SDA, SCL);
  Wire.setClock(400000); //Increase I2C data rate to 400kHz
  myIMU.enableRotationVector(50); //Send data update every 50ms

  // Vibration Motor Setup
  pinMode(motorPin, OUTPUT);
}

void loop() {
  //Look for reports from the IMU
  if (myIMU.dataAvailable()) {
    float quatI = myIMU.getQuatI();
    float quatJ = myIMU.getQuatJ();
    float quatK = myIMU.getQuatK();
    float quatReal = myIMU.getQuatReal();
    float quatRadianAccuracy = myIMU.getQuatRadianAccuracy();

    SerialBT.print(F("@")); // denotes start of packet
    SerialBT.print(millis());
    SerialBT.print(F(","));
    SerialBT.print(quatI, 2);
    SerialBT.print(F(","));
    SerialBT.print(quatJ, 2);
    SerialBT.print(F(","));
    SerialBT.print(quatK, 2);
    SerialBT.print(F(","));
    SerialBT.print(quatReal, 2);
    SerialBT.print(F(","));
    SerialBT.print(quatRadianAccuracy, 2);
    SerialBT.print(F("@")); // denotes end of packet
    SerialBT.println();

    if (DEBUG) {
      char inputChar = Serial.read();
      if (inputChar == 'o') {
        delay(10); // Small delay for reading the next character
        if (Serial.available() > 0 && Serial.read() == 'k') {
          Serial.println("Triggering vibration with 'ok' command");
          digitalWrite(motorPin, HIGH); // Turn on the vibration motor
          delay(1000); // Vibrate for 1 second
          digitalWrite(motorPin, LOW); // Turn off the vibration motor
        }
      }

      Serial.print(F("@")); // denotes start of packet
      Serial.print(millis());
      Serial.print(F(","));
      Serial.print(quatI, 2);
      Serial.print(F(","));
      Serial.print(quatJ, 2);
      Serial.print(F(","));
      Serial.print(quatK, 2);
      Serial.print(F(","));
      Serial.print(quatReal, 2);
      Serial.print(F(","));
      Serial.print(quatRadianAccuracy, 2);
      Serial.print(F("@")); // denotes end of packet
      Serial.println();
    }
  }
}
