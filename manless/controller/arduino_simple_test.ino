/*
  Arduino Simple Test - Minimal dan Responsif
  Hanya untuk test komunikasi serial
*/

void setup() {
  Serial.begin(9600);
  delay(1000);  // Tunggu serial siap
  Serial.println("Arduino Ready");
  Serial.flush();
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();
    
    if (command == "PING") {
      Serial.println("PONG");
    }
    else if (command == "STATUS") {
      Serial.println("GATE:CLOSED,VEHICLE:0,POSITION:0,SENSORS:OK");
    }
    else if (command == "LED_RED_ON") {
      Serial.println("LED_OK");
    }
    else if (command == "LED_RED_OFF") {
      Serial.println("LED_OK");
    }
    else if (command == "LED_GREEN_ON") {
      Serial.println("LED_OK");
    }
    else if (command == "LED_GREEN_OFF") {
      Serial.println("LED_OK");
    }
    else if (command == "LED_BLUE_ON") {
      Serial.println("LED_OK");
    }
    else if (command == "LED_BLUE_OFF") {
      Serial.println("LED_OK");
    }
    else if (command.startsWith("BUZZER_")) {
      Serial.println("BUZZER_OK");
    }
    else if (command == "RESET") {
      Serial.println("SYSTEM_RESET");
    }
    else if (command == "EMERGENCY_STOP") {
      Serial.println("EMERGENCY_STOP_ACTIVATED");
    }
    else if (command == "GATE_OPEN") {
      Serial.println("GATE_OPENING");
    }
    else if (command == "GATE_CLOSE") {
      Serial.println("GATE_CLOSING");
    }
    else {
      Serial.println("UNKNOWN_COMMAND");
    }
  }
  
  delay(10);  // Small delay
} 