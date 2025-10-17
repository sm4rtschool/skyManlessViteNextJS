/*
  Arduino Gate Controller untuk Sistem Parkir Manless (Versi Debug)
  - Handler serial: STATUS, PING, GATE_OPEN, GATE_CLOSE, LED_xx, BUZZER_xx, RESET, EMERGENCY_STOP
  - Semua perintah serial pasti membalas
  - LED biru akan berkedip tiap loop sebagai indikator loop berjalan
*/

// Pin definitions
#define GATE_MOTOR_PIN 3
#define GATE_DIRECTION_PIN 4
#define LED_RED_PIN 5
#define LED_GREEN_PIN 6
#define LED_BLUE_PIN 7
#define BUZZER_PIN 8
#define VEHICLE_SENSOR_PIN 9
#define GATE_POSITION_SENSOR_PIN 10

// Gate states
enum GateState {
  GATE_CLOSED,
  GATE_OPENING,
  GATE_OPEN,
  GATE_CLOSING,
  GATE_ERROR
};

// Global variables
GateState currentGateState = GATE_CLOSED;
unsigned long gateOperationStartTime = 0;
unsigned long buzzerStartTime = 0;
unsigned long buzzerDuration = 0;
bool buzzerActive = false;
String inputBuffer = "";
unsigned long gateOpenTime = 0;

// Debug LED
unsigned long lastBlink = 0;
bool blueLedState = false;

// Timing constants
const unsigned long GATE_OPERATION_TIME = 3000;
const unsigned long GATE_AUTO_CLOSE_TIME = 10000;

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // Tunggu koneksi serial
  }
  
  // Beri sedikit jeda agar serial siap sepenuhnya
  delay(100); 

  pinMode(GATE_MOTOR_PIN, OUTPUT);
  pinMode(GATE_DIRECTION_PIN, OUTPUT);
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_BLUE_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(VEHICLE_SENSOR_PIN, INPUT_PULLUP);
  pinMode(GATE_POSITION_SENSOR_PIN, INPUT_PULLUP);
  digitalWrite(GATE_MOTOR_PIN, LOW);
  digitalWrite(GATE_DIRECTION_PIN, LOW);
  digitalWrite(LED_RED_PIN, LOW);
  digitalWrite(LED_GREEN_PIN, LOW);
  digitalWrite(LED_BLUE_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  currentGateState = GATE_CLOSED;
  blinkLED(LED_GREEN_PIN, 3);
  Serial.println("Arduino Gate Controller Ready");
}

void loop() {
  // 1. Handle incoming serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    // Menggunakan struktur if-else tunggal yang bersih untuk semua perintah
    if (command == "PING") {
      Serial.println("PONG");
    } else if (command == "STATUS") {
      sendStatus(); // Menggunakan fungsi status yang lebih detail
    } else if (command == "GATE_OPEN") {
      openGate();
      // Respons "GATE_OPENED" akan dikirim oleh state machine saat gerbang benar-benar terbuka
    } else if (command == "GATE_CLOSE") {
      closeGate();
      // Respons "GATE_CLOSED" akan dikirim oleh state machine saat gerbang benar-benar tertutup
    } else if (command == "LED_RED_ON") {
      digitalWrite(LED_RED_PIN, HIGH);
      Serial.println("LED_OK");
    } else if (command == "LED_RED_OFF") {
      digitalWrite(LED_RED_PIN, LOW);
      Serial.println("LED_OK");
    } else if (command == "LED_GREEN_ON") {
      digitalWrite(LED_GREEN_PIN, HIGH);
      Serial.println("LED_OK");
    } else if (command == "LED_GREEN_OFF") {
      digitalWrite(LED_GREEN_PIN, LOW);
      Serial.println("LED_OK");
    } else if (command == "LED_BLUE_ON") {
      digitalWrite(LED_BLUE_PIN, HIGH);
      Serial.println("LED_OK");
    } else if (command == "LED_BLUE_OFF") {
      digitalWrite(LED_BLUE_PIN, LOW);
      Serial.println("LED_OK");
    } else if (command.startsWith("BUZZER_")) {
      int duration = command.substring(7).toInt();
      activateBuzzer(duration);
      Serial.println("BUZZER_OK");
    } else if (command == "RESET") {
      resetSystem();
      Serial.println("SYSTEM_RESET");
    } else if (command == "EMERGENCY_STOP") {
      emergencyStop();
      Serial.println("EMERGENCY_STOP_ACTIVATED");
    } else if (command != "") { // Abaikan perintah kosong
      Serial.println("UNKNOWN_COMMAND");
    }
  }

  // 2. Update state machine dan tugas-tugas loop lainnya
  updateGateStateMachine();
  handleBuzzer();
  checkAutoClose();
  blinkDebugLED();
  
  delay(10); // Delay singkat untuk mencegah loop yang terlalu sibuk
}

void blinkDebugLED() {
  // LED biru kedip tiap 500ms
  if (millis() - lastBlink > 500) {
    blueLedState = !blueLedState;
    digitalWrite(LED_BLUE_PIN, blueLedState ? HIGH : LOW);
    lastBlink = millis();
  }
}

