# 🎮 CONTROLLER APPLICATION
## Manless Parking System - Middleware Controller

Controller adalah aplikasi middleware yang berfungsi sebagai penghubung antara **frontend** dan **backend** dalam sistem parkir manless. Aplikasi ini dirancang untuk diletakkan di **mini PC di dalam tiket dispenser**.

## 🏗️ Arsitektur Sistem

```
Frontend ↔ Controller ↔ Backend
```

- **Frontend**: Antarmuka pengguna (React/Vue)
- **Controller**: Middleware (Python FastAPI) - **APLIKASI INI**
- **Backend**: Data management & WebSocket server (Python FastAPI)

## 🎯 Fungsi Controller

### Hardware Management
- ✅ **Kamera**: Streaming video, capture gambar
- ✅ **Card Reader**: Pembacaan kartu RFID/NFC
- ✅ **Arduino/Gate**: Kontrol gate parkir, LED, buzzer

### Business Logic
- ✅ **Parking Entry**: Validasi kartu, buka gate, capture foto
- ✅ **Parking Exit**: Hitung tarif, proses pembayaran, buka gate
- ✅ **Gate Control**: Kontrol manual gate
- ✅ **System Monitoring**: Status hardware dan sistem

### Communication
- ✅ **Frontend API**: REST API dan WebSocket
- ✅ **Backend Client**: Komunikasi dengan backend server
- ✅ **Hardware Interface**: Serial communication dengan perangkat

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd manless/controller
pip install -r requirements.txt
```

### 2. Configuration
Edit `config.py` atau gunakan environment variables:

```bash
# Backend Configuration
export BACKEND_HOST=localhost
export BACKEND_PORT=8000

# Hardware Configuration
export CAMERA_SOURCE=0
export CARD_READER_PORT=COM3
export ARDUINO_PORT=COM4

# Simulation Mode (untuk testing tanpa hardware)
export SIMULATE_HARDWARE=True
```

### 3. Run Controller
```bash
python run_controller.py
```

Controller akan berjalan di: `http://localhost:8001`

## 📡 API Endpoints

### WebSocket Endpoints
- `ws://localhost:8001/ws` - Main WebSocket untuk frontend
- `ws://localhost:8001/ws/camera` - Camera streaming WebSocket

### REST API Endpoints
- `GET /api/status` - System status
- `POST /api/parking/entry` - Process parking entry
- `POST /api/parking/exit` - Process parking exit
- `POST /api/gate/control` - Manual gate control
- `POST /api/camera/control` - Camera control
- `GET /api/camera/stream` - HTTP camera stream

## 🔧 Hardware Configuration

### Camera
```python
CAMERA_SOURCE = "0"  # Webcam index atau IP camera URL
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30
```

### Card Reader
```python
CARD_READER_PORT = "COM3"  # Serial port
CARD_READER_BAUDRATE = 9600
CARD_READER_TIMEOUT = 10
```

### Arduino
```python
ARDUINO_PORT = "COM4"  # Serial port
ARDUINO_BAUDRATE = 9600
GATE_AUTO_CLOSE_DELAY = 10  # seconds
```

## 🎮 WebSocket Message Types

### From Frontend to Controller
```javascript
// Parking Entry
{
  "type": "parking_entry",
  "payload": {
    "card_id": "CARD001"
  }
}

// Gate Control
{
  "type": "gate_control",
  "payload": {
    "action": "open",
    "duration": 10
  }
}

// Camera Control
{
  "type": "camera_control",
  "payload": {
    "command": "capture_image"
  }
}
```

### From Controller to Frontend
```javascript
// Entry Approved
{
  "type": "entry_approved",
  "payload": {
    "card_id": "CARD001",
    "image_path": "captures/capture_20241223_101530.jpg",
    "timestamp": "2024-12-23T10:15:30"
  }
}

// Gate Status
{
  "type": "gate_status",
  "payload": {
    "action": "open",
    "result": {"status": "success"},
    "timestamp": "2024-12-23T10:15:30"
  }
}

// System Status
{
  "type": "system_status",
  "payload": {
    "controller": {
      "camera": {"connected": true},
      "card_reader": {"connected": true},
      "arduino": {"connected": true}
    },
    "backend": {"status": "connected"}
  }
}
```

## 🔄 Workflow Parkir

### Entry Process
1. User tap kartu di card reader
2. Controller validasi kartu dengan backend
3. Jika valid: buka gate, capture foto, log entry
4. Jika invalid: tolak masuk, tampilkan pesan error

### Exit Process
1. User tap kartu di card reader
2. Controller ambil data sesi parkir dari backend
3. Hitung tarif berdasarkan durasi
4. Proses pembayaran
5. Buka gate, capture foto, log exit

## 🛠️ Development

### Project Structure
```
controller/
├── main.py              # FastAPI application
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── run_controller.py   # Run script
├── hardware/          # Hardware controllers
│   ├── camera.py      # Camera controller
│   ├── card_reader.py # Card reader controller
│   └── arduino.py     # Arduino controller
├── captures/          # Captured images
└── logs/             # Application logs
```

### Environment Modes
- **Development**: `CONTROLLER_ENV=development` (dengan simulasi)
- **Production**: `CONTROLLER_ENV=production` (hardware nyata)
- **Test**: `CONTROLLER_ENV=test` (untuk testing)

### Hardware Simulation
Untuk development tanpa hardware nyata:
```bash
export SIMULATE_HARDWARE=True
```

Mode simulasi akan:
- Simulasi pembacaan kartu
- Simulasi kontrol gate
- Gunakan webcam untuk kamera
- Generate data sensor dummy

## 🔧 Troubleshooting

### Hardware Issues
1. **Camera tidak terdeteksi**
   - Cek CAMERA_SOURCE
   - Pastikan kamera tidak digunakan aplikasi lain
   - Set SIMULATE_HARDWARE=True untuk testing

2. **Serial port error**
   - Cek COM port yang tersedia
   - Pastikan driver serial terinstall
   - Cek permission port serial

3. **Backend connection error**
   - Pastikan backend server running
   - Cek BACKEND_HOST dan BACKEND_PORT
   - Cek network connectivity

### Logging
Log file tersimpan di: `logs/controller.log`

Set log level:
```bash
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## 🔐 Security

- CORS dikonfigurasi untuk frontend origins
- Serial communication dengan timeout
- Error handling untuk hardware failures
- Input validation untuk semua API endpoints

## 📝 Notes

- Controller berjalan di port **8001** (berbeda dari backend port 8000)
- Semua komunikasi dengan backend menggunakan HTTP API
- Hardware controllers mendukung mode simulasi untuk development
- Images tersimpan lokal di folder `captures/`
- Support untuk multiple camera sources (webcam, IP camera)

## 🚀 Deployment

Untuk deployment di mini PC:
1. Install Python dan dependencies
2. Set environment variables
3. Connect hardware (camera, card reader, Arduino)
4. Run controller dengan production config
5. Monitor logs untuk troubleshooting

---

**🎯 Tujuan**: Controller berfungsi sebagai otak lokal yang menangani hardware dan business logic, sementara backend fokus pada data management dan komunikasi central. 