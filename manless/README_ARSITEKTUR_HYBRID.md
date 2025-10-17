# Arsitektur Hybrid Sistem Parkir Manless

## 🏗️ **Arsitektur yang Benar**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARSITEKTUR HYBRID SYSTEM                     │
└─────────────────────────────────────────────────────────────────┘

    Frontend (Smart Routes)       Backend (Hybrid)         Controller
  ┌─────────────────────────┐   ┌─────────────────────┐   ┌─────────────┐
  │                         │   │                     │   │             │
  │ URL: /gate-in           │   │   FastAPI Server    │   │ Hardware    │
  │ → WS: ws/gate_in        ├──►│                     │◄──┤ Controller  │
  │                         │   │ • HTTP API:         │   │             │
  │ URL: /gate-out          │   │   /api/v1/*         │   │ - Arduino   │
  │ → WS: ws/gate_out       ├──►│ • Database          │   │ - Camera    │
  │                         │   │ • Business Logic    │   │ - Card      │
  │ URL: /admin             │   │                     │   │   Reader    │
  │ → WS: ws/gate_all       ├──►│ • WebSocket:        │   │             │
  │                         │   │   /ws/gate_in       │   │             │
  │ Smart WebSocket:        │   │   /ws/gate_out      │   │             │
  │ - Auto-detect channel   │   │   /ws/gate_all      │   │             │
  │ - URL-based routing     │   │   /ws/admin         │   │             │
  │ - Real-time updates     │   │                     │   │             │
  └─────────────────────────┘   └─────────────────────┘   └─────────────┘
```

## ✅ **Komponen Sistem**

### 1. **Backend Hybrid** (`backend/main_hybrid.py`)
**Fungsi**: HTTP API + WebSocket Server dalam satu aplikasi FastAPI

#### HTTP API:
- `/api/v1/*` - REST API untuk database dan business logic
- `/api/docs` - API documentation
- `/api/system/status` - System status
- `/api/websocket/status` - WebSocket debugging

#### WebSocket Server:
- `/ws/gate_in` - Channel untuk frontend gate masuk
- `/ws/gate_out` - Channel untuk frontend gate keluar
- `/ws/gate_all` - Channel untuk monitoring semua gate
- `/ws/admin` - Channel untuk admin (alias gate_all)
- `/ws/controller/gate_in` - Endpoint untuk controller gate masuk
- `/ws/controller/gate_out` - Endpoint untuk controller gate keluar

### 2. **Controller WebSocket Client** (`controller/main_websocket.py`)
**Fungsi**: Hardware management + WebSocket client ke backend
- Menangani Arduino, Camera, Card Reader
- Mengirim data hardware secara real-time ke backend
- Menerima perintah kontrol dari backend

### 3. **Frontend Smart WebSocket** (`frontend/src/services/smartWebSocket.js`)
**Fungsi**: Auto-detect WebSocket channel berdasarkan URL

#### Smart Routing:
```javascript
URL Frontend → WebSocket Channel:
/gate-in    → ws://localhost:8000/ws/gate_in
/gate-out   → ws://localhost:8000/ws/gate_out
/admin      → ws://localhost:8000/ws/gate_all
/dashboard  → ws://localhost:8000/ws/gate_all
```

## 🚀 **Cara Menjalankan**

### Metode 1: Script Otomatis (Recommended)
```bash
# Jalankan sistem hybrid
start_hybrid_system.bat
```

### Metode 2: Manual
```bash
# 1. Backend Hybrid (API + WebSocket)
cd backend
python main_hybrid.py

# 2. Controller Gate IN (terminal baru)
cd controller
python main_websocket.py gate_in

# 3. Controller Gate OUT (terminal baru) 
cd controller
python main_websocket.py gate_out

# 4. Frontend (terminal baru)
cd frontend
npm start
```

### Frontend Access:
```bash
# Buka browser ke:
http://localhost:3000/gate-in     # Kiosk Gate Masuk
http://localhost:3000/gate-out    # Kiosk Gate Keluar  
http://localhost:3000/admin       # Dashboard Admin
```

## 🌐 **Frontend Smart Usage**

### Auto-Detection dari URL
Frontend otomatis detect channel WebSocket berdasarkan URL tanpa konfigurasi manual:

```javascript
// Di halaman /gate-in
import { useSmartWebSocket } from '../services/smartWebSocket'

const GateInPage = () => {
  const ws = useSmartWebSocket()  // Otomatis connect ke gate_in
  
  useEffect(() => {
    ws.connect()  // Connect ke ws://localhost:8000/ws/gate_in
    
    ws.on('hardware_status', (data) => {
      // Hanya menerima data untuk gate_in
      console.log('Gate IN status:', data.payload)
    })
    
    // Kontrol gate (otomatis untuk gate_in)
    ws.openGate(10)  // Buka gate selama 10 detik
  }, [])
}
```

### Route-Specific Components
```javascript
// /gate-in → GateInPage.jsx (hanya data gate_in)
// /gate-out → GateOutPage.jsx (hanya data gate_out) 
// /admin → AdminPage.jsx (data semua gate)
```

## 📡 **Komunikasi Data**

### Dari Controller ke Backend
```json
{
  "type": "hardware_status",
  "payload": {
    "camera": { "connected": true },
    "card_reader": { "connected": true },
    "arduino": { "connected": true, "gate_status": "closed" }
  },
  "gate_id": "gate_in",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### Backend → Frontend (Auto-Filtered)
Frontend hanya menerima data yang relevan dengan channelnya:

```javascript
// Di /gate-in: hanya menerima data gate_id: "gate_in"
// Di /gate-out: hanya menerima data gate_id: "gate_out"  
// Di /admin: menerima semua data
```

### Frontend → Backend (Smart Commands)
```javascript
// Di halaman gate-in
ws.openGate()  // Otomatis kirim ke gate_in

// Di halaman admin  
ws.controlSpecificGate('gate_out', 'open')  // Kontrol gate spesifik
```

## 🔧 **HTTP API Usage**

Selain WebSocket, backend juga menyediakan HTTP API:

```javascript
// Database operations
POST /api/v1/parking/entry
POST /api/v1/parking/exit
GET  /api/v1/parking/history

// Gate control via HTTP
POST /api/v1/gate/gate_in/control
GET  /api/v1/gate/gate_in/status

// System monitoring
GET  /api/system/status
GET  /api/websocket/status
```

## 🎯 **Keuntungan Arsitektur Hybrid**

### ✅ **Separation of Concerns**
- Backend: Database + Business Logic + Real-time Communication
- Controller: Hardware Management
- Frontend: UI dengan Smart Routing

### ✅ **Best of Both Worlds**
- HTTP API untuk operasi database yang reliabel
- WebSocket untuk real-time updates yang cepat
- Smart frontend yang tahu cara connect otomatis

### ✅ **Scalability & Maintainability**
- Satu backend server untuk semua fungsi
- Frontend routing yang bersih dan intuitif
- Easy debugging dan monitoring

### ✅ **Real-time Performance**
- Data hardware langsung dari controller ke frontend
- Minimal latency dengan smart filtering
- Auto-reconnect dan error handling

## 🔄 **Message Flow**

```
1. Controller Hardware Event:
   Arduino → Controller → Backend WebSocket → Frontend (filtered)

2. Frontend Gate Control:
   Frontend → Backend WebSocket → Controller → Arduino

3. Database Operations:
   Frontend → Backend HTTP API → Database

4. Status Monitoring:
   Frontend → Backend (HTTP/WebSocket) → Real-time updates
```

## 🧪 **Testing & Debugging**

### Test System
```bash
python test_websocket_system.py
```

### API Documentation
```
http://localhost:8000/api/docs
```

### System Status
```
http://localhost:8000/api/system/status
http://localhost:8000/api/websocket/status
```

### Frontend Debug
Buka browser console di setiap halaman untuk melihat:
- Auto-detected WebSocket channel
- Real-time message flow
- Connection status
- Filtered data

## 🚨 **Troubleshooting**

### Backend tidak start
```bash
# Check port 8000
netstat -an | findstr :8000

# Manual debug
cd backend
python main_hybrid.py
```

### Frontend tidak menerima data
```javascript
// Check di browser console
console.log('Current channel:', ws.getCurrentChannel())
console.log('Connected:', ws.isConnected())

// Manual reconnect
ws.reconnect()
```

### Controller tidak connect
```bash
# Check backend status
curl http://localhost:8000/api/websocket/status

# Manual start controller
cd controller
python main_websocket.py gate_in
```

## 📊 **URL Mapping Summary**

| Frontend URL | WebSocket Channel | Purpose |
|--------------|------------------|---------|
| `/gate-in` | `ws/gate_in` | Kiosk gate masuk |
| `/gate-out` | `ws/gate_out` | Kiosk gate keluar |
| `/admin` | `ws/gate_all` | Dashboard admin |
| `/dashboard` | `ws/gate_all` | Monitoring |
| `/monitor` | `ws/gate_all` | Monitoring |

## 🎪 **Demo Flow**

1. **Start System**: `start_hybrid_system.bat`
2. **Start Frontend**: `cd frontend && npm start`
3. **Test Gate IN**:
   - Buka `http://localhost:3000/gate-in`
   - Lihat console: auto-connect ke `ws/gate_in`
   - Klik "BUKA GATE" → perintah terkirim ke controller
4. **Test Admin**:
   - Buka `http://localhost:3000/admin`
   - Lihat console: auto-connect ke `ws/gate_all`
   - Monitor data dari kedua gate
5. **API Test**: Buka `http://localhost:8000/api/docs`

Arsitektur hybrid ini memberikan fleksibilitas maksimal dengan kompleksitas minimal! 🚀 