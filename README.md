# ESP32
Likely to be DFRobot's ESP-32-WROOM module  

# Python Bluetooth
pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez  

# Breadboard Plan
    ESP32: b12, i12, i30, b30  
    BNO080: j1 to j10  

    Connections:  
    Batt VCC to a30  
    Batt GND to a25  
    
    f1 to a12 (BNO080 VCC)  
    f2 to j12 (BNO080 GND)  
    f3 to j14 (BNO080 SDA to ESP32 GPIO22)  
    f4 to j17 (BNO080 SCL to ESP32 GPIO21)  

    j18 to Vibration Motor GND (ESP32 GND to Vibration Motor GND)  
    j21 to Vibration Motor IN (ESP32 GPIO5 to Vibration Motor IN)  
    g1 to Vibration Motor VCC (ESP32 3.3V to Vibration Motor VCC)  

![esp32-devkitC-v4-pinout](https://github.com/SamuelFoo/imu_pose/assets/26446878/9ae7118c-93e6-4553-b023-82b782f59cf9)

Battery: 4 1.5V AA Cylindrical Batteries.

# Use IMU_BT_Test
