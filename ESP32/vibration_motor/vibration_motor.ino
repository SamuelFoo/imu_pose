const int motorPin = 5; // Digital pin connected to the vibration motor

void setup() {
  pinMode(motorPin, OUTPUT); // Set the pin as an output
  Serial.begin(115200); // Initialize serial communication
}

void loop() {
  if (Serial.available() > 0) {
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
  }
}
