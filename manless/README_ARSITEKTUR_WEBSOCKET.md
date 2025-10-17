# Arsitektur WebSocket Sistem Parkir Manless

## 🏗️ Arsitektur Baru

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARSITEKTUR WEBSOCKET                     │
└─────────────────────────────────────────────────────────────────┘

    Frontend (React)           Backend (FastAPI)          Controller (Python)
  ┌─────────────────┐       ┌─────────────────────┐       ┌─────────────────┐
  │                 │       │                     │       │                 │
  │   WebSocket     │◄──────┤  WebSocket Server   ├──────►│   WebSocket     │
  │    Client       │       │                     │       │    Client       │
  │                 │       │  Channel Manager:   │       │                 │
  │  - gate_in      │       │  - /ws/gate_in      │       │  Hardware:      │
  │  - gate_out     │       │  - /ws/gate_out     │       │  - Arduino      │
  │  - gate_all     │       │  - /ws/gate_all     │       │  - Camera       │
  │  - admin        │       │  - /ws/admin        │       │  - Card Reader  │
  │                 │       │                     │       │                 │
  └─────────────────┘       │  Controller:        │       └─────────────────┘
                            │  - /ws/controller/  │
                            │    gate_in          │
                            │  - /ws/controller/  │
                            │    gate_out         │
                            └─────────────────────┘
```

## 🔧 Komponen Sistem

### 1. Backend WebSocket Server (`backend/main_websocket.py`)
- **Fungsi**: Hanya untuk komunikasi data dan relay informasi
- **Port**: 8000
- **Endpoints**:
  - Frontend WebSocket:
    - `ws://localhost:8000/ws/gate_in` - Untuk frontend gate masuk
    - `ws://localhost:8000/ws/gate_out` - Untuk frontend gate keluar
    - `ws://localhost:8000/ws/gate_all` - Untuk monitoring semua gate
    - `ws://localhost:8000/ws/admin` - Untuk admin/monitoring
  - Controller WebSocket:
    - `ws://localhost:8000/ws/controller/gate_in` - Dari controller gate masuk
    - `ws://localhost:8000/ws/controller/gate_out` - Dari controller gate keluar

### 2. Controller WebSocket Client (`controller/main_websocket.py`)
- **Fungsi**: Menangani hardware dan mengirim data realtime ke backend
- **Peran**: WebSocket Client yang terhubung ke backend
- **Hardware yang dikelola**:
  - Arduino (kontrol gate)
  - Camera (capture gambar)
  - Card Reader (baca kartu parkir)

### 3. Frontend WebSocket Client (`frontend/src/services/websocketNew.js`)
- **Fungsi**: Menampilkan data realtime dari controller
- **Peran**: WebSocket Client yang menerima data dari backend
- **Channel yang tersedia**:
  - `gate_in` - Data khusus gate masuk
  - `gate_out` - Data khusus gate keluar
  - `gate_all` - Data dari semua gate
  - `admin` - Data untuk admin/monitoring

## 🚀 Cara Menjalankan

### Otomatis (Recommended)
```bash
# Jalankan script batch
start_websocket_system.bat
```

### Manual
```bash
# 1. Start Backend WebSocket Server
cd backend
python main_websocket.py

# 2. Start Controller Gate IN (terminal baru)
cd controller
python main_websocket.py gate_in

# 3. Start Controller Gate OUT (terminal baru)
cd controller
python main_websocket.py gate_out

# 4. Start Frontend (terminal baru)
cd frontend
npm start
```

## 📡 Komunikasi Data

