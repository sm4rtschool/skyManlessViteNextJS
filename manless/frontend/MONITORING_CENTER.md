# Monitoring Center - Dashboard Terpusat

## Overview
Monitoring Center adalah dashboard terpusat untuk memantau semua gate dalam sistem parkir manless. Dashboard ini menampilkan status real-time dari semua komponen sistem dan aktivitas parkir.

## Akses URL
- **Monitoring Center**: `http://localhost:5173/` (tanpa parameter)
- **Monitoring Center**: `http://localhost:5173/?gate=all` (eksplisit)
- **Gate IN Kiosk**: `http://localhost:5173/?gate=gate_in`
- **Gate OUT Kiosk**: `http://localhost:5173/?gate=gate_out`

## Fitur Utama

### 1. System Overview Cards
- **Central Hub**: Status coordinator dengan active sessions dan timestamp
- **Gate Masuk**: Status hardware (Camera/Arduino/Card Reader) gate masuk
- **Gate Keluar**: Status hardware (Camera/Arduino/Card Reader) gate keluar

### 2. Real-time Connection Status
- **Connection Indicator**: Status koneksi WebSocket (CONNECTED/DISCONNECTED)
- **Current Time**: Waktu sistem dalam format Indonesia
- **Auto-refresh**: Update otomatis setiap 10 detik

### 3. Gate Selector
- **Dropdown Menu**: Pilih gate untuk monitoring atau buka interface operasional
- **Quick Links**: URL untuk membuka gate-specific interface di tab baru

### 4. System Statistics
- **Total Vehicles**: Jumlah kendaraan dalam sistem
- **Today Entries**: Kendaraan masuk hari ini
- **Current Occupancy**: Kapasitas terisi saat ini
- **Available Slots**: Slot parkir tersedia

### 5. Live View
- **Multi-Gate Camera**: View kamera dari semua gate
- **Real-time Stream**: Stream video real-time
- **Connection Status**: Status koneksi kamera per gate

### 6. Recent Events Panel
- **Real-time Events**: 10 event terbaru dari semua gate
- **Color Coding**: 
  - 🟢 Success (hijau)
  - 🟡 Warning (kuning)
  - 🔴 Error (merah)
  - 🔵 Info (biru)
- **Timestamp**: Waktu event dalam format Indonesia

### 7. System Logs
- **Comprehensive Logging**: Log dari semua komponen sistem
- **Filtered View**: Log dapat difilter berdasarkan level dan komponen
- **Real-time Updates**: Log update secara real-time

### 8. Quick Actions
- **🔄 Refresh Status**: Manual refresh status sistem
- **📸 Capture Gate IN**: Ambil foto dari kamera gate masuk
- **📸 Capture Gate OUT**: Ambil foto dari kamera gate keluar
- **🖥️ Open Gate IN**: Buka interface operasional gate masuk di tab baru

## Event Types yang Dimonitor

### WebSocket Events
```javascript
// Connection events
wsService.on('connected', handleConnected)
wsService.on('disconnected', handleDisconnected)

// System events
wsService.on('system_status', handleSystemStatus)
wsService.on('parking_event', handleParkingEvent)
wsService.on('gate_event', handleGateEvent)
wsService.on('camera_event', handleCameraEvent)
wsService.on('card_event', handleCardEvent)
```

### Event Processing
- **Parking Events**: Entry/exit kendaraan dengan update statistik
- **Gate Events**: Buka/tutup gate dengan logging
- **Camera Events**: Capture foto dengan notifikasi
- **Card Events**: Validasi kartu dengan status feedback

## Hardware Status Indicators

### Status Colors
- **🟢 Green**: All systems online (3/3 connected)
- **🟡 Orange**: Partial connection (1-2/3 connected)
- **🔴 Red**: Offline (0/3 connected)

### Hardware Components
- **Camera**: Status koneksi kamera RTSP/HTTP
- **Arduino**: Status koneksi mikrokontroler
- **Card Reader**: Status pembaca kartu RFID/NFC

## API Integration

### System Status API
```javascript
const systemData = await apiService.getSystemStatus()
const capacity = await apiService.getParkingCapacity()
```

### WebSocket Commands
```javascript
wsService.requestSystemStatus()
wsService.captureImageGateIn()
wsService.captureImageGateOut()
```

## Responsive Design
- **Desktop**: Layout 3-kolom dengan sidebar
- **Tablet**: Layout 2-kolom responsif
- **Mobile**: Layout 1-kolom dengan scroll

## Auto-refresh Features
- **System Status**: Update setiap 10 detik
- **Real-time Clock**: Update setiap detik
- **Event Stream**: Real-time via WebSocket
- **Statistics**: Update otomatis berdasarkan events

## Error Handling
- **Connection Errors**: Graceful degradation dengan retry
- **API Errors**: Error logging dengan fallback data
- **WebSocket Errors**: Auto-reconnect dengan status indicator

## Usage Scenarios

### 1. Security Control Room
- Monitor semua gate dari satu dashboard
- Real-time alerts untuk anomali
- Historical data dan reporting

### 2. Parking Management
- Kapasitas monitoring real-time
- Revenue tracking per gate
- System health monitoring

### 3. Technical Support
- Hardware status monitoring
- Error diagnosis dan troubleshooting
- Remote system control

## Development Notes

### Component Structure
```
MonitoringCenter.jsx
├── Header dengan connection status
├── Gate Selector untuk navigation
├── System Overview Cards (3 cards)
├── System Statistics
├── Main Content Grid
│   ├── Live View (2 columns)
│   └── Recent Events (1 column)
├── Log Viewer (full width)
└── Quick Actions panel
```

### State Management
- **systemStatus**: Status semua komponen sistem
- **parkingStats**: Statistik parkir real-time
- **recentEvents**: Array 10 event terbaru
- **connectionStatus**: Status koneksi WebSocket

### Performance Optimizations
- **Event Filtering**: Hanya proses events yang relevan
- **Lazy Loading**: Load data sesuai kebutuhan
- **Memory Management**: Limit event history ke 10 items
- **Debounced Updates**: Hindari update berlebihan

## Deployment
Monitoring Center siap untuk deployment sebagai:
- **Web Dashboard**: Akses via browser dari control room
- **Kiosk Mode**: Fullscreen untuk monitor dedicated
- **Mobile App**: Responsive untuk akses mobile

Status: ✅ **READY FOR PRODUCTION** 