# WebSocket Troubleshooting Guide - Manless Parking System

## 🔍 Status Diagnosis

### ✅ WebSocket Connection Working!
Berdasarkan testing terbaru, WebSocket connection sudah berfungsi dengan baik:

- **Connection**: Successfully established
- **Ping/Pong**: Communication working
- **System Status**: Data received correctly  
- **Gate Controllers**: Both online and responding

## 🛠️ Perbaikan yang Telah Dilakukan

### 1. Frontend WebSocket Service (websocket.js)
- Delay 200ms sebelum send initial request
- Better readyState checking: ws.readyState !== WebSocket.OPEN
- Ping/Pong monitoring setiap 30 detik
- Exponential backoff untuk reconnection
- Better error handling dan logging

### 2. Interface Operasional (GateOperationalInterface.jsx)
- Component-based logging system
- Auto-reset card reader status (5 detik)
- Real-time connection status indicators
- Better state management untuk semua hardware

### 3. Backend DateTime JSON Fix
- datetime.now() → datetime.now().isoformat()
- Custom JSON encoder untuk handle datetime objects
- Safe WebSocket message sending functions

## 🚨 Common Issues & Solutions

### Issue 1: "WebSocket connection failed"
**Solutions:**
1. Check Backend Running: `cd manless/backend && python main.py`
2. Check Port: `netstat -an | findstr :8000`
3. Restart WebSocket: `wsService.reconnect()`

### Issue 2: "InvalidStateError: Still in CONNECTING state" 
**Fixed dengan:**
- Delay dalam onOpen() method
- Better state checking dalam send() method

### Issue 3: "Object of type datetime is not JSON serializable"
**Fixed dengan:**
- Menggunakan .isoformat() untuk datetime objects
- Custom JSON encoder untuk handle datetime

## 🔧 Testing Commands

### Quick System Status Check
```bash
cd manless
python check_system_status.py
```

### WebSocket Connection Test  
```bash
cd manless
python test_websocket_client.py simple
```

## 📊 Expected System Status

### ✅ Healthy System:
- Central Hub (Port 8000): WebSocket Connected
- Gate IN Controller (8001): HTTP 200 - API responding
- Gate OUT Controller (8002): HTTP 200 - API responding
- Frontend (Port 5173): HTTP 200 - Development server

### ⚠️ Normal Errors:
- Root endpoints (/) returning 404 adalah normal
- Error 405 "Method Not Allowed" tidak mempengaruhi WebSocket

## 🎯 Frontend Browser Console

### ✅ Expected Logs:
```
✅ GateConfig initialized: gate_in
🔗 Connecting to Central Hub WebSocket...
✅ Connected to Central Hub WebSocket
📤 Sent to Central Hub: request_system_status
📨 Received from Central Hub: system_status
```

## 🚀 Performance Optimizations

### Connection Monitoring
- Ping setiap 30 detik untuk health check
- Auto-reconnect dengan exponential backoff
- Max 10 reconnection attempts

### Message Filtering
- Gate-specific event filtering
- Reduced unnecessary processing
- Better performance untuk kiosk mode

### Log Management
- Max 50 logs untuk prevent memory issues
- Auto-scroll untuk better UX
- Component-based log organization

## 📱 Kiosk Mode Features

### Auto-Setup URLs:
- Gate Masuk: `http://localhost:5173/?gate=gate_in`
- Gate Keluar: `http://localhost:5173/?gate=gate_out`
- Monitoring: `http://localhost:5173/`

### Kiosk Optimizations:
- Auto-fullscreen
- Disable right-click dan F12
- Auto-refresh setiap 6 jam
- Touch-friendly interface

## 🚨 Error onClose/onError di Frontend Gate IN

### Issue 4: "Error in onClose handler" / "Error in onError handler"
**Fixed dengan:**
- Safe event binding dengan try-catch di semua event handlers
- Better error handling untuk undefined/null event properties
- Robust data validation untuk semua WebSocket events

### Perbaikan Event Handlers:
```javascript
// Safe event binding
this.ws.onclose = (event) => {
  try {
    this.onClose(event)
  } catch (error) {
    console.error('Error in onClose handler:', error)
  }
}

// Safe property access  
onClose(event) {
  this.emit('disconnected', { 
    code: event?.code || 1000, 
    reason: event?.reason || 'Connection closed',
    wasClean: event?.wasClean || false,
    timestamp: new Date().toISOString()
  })
}
```

## 🛠️ Quick Start Tools

### PowerShell Startup Script
```powershell
.\start_components.ps1
```
Automatically starts all components dan check status.

### Manual Testing Tool
Open `test_frontend_gate_in.html` dalam browser untuk manual testing WebSocket connection.

## 🎉 System Ready!

WebSocket connection dan interface operasional sekarang berfungsi dengan baik untuk:
- ✅ Gate IN Interface (Port 8001) - Error handling improved
- ✅ Gate OUT Interface (Port 8002) - Error handling improved
- ✅ Monitoring Center (All gates) - Full monitoring
- ✅ Kiosk Mode (10 inch monitors) - Production ready
- ✅ Real-time Updates - Stable WebSocket connection
- ✅ Hardware Integration - Robust error handling

Sistem siap untuk deployment di monitor kiosk sebagai aplikasi operasional utama! 