### Dari Controller ke Backend
```json
{
  "type": "hardware_status",
  "payload": {
    "camera": { "connected": true, "status": "ready" },
    "card_reader": { "connected": true, "port": "COM17" },
    "arduino": { "connected": true, "gate_status": "closed" }
  },
  "gate_id": "gate_in",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### Dari Backend ke Frontend
```json
{
  "type": "hardware_status",
  "payload": {
    "camera": { "connected": true, "status": "ready" },
    "card_reader": { "connected": true, "port": "COM17" },
    "arduino": { "connected": true, "gate_status": "closed" }
  },
  "gate_id": "gate_in",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### Dari Frontend ke Backend (Gate Control)
```json
{
  "type": "gate_control",
  "payload": {
    "action": "open",
    "gate_id": "gate_in",
    "duration": 10
  }
}
```

## 🔄 Message Types

### Hardware Status
- `hardware_status` - Status hardware (kamera, arduino, card reader)
- `system_status` - Status sistem controller
- `card_detected` - Kartu terdeteksi di card reader
- `gate_status` - Status gate (open/closed/opening/closing)

### Parking Events
- `parking_entry` - Event masuk parkir
- `parking_exit` - Event keluar parkir
- `image_captured` - Gambar berhasil di-capture

### Control Commands
- `gate_control` - Kontrol gate (open/close)
- `camera_control` - Kontrol kamera (capture/start_stream/stop_stream)
- `request_status` - Request status sistem

### Responses
- `gate_control_response` - Response kontrol gate
- `parking_event` - Event parkir
- `error` - Error message

## 🌐 Frontend Usage

### Koneksi ke Channel Berbeda
```javascript
import { 
  connectToGateIn, 
  connectToGateOut, 
  connectToGateAll,
  getGateInClient,
  getGateAllClient 
} from './services/websocketNew.js'

// Koneksi ke gate masuk
const gateInClient = connectToGateIn()

// Listen untuk hardware status
gateInClient.on('hardware_status', (data) => {
  console.log('Gate IN Hardware Status:', data.payload)
})

// Kontrol gate
gateInClient.controlGate('open', 'gate_in', 10)

// Monitoring semua gate
const allGatesClient = connectToGateAll()
allGatesClient.on('parking_event', (data) => {
  console.log('Parking Event:', data.payload)
})
```

### Komponen React
```jsx
import { useEffect, useState } from 'react'
import { getGateInClient } from '../services/websocketNew'

function GateInMonitor() {
  const [hardwareStatus, setHardwareStatus] = useState({})
  const [connected, setConnected] = useState(false)
  
  useEffect(() => {
    const client = getGateInClient()
    client.connect()
    
    client.on('connected', () => setConnected(true))
    client.on('disconnected', () => setConnected(false))
    client.on('hardware_status', (data) => {
      setHardwareStatus(data.payload)
    })
    
    return () => client.disconnect()
  }, [])
  
  const handleOpenGate = () => {
    const client = getGateInClient()
    client.controlGate('open')
  }
  
  return (
    <div>
      <h2>Gate IN Monitor</h2>
      <p>Status: {connected ? 'Connected' : 'Disconnected'}</p>
      <button onClick={handleOpenGate}>Open Gate</button>
      <pre>{JSON.stringify(hardwareStatus, null, 2)}</pre>
    </div>
  )
}
```

## 🔧 Konfigurasi

### Environment Variables
```bash
# Controller
GATE_ID=gate_in          # atau gate_out
BACKEND_HOST=localhost
BACKEND_PORT=8000

# Backend
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8000
```

### Channel Configuration
- **gate_in**: Data khusus untuk gate masuk
- **gate_out**: Data khusus untuk gate keluar  
- **gate_all**: Monitoring semua gate (untuk dashboard utama)
- **admin**: Untuk monitoring dan kontrol admin

## 🏗️ Struktur File Baru

```
manless/
├── backend/
│   ├── main_websocket.py      # Backend WebSocket Server
│   ├── websocket_server.py    # WebSocket Channel Manager
│   └── ...
├── controller/  
│   ├── main_websocket.py      # Controller WebSocket Client
│   ├── websocket_client.py    # WebSocket Client Implementation
│   └── ...
├── frontend/
│   ├── src/services/
│   │   ├── websocketNew.js    # Frontend WebSocket Client
│   │   └── ...
│   └── ...
├── start_websocket_system.bat # Script untuk start semua komponen
└── README_ARSITEKTUR_WEBSOCKET.md
```

## 🎯 Keuntungan Arsitektur Baru

1. **Separation of Concerns**:
   - Backend hanya untuk relay data
   - Controller fokus pada hardware
   - Frontend fokus pada UI realtime

2. **Scalability**:
   - Mudah menambah gate baru
   - Channel terpisah untuk setiap gate
   - Multiple frontend bisa connect ke channel berbeda

3. **Real-time Performance**:
   - Data langsung dari controller ke frontend
   - Minimal latency
   - Efficient message routing

4. **Reliability**:
   - Auto-reconnect pada semua komponen
   - Error handling yang baik
   - Status monitoring

5. **Flexibility**:
   - Frontend bisa pilih channel sesuai kebutuhan
   - Easy debugging per channel
   - Modular architecture

## 🚨 Troubleshooting

### Backend WebSocket Server tidak start
```bash
# Check port 8000
netstat -an | findstr :8000

# Manual start untuk debug
cd backend
python main_websocket.py
```

### Controller tidak connect ke backend
```bash
# Check backend sudah running
curl http://localhost:8000/status

# Manual start controller
cd controller
python main_websocket.py gate_in
```

### Frontend tidak menerima data
```javascript
// Check connection status
const client = getGateAllClient()
console.log('Connected:', client.isConnected())
console.log('State:', client.getConnectionState())

// Manual connect
client.connect()
```

## 📊 Monitoring & Debugging

### Backend Status
- URL: `http://localhost:8000/status`
- Shows: Active channels, connected controllers, latest data

### Frontend Console
- All WebSocket events logged with channel info
- Connection status updates
- Message flow tracking

### Controller Logs
- Hardware status updates
- WebSocket connection status  
- Error messages and reconnection attempts 