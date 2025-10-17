# 🏢 Sistem Parkir Manless - Arsitektur Terpusat

## 📋 Deskripsi

Sistem parkir manless dengan arsitektur **TERPUSAT** menggunakan Backend sebagai **Central Hub** yang mengkoordinasi multiple gate controllers. Arsitektur ini memungkinkan pengelolaan yang lebih efisien dan koordinasi yang lebih baik antar gate.

## 🏗️ Arsitektur Sistem

```
Frontend (5173) ←→ Backend Central Hub (8000) ←→ Gate Controllers
                                              ├── Gate IN (8001)
                                              └── Gate OUT (8002)
```

### Komponen Utama:

1. **Frontend (React)** - Port 5173
   - User Interface untuk monitoring dan kontrol
   - WebSocket connection ke Central Hub
   - Real-time updates dari semua gate

2. **Backend Central Hub (FastAPI)** - Port 8000
   - Koordinasi semua gate controllers
   - Session management terpusat
   - Event broadcasting
   - API Gateway untuk frontend

3. **Gate IN Controller (FastAPI)** - Port 8001
   - Entry processing
   - Card validation
   - Camera control
   - Hardware gate IN

4. **Gate OUT Controller (FastAPI)** - Port 8002
   - Exit processing
   - Payment processing
   - Receipt printing
   - Hardware gate OUT

## 🔧 Keunggulan Arsitektur Terpusat

### ✅ **Advantages:**
- **Koordinasi Terpusat**: Semua gate dikoordinasi oleh satu central hub
- **Session Management**: Tracking kendaraan yang sedang parkir secara terpusat
- **Event Broadcasting**: Real-time updates ke semua clients
- **Scalability**: Mudah menambah gate baru
- **Monitoring**: Comprehensive system monitoring
- **Debugging**: Easier debugging dengan centralized logging

### 🔄 **Flow Data:**
1. Frontend → Backend (Central Hub)
2. Backend → Gate Controller yang sesuai
3. Gate Controller → Hardware
4. Response: Hardware → Gate Controller → Backend → Frontend

## 🚀 Cara Menjalankan Sistem

### Windows (Batch Script):
```bash
# Jalankan script batch
start_centralized_system.bat
```

### Manual (Step by Step):

#### 1. Backend Central Hub (Port 8000)
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Gate IN Controller (Port 8001)
```bash
cd controller
python main_gate_in.py
```

#### 3. Gate OUT Controller (Port 8002)
```bash
cd controller
python main_gate_out.py
```

#### 4. Frontend (Port 5173)
```bash
cd frontend
npm run dev
```

## 📡 API Communication

### Frontend → Backend Central Hub

#### WebSocket Messages:
```javascript
// Parking entry request
{
  "type": "parking_entry",
  "payload": {
    "card_id": "CARD_001",
    "license_plate": "B1234XYZ"
  }
}

// Parking exit request
{
  "type": "parking_exit", 
  "payload": {
    "card_id": "CARD_001",
    "payment_method": "card"
  }
}

// Gate control
{
  "type": "gate_control",
  "payload": {
    "gate_id": "gate_in",
    "action": "open",
    "duration": 10
  }
}
```

#### HTTP API Endpoints:
- `GET /api/status` - System status
- `GET /api/parking/capacity` - Parking capacity
- `POST /api/parking/entry` - Process entry
- `POST /api/parking/exit` - Process exit
- `POST /api/gate/control/{gate_id}` - Gate control
- `GET /api/camera/stream/{gate_id}` - Camera stream
- `POST /api/camera/capture/{gate_id}` - Capture image
- `GET /api/logs` - System logs
- `POST /api/emergency/force-exit` - Emergency exit

### Backend → Gate Controllers

#### HTTP Requests:
- `GET /api/status` - Health check
- `POST /api/parking/entry` - Entry processing
- `POST /api/parking/exit` - Exit processing
- `POST /api/gate/control` - Gate control
- `POST /api/camera/control` - Camera control

## 🗃️ Database Schema

Database tetap sama dengan sistem sebelumnya, menggunakan MySQL dengan tabel:
- `cards` - Kartu parkir
- `vehicles` - Data kendaraan
- `parking_slots` - Slot parkir
- `parking_log` - Log parkir
- `payments` - Transaksi pembayaran
- `system_alerts` - Alert sistem
- `system_config` - Konfigurasi sistem

## 📁 Struktur File

```
manless/
├── backend/                    # Backend Central Hub
│   ├── app/
│   │   ├── main.py            # FastAPI app dengan gate coordinator
│   │   │   ├── api/routes.py      # API routes
│   │   │   └── database/          # Database models
│   │   └── gate_coordinator.py    # Gate coordinator logic
│   └── gate_coordinator.py    # Gate coordinator logic
│
├── controller/                 # Gate Controllers
│   ├── config_gate_in.py      # Konfigurasi Gate IN
│   ├── config_gate_out.py     # Konfigurasi Gate OUT
│   ├── main_gate_in.py        # Gate IN Controller
│   ├── main_gate_out.py       # Gate OUT Controller
│   └── hardware/              # Hardware controllers
│
├── frontend/                   # Frontend React
│   ├── src/
│   │   ├── services/
│   │   │   ├── api.js         # API service (updated)
│   │   │   └── websocket.js   # WebSocket service (updated)
│   │   └── components/        # React components
│   └── package.json
│
├── start_centralized_system.bat  # Windows batch script
├── start_centralized_system.py   # Python script
└── README_ARSITEKTUR_TERPUSAT.md # Dokumentasi ini
```

## ⚙️ Konfigurasi

### Environment Variables (.env):
```bash
# Database
DATABASE_URL=mysql://parkir:parkir123@localhost/parkir_db

# Simulation Mode
SIMULATION_MODE=true

# Hardware Ports
GATE_IN_CAMERA_SOURCE=0
GATE_IN_CARD_READER_PORT=COM3
GATE_IN_ARDUINO_PORT=COM4

GATE_OUT_CAMERA_SOURCE=1
GATE_OUT_CARD_READER_PORT=COM5
GATE_OUT_ARDUINO_PORT=COM6

# Payment Hardware
CASH_DISPENSER_PORT=COM7
CARD_TERMINAL_PORT=COM8
RECEIPT_PRINTER_PORT=COM9

# Alerts
ALERT_EMAIL=admin@parkir.com
ALERT_WEBHOOK=https://hooks.slack.com/...
```

## 🔍 Monitoring & Debugging

### System Status:
```javascript
// Get comprehensive system status
const status = await apiService.getSystemStatus()
console.log(status)

/*
{
  "coordinator": {
    "status": "online",
    "active_sessions": 5
  },
  "gates": {
    "gate_in": {
      "status": "online",
      "controller_status": {...}
    },
    "gate_out": {
      "status": "online", 
      "controller_status": {...}
    }
  },
  "active_sessions": {
    "CARD_001": {
      "card_id": "CARD_001",
      "entry_time": "2024-01-01T10:00:00",
      "status": "parked"
    }
  }
}
*/
```

### Real-time Events:
```javascript
// Listen to all parking events
wsService.on('parking_event', (data) => {
  console.log('Parking event:', data)
  // { event: 'entry', gate: 'gate_in', result: {...} }
})

// Listen to specific gate events
wsService.on('gate_in_event', (data) => {
  console.log('Gate IN event:', data)
})

wsService.on('gate_out_event', (data) => {
  console.log('Gate OUT event:', data)
})
```

## 🆘 Emergency Features

### Force Exit Session:
```javascript
// Force exit untuk emergency
await apiService.forceExitSession('CARD_001', 'emergency')
```

### Manual Gate Control:
```javascript
// Buka gate manual
await apiService.openGateIn(15)  // 15 seconds
await apiService.openGateOut(15)

// Tutup gate manual
await apiService.closeGateIn()
await apiService.closeGateOut()

// Kontrol semua gate sekaligus
await apiService.openAllGates(10)
await apiService.closeAllGates()
```

## 🧪 Testing & Simulation

### Simulasi Parkir:
```javascript
// Simulasi kendaraan masuk
await wsService.simulateVehicleEntry('TEST_CARD_001', 'B1234XYZ')

// Simulasi kendaraan keluar
await wsService.simulateVehicleExit('TEST_CARD_001')

// Test gate control
await wsService.controlGate('gate_in', 'open', 10)
```

## 📊 Performance & Scaling

### Current Capacity:
- **Concurrent Connections**: 100 per controller
- **Request Timeout**: 10 seconds
- **WebSocket Reconnection**: 5 attempts
- **Database Connection Pooling**: 10 connections

### Scaling Options:
1. **Horizontal**: Tambah gate controllers baru
2. **Vertical**: Increase server resources
3. **Load Balancing**: Multiple backend instances
4. **Database Sharding**: Separate by location/time

## 🔐 Security Features

- **CORS Protection**: Configured origins
- **Input Validation**: Pydantic models
- **Error Handling**: Graceful error responses
- **Session Management**: Secure session tracking
- **Hardware Isolation**: Separate controller per gate

## 📝 Logs & Audit Trail

### Log Levels:
- **INFO**: Normal operations
- **WARN**: Unusual but handled events
- **ERROR**: System errors
- **DEBUG**: Detailed debugging info

### Log Sources:
- Backend Central Hub: `logs/central_hub.log`
- Gate IN Controller: `logs/gate_in.log`
- Gate OUT Controller: `logs/gate_out.log`

## 🔄 Deployment

### Development:
```bash
# Run with hot reload
start_centralized_system.bat
```

### Production:
```bash
# Use production WSGI server
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000
```

### Docker (Optional):
```dockerfile
# Dockerfile untuk backend
FROM python:3.9
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🎯 Kesimpulan

Arsitektur terpusat memberikan **koordinasi yang lebih baik** antar gate, **monitoring terpusat**, dan **scalability** yang lebih mudah. Sistem ini cocok untuk:

- **Mall/Plaza**: Multiple entry/exit points
- **Perkantoran**: Koordinasi antar blok
- **Perumahan**: Multiple gate access
- **Bandara/Stasiun**: High traffic coordination

Dengan backend sebagai central hub, sistem dapat **mengelola session secara terpusat**, **broadcast events** ke semua clients, dan **koordinasi** antar gate dengan lebih efisien.

---

📞 **Support**: Hubungi tim development untuk bantuan implementasi dan customization. 