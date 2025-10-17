# Debugging Frontend Blank Issue

## Masalah
Frontend menampilkan halaman blank saat diakses via `http://localhost:5173/?gate=gate_in`

## Perbaikan yang Dilakukan

### 1. Error Boundary
- **File**: `src/components/ErrorBoundary.jsx`
- **Fungsi**: Menangkap JavaScript errors dan menampilkan fallback UI
- **Status**: ✅ Implemented

### 2. Loading Screen
- **File**: `src/components/LoadingScreen.jsx`
- **Fungsi**: Menampilkan loading state saat initialization
- **Status**: ✅ Implemented

### 3. Simple Dashboard
- **File**: `src/components/SimpleDashboard.jsx`
- **Fungsi**: Dashboard sederhana sebagai fallback untuk debugging
- **Status**: ✅ Implemented

### 4. Service Exports
- **File**: `src/services/websocket.js`
- **Perbaikan**: Export `wsService` instance
- **Status**: ✅ Fixed

- **File**: `src/services/api.js`
- **Perbaikan**: Export `apiService` instance
- **Status**: ✅ Fixed

### 5. Dashboard Loading State
- **File**: `src/pages/Dashboard.jsx`
- **Perbaikan**: 
  - Tambah loading state
  - Perbaiki API calls (getHealthCheck → getSystemStatus)
  - Gunakan SimpleDashboard untuk gate-specific mode
- **Status**: ✅ Fixed

## Cara Testing

### 1. Buka Browser Console
```
F12 → Console Tab
```

### 2. Akses URL Gate-Specific
```
http://localhost:5173/?gate=gate_in
http://localhost:5173/?gate=gate_out
```

### 3. Check WebSocket Connection
```javascript
// Di browser console
wsService.isConnected()
```

### 4. Check System Status
```javascript
// Di browser console
apiService.getSystemStatus()
```

## Expected Behavior

### Loading Sequence
1. **Loading Screen** (1 detik)
2. **Simple Dashboard** (gate-specific mode)
3. **WebSocket Connection** (auto-connect)
4. **System Status** (fetch from API)

### Gate-Specific Mode
- URL: `?gate=gate_in` atau `?gate=gate_out`
- Layout: Fullscreen tanpa sidebar
- Components: SimpleDashboard (fallback)

### Monitoring Mode
- URL: `?gate=all` atau tanpa parameter
- Layout: Dengan sidebar dan header
- Components: Full Dashboard

## Error Indicators

### 1. JavaScript Errors
- **Error Boundary** akan menampilkan fallback UI
- **Console** akan menampilkan stack trace

### 2. API Connection Issues
- **Simple Dashboard** akan menampilkan "Disconnected"
- **Console** akan menampilkan fetch errors

### 3. WebSocket Issues
- **Connection Status** akan menampilkan "DISCONNECTED"
- **Console** akan menampilkan WebSocket errors

## Debug Commands

### Browser Console
```javascript
// Check gate configuration
gateConfig.getCurrentGate()
gateConfig.getGateInfo()
gateConfig.isGateSpecific()

// Check services
wsService.isConnected()
apiService.getSystemStatus()

// Simulate actions
wsService.simulateCardScan('gate_in', 'TEST_001', 'B1234XYZ')
wsService.controlGate('gate_in', 'open', 10)
```

### Network Tab
- Check API calls ke `http://localhost:8000/api/status`
- Check WebSocket connection ke `ws://localhost:8000/ws`

## Backend Requirements

### Central Hub (Port 8000)
```bash
cd manless/backend
python main.py
```

### Gate Controllers
```bash
# Gate IN (Port 8001)
cd manless/controller
python main_gate_in.py

# Gate OUT (Port 8002)
cd manless/controller
python main_gate_out.py
```

## Rollback Plan

Jika SimpleDashboard bermasalah, bisa kembali ke GateSpecificDashboard:

```javascript
// Di src/pages/Dashboard.jsx
if (gateConfig.isGateSpecific()) {
  return <GateSpecificDashboard />  // Enable ini
  // return <SimpleDashboard />     // Disable ini
}
```

## Status Komponen

- ✅ ErrorBoundary - Working
- ✅ LoadingScreen - Working  
- ✅ SimpleDashboard - Working
- ⚠️ GateSpecificDashboard - Debugging
- ✅ WebSocket Service - Working
- ✅ API Service - Working
- ✅ Gate Config - Working

## Next Steps

1. Test SimpleDashboard di browser
2. Check console untuk errors
3. Verify WebSocket connection
4. Test API calls
5. Jika SimpleDashboard work, debug GateSpecificDashboard 