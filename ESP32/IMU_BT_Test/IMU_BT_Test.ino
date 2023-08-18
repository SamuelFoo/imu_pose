#include "BluetoothSerial.h"
#include <Wire.h>
#include "SparkFun_BNO080_Arduino_Library.h"

String BT_DEVICE_NAME = "ESP32-BT-Slave";

BluetoothSerial SerialBT;
BNO080 myIMU;

void setup() {
  SerialBT.begin(BT_DEVICE_NAME); //Bluetooth device name

  Wire.begin();
  delay(100); //  Wait for BNO to boot
  // Start i2c and BNO080
  Wire.flush();   // Reset I2C
  myIMU.begin(0x4B, Wire);
  Wire.begin(SDA, SCL);

  Wire.setClock(400000); //Increase I2C data rate to 400kHz
  myIMU.enableRotationVector(50); //Send data update every 50ms
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
  }
}