void openGate() {
  if (currentGateState == GATE_CLOSED || currentGateState == GATE_CLOSING) {
    currentGateState = GATE_OPENING;
    gateOperationStartTime = millis();
    digitalWrite(GATE_DIRECTION_PIN, HIGH);
    analogWrite(GATE_MOTOR_PIN, 200);
    digitalWrite(LED_GREEN_PIN, HIGH);
    digitalWrite(LED_RED_PIN, LOW);
  }
}

void closeGate() {
  if (currentGateState == GATE_OPEN || currentGateState == GATE_OPENING) {
    currentGateState = GATE_CLOSING;
    gateOperationStartTime = millis();
    digitalWrite(GATE_DIRECTION_PIN, LOW);
    analogWrite(GATE_MOTOR_PIN, 200);
    digitalWrite(LED_RED_PIN, HIGH);
    digitalWrite(LED_GREEN_PIN, LOW);
  }
}

void updateGateStateMachine() {
  unsigned long currentTime = millis();
  switch (currentGateState) {
    case GATE_OPENING:
      if (currentTime - gateOperationStartTime >= GATE_OPERATION_TIME) {
        analogWrite(GATE_MOTOR_PIN, 0);
        currentGateState = GATE_OPEN;
        gateOpenTime = currentTime;
        digitalWrite(LED_GREEN_PIN, HIGH);
        Serial.println("GATE_OPENED");
      }
      break;
    case GATE_CLOSING:
      if (currentTime - gateOperationStartTime >= GATE_OPERATION_TIME) {
        analogWrite(GATE_MOTOR_PIN, 0);
        currentGateState = GATE_CLOSED;
        digitalWrite(LED_RED_PIN, LOW);
        Serial.println("GATE_CLOSED");
      }
      break;
    case GATE_OPEN:
      break;
    case GATE_CLOSED:
      break;
    case GATE_ERROR:
      analogWrite(GATE_MOTOR_PIN, 0);
      digitalWrite(LED_RED_PIN, HIGH);
      break;
  }
}

void checkAutoClose() {
  if (currentGateState == GATE_OPEN && gateOpenTime > 0) {
    unsigned long currentTime = millis();
    if (currentTime - gateOpenTime >= GATE_AUTO_CLOSE_TIME) {
      bool vehiclePresent = !digitalRead(VEHICLE_SENSOR_PIN);
      if (!vehiclePresent) {
        closeGate();
        gateOpenTime = 0;
      }
    }
  }
}

void sendStatus() {
  String status = "GATE:";
  switch (currentGateState) {
    case GATE_CLOSED: status += "CLOSED"; break;
    case GATE_OPENING: status += "OPENING"; break;
    case GATE_OPEN: status += "OPEN"; break;
    case GATE_CLOSING: status += "CLOSING"; break;
    case GATE_ERROR: status += "ERROR"; break;
  }
  bool vehiclePresent = !digitalRead(VEHICLE_SENSOR_PIN);
  bool gatePositionSensor = !digitalRead(GATE_POSITION_SENSOR_PIN);
  status += ",VEHICLE:" + String(vehiclePresent ? "1" : "0");
  status += ",POSITION:" + String(gatePositionSensor ? "1" : "0");
  status += ",SENSORS:OK";
  Serial.println(status);
}

void activateBuzzer(int duration) {
  buzzerDuration = duration;
  buzzerStartTime = millis();
  buzzerActive = true;
  digitalWrite(BUZZER_PIN, HIGH);
}

void handleBuzzer() {
  if (buzzerActive) {
    unsigned long currentTime = millis();
    if (currentTime - buzzerStartTime >= buzzerDuration) {
      digitalWrite(BUZZER_PIN, LOW);
      buzzerActive = false;
    }
  }
}

void resetSystem() {
  analogWrite(GATE_MOTOR_PIN, 0);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LED_RED_PIN, LOW);
  digitalWrite(LED_GREEN_PIN, LOW);
  digitalWrite(LED_BLUE_PIN, LOW);
  currentGateState = GATE_CLOSED;
  gateOperationStartTime = 0;
  gateOpenTime = 0;
  buzzerActive = false;
  blinkLED(LED_BLUE_PIN, 3);
}

void emergencyStop() {
  analogWrite(GATE_MOTOR_PIN, 0);
  currentGateState = GATE_ERROR;
  digitalWrite(LED_RED_PIN, HIGH);
  digitalWrite(LED_GREEN_PIN, LOW);
  digitalWrite(LED_BLUE_PIN, LOW);
  activateBuzzer(2000);
}

void blinkLED(int pin, int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(pin, HIGH);
    delay(200);
    digitalWrite(pin, LOW);
    delay(200);
  }
}

// Interrupt handlers for sensors (optional)
void vehicleSensorISR() {
  // Handle vehicle detection
  // This can be used for immediate response to vehicle presence
}

void gatePositionISR() {
  // Handle gate position feedback
  // This can be used for precise gate positioning
} 