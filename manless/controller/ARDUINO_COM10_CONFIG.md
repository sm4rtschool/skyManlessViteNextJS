# Konfigurasi Arduino COM10 - Gate IN

## Status Arduino
✅ **Arduino terhubung di COM10**

## Konfigurasi yang Sudah Diupdate

### 1. Gate IN Controller (`config_gate_in.py`)
```python
# Arduino/Gate Controller Configuration
ARDUINO_ENABLED = True
ARDUINO_PORT = os.getenv("GATE_IN_ARDUINO_PORT", "COM10")  # Updated to COM10
ARDUINO_BAUDRATE = 9600
GATE_OPEN_DURATION = 10  # seconds
```

### 2. Controller Config (`config.py`)
```python
# Arduino Configuration
ARDUINO_PORT = os.getenv("ARDUINO_PORT", "COM10")  # Updated to COM10
ARDUINO_BAUDRATE = int(os.getenv("ARDUINO_BAUDRATE", "9600"))
GATE_AUTO_CLOSE_DELAY = int(os.getenv("GATE_AUTO_CLOSE_DELAY", "10"))
```

## Environment Variables
Untuk override konfigurasi, set environment variable:
```bash
# Windows PowerShell
$env:GATE_IN_ARDUINO_PORT="COM10"

# Windows CMD
set GATE_IN_ARDUINO_PORT=COM10

# Linux/Mac
export GATE_IN_ARDUINO_PORT=COM10
```

## Testing Arduino Connection

### 1. Jalankan Gate IN Controller
```bash
cd manless/controller
python main_gate_in.py
```

### 2. Expected Output
```
INFO - Starting Gate Masuk Controller...
INFO - Arduino initialized
INFO - Gate Masuk Controller ready!
INFO - Application startup complete.
INFO - Uvicorn running on http://0.0.0.0:8001
```

### 3. Test Arduino Commands
```bash
# Test gate open
curl -X POST http://localhost:8001/gate/open

# Test gate close  
curl -X POST http://localhost:8001/gate/close

# Check Arduino status
curl http://localhost:8001/status/arduino
```

## Arduino Code Requirements

### Expected Arduino Commands
```cpp
// Commands yang harus didukung Arduino
- "GATE_OPEN\n"     -> Response: "GATE_OPENED"
- "GATE_CLOSE\n"    -> Response: "GATE_CLOSED"  
- "STATUS\n"        -> Response: "GATE:CLOSED,SENSORS:OK"
- "LED_RED_ON\n"    -> Response: "LED_OK"
- "BUZZER_500\n"    -> Response: "BUZZER_OK"
- "RESET\n"         -> Response: "OK"
```

### Arduino Serial Settings
```cpp
void setup() {
  Serial.begin(9600);  // Match baudrate
  // Initialize gate control pins
  // Initialize LED pins
  // Initialize buzzer pin
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "GATE_OPEN") {
      openGate();
      Serial.println("GATE_OPENED");
    }
    else if (command == "GATE_CLOSE") {
      closeGate();
      Serial.println("GATE_CLOSED");
    }
    else if (command == "STATUS") {
      Serial.println("GATE:CLOSED,SENSORS:OK");
    }
    // Handle other commands...
  }
}
```

## Troubleshooting

### Arduino Not Detected
```python
# Check available ports
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"{port.device}: {port.description}")
```

### Connection Failed
1. **Check Port**: Pastikan Arduino di COM10
2. **Check Driver**: Install CH340/FTDI driver jika perlu
3. **Check Cable**: Gunakan kabel USB data (bukan charging only)
4. **Check Baudrate**: Pastikan Arduino menggunakan 9600 baud
5. **Check Permissions**: Run sebagai administrator jika perlu

### Serial Monitor Test
Buka Arduino IDE Serial Monitor:
- Port: COM10
- Baud: 9600
- Send: "STATUS"
- Expected: "GATE:CLOSED,SENSORS:OK"

## Frontend Integration

Arduino status akan muncul di:
1. **Gate IN Interface**: `http://localhost:5173/?gate=gate_in`
2. **Monitoring Center**: `http://localhost:5173/`

### Status Indicators
- 🟢 **Green**: Arduino connected dan responding
- 🔴 **Red**: Arduino disconnected atau error
- 🟡 **Yellow**: Arduino connected tapi ada warning

## Next Steps

1. ✅ **Arduino Config Updated** - COM10 configured
2. 🔄 **Test Connection** - Run controller dan test
3. 📋 **Upload Arduino Code** - Upload sketch yang sesuai
4. 🧪 **Test Commands** - Test gate open/close
5. 🖥️ **Frontend Test** - Verify status di frontend

## Hardware Setup Checklist

- [ ] Arduino terhubung di COM10
- [ ] Arduino sketch uploaded dengan serial commands
- [ ] Gate control hardware terhubung ke Arduino
- [ ] LED indicators terhubung (optional)
- [ ] Buzzer terhubung (optional)
- [ ] Power supply adequate untuk gate motor
- [ ] Safety switches installed

Status: ✅ **ARDUINO COM10 CONFIGURED** 