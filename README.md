# ESP32
Likely to be DFRobot's ESP-32-WROOM module

# Python Bluetooth
pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez

# Breadboard Plan
ESP32: a12, j12, j30, b30
BNO080: j1 to i10
Connections:
    Batt VCC to a30
    Batt GND to a25
    f1 to a12 (BNO080 VCC)
    f2 to j12 (BNO080 GND)
    f3 to j14 (BNO080 SDA to ESP32 GPIO22)
    f4 to j17 (BNO080 SCL to ESP32 GPIO21)

Battery: 4 1.5V AA Cylindrical Batteries.