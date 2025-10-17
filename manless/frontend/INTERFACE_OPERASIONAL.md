# Interface Operasional Gate - Sistem Parkir Manless

## Overview
Interface operasional ini adalah **aplikasi utama** yang akan berjalan di setiap gate (Gate IN dan Gate OUT). Dirancang khusus untuk monitor 10 inch sebagai interface utama operasional, bukan hanya dashboard monitoring.

## Fitur Utama

### 🖥️ **Design Interface**
- **Dark Theme**: Background hitam dengan teks putih untuk visibilitas optimal
- **Monospace Font**: Font terminal untuk tampilan profesional
- **Grid Layout**: 2 kolom responsif untuk organisasi informasi
- **Real-time Updates**: Semua data update secara real-time

### 📹 **Live Camera View**
- **Real-time Video Stream**: Menampilkan feed kamera langsung
- **Connection Status**: Indikator status koneksi kamera
- **Last Capture Time**: Timestamp foto terakhir yang diambil
- **Stream URL Display**: Menampilkan URL stream yang aktif

### 🔗 **Status Koneksi**
- **WebSocket Server**: Status koneksi ke backend central hub
- **Arduino Controller**: Status koneksi ke hardware controller
- **Camera**: Status koneksi kamera RTSP/HTTP
- **Card Reader**: Status koneksi RFID reader
- **Color Indicators**: Hijau (terhubung), Merah (terputus)

### 💳 **Card Reader Interface**
- **Real-time Status**: WAITING → VALID/INVALID
- **Card ID Display**: Menampilkan ID kartu yang ditap
- **Timestamp**: Waktu tap kartu terakhir
- **Visual Feedback**: Background berubah sesuai status
- **Auto-reset**: Kembali ke WAITING setelah 3 detik

### 🚪 **Gate Control Status**
- **Gate Position**: TERBUKA/TERTUTUP dengan indikator visual
- **Operation Time**: Timestamp operasi terakhir
- **Auto-close Timer**: Gate otomatis tertutup setelah durasi tertentu
- **Vehicle Detection**: Status keberadaan kendaraan di gate

### 🅿️ **Parking Area Info**
- **Total Slots**: Jumlah total slot parkir
- **Occupied**: Slot yang terisi
- **Available**: Slot yang tersedia
- **Real-time Updates**: Data update otomatis dari backend

### ⏰ **Real-time Clock**
- **Current Time**: Jam, menit, detik (update setiap detik)
- **Full Date**: Hari, tanggal, bulan, tahun dalam bahasa Indonesia
- **Timezone**: Waktu Indonesia (id-ID)

### 📋 **Operational Logs**
Real-time log aktivitas dengan timestamp dan color coding:
- 🟢 **WebSocket Events**: Koneksi/disconnection
- 💳 **Card Events**: Tap kartu, validasi
- 🚪 **Gate Events**: Buka/tutup gate
- 🚗 **Vehicle Events**: Deteksi kendaraan
- 📸 **Camera Events**: Capture foto
- 🎫 **Ticket Events**: Cetak tiket
- 🔧 **Arduino Events**: Hardware events
- 🔘 **Button Events**: Tombol manual ditekan

## Event Handling

### WebSocket Events yang Didengarkan:
```javascript
// System Events
'connected' → WebSocket terhubung
'disconnected' → WebSocket terputus
'system_status' → Status sistem update

// Hardware Events  
'card_event' → Kartu ditap
'gate_event' → Gate dibuka/ditutup
'vehicle_event' → Kendaraan terdeteksi/lewat
'camera_event' → Foto diambil/stream update
'ticket_event' → Tiket dicetak
'arduino_event' → Event dari Arduino
```

### Log Messages:
```
[14:30:25] 🟢 WebSocket terhubung ke server
[14:30:26] 💳 Kartu ditap: CARD_001 - valid
[14:30:27] 🚪 Gate dibuka
[14:30:28] 📸 Foto kendaraan diambil: capture_001.jpg
[14:30:29] 🎫 Tiket dicetak: TKT_001
[14:30:30] 🚗 Kendaraan terdeteksi
[14:30:35] 🚗 Kendaraan melewati gate
[14:30:40] 🚪 Gate otomatis tertutup
```

## URL Configuration

### Gate IN Interface:
```
http://localhost:5173/?gate=gate_in
```
- **Header**: 🚪➡️ Gate Masuk (Hijau)
- **Location**: Pintu Masuk Utama
- **Events**: Entry processing, card validation, ticket printing

### Gate OUT Interface:
```
http://localhost:5173/?gate=gate_out
```
- **Header**: 🚪⬅️ Gate Keluar (Merah)  
- **Location**: Pintu Keluar Utama
- **Events**: Exit processing, payment, receipt printing

## Auto-run Setup

### Kiosk Mode Features:
- **Auto-fullscreen**: Masuk fullscreen otomatis
- **Disable right-click**: Mencegah context menu
- **Disable F12/DevTools**: Keamanan interface
- **Auto-refresh**: Refresh otomatis setiap 6 jam
- **Touch-friendly**: Interface optimal untuk touchscreen

### Startup Scripts:
```batch
# Gate IN Kiosk
start_gate_in_kiosk.bat
→ chrome --kiosk --disable-web-security http://localhost:5173/?gate=gate_in

# Gate OUT Kiosk  
start_gate_out_kiosk.bat
→ chrome --kiosk --disable-web-security http://localhost:5173/?gate=gate_out
```

## Hardware Integration

### Arduino Events:
- **Button Press**: Manual gate control
- **Sensor Data**: Vehicle detection
- **Gate Motor**: Open/close operations
- **Status LEDs**: Visual indicators

### Camera Integration:
- **RTSP Stream**: Live video feed
- **HTTP Capture**: Foto kendaraan
- **Motion Detection**: Trigger events
- **Stream Health**: Connection monitoring

### Card Reader:
- **RFID Detection**: Tap kartu
- **Card Validation**: Valid/invalid status
- **Data Extraction**: Card ID, user info
- **Response Time**: Real-time feedback

## Technical Specs

### Performance:
- **Update Frequency**: 1 detik (clock), real-time (events)
- **Log Retention**: 20 entries terakhir
- **Auto-scroll**: Log otomatis scroll ke bawah
- **Memory Management**: Cleanup old data

### Responsive Design:
- **Grid Layout**: 2 kolom pada desktop
- **Mobile Fallback**: Stack vertical pada mobile
- **Touch Targets**: Minimum 44px untuk touch
- **High Contrast**: Optimal untuk berbagai kondisi cahaya

## Deployment

### Production Setup:
1. **Frontend**: `npm run build` → Static files
2. **Backend**: Central Hub + Gate Controllers
3. **Hardware**: Arduino, Camera, Card Reader
4. **Network**: Local network dengan port forwarding
5. **Kiosk**: Windows/Linux dengan auto-start browser

### Monitoring:
- **Health Checks**: Automatic connection monitoring
- **Error Recovery**: Auto-reconnect pada disconnection
- **Logging**: Comprehensive operational logs
- **Alerts**: Visual dan audio indicators untuk issues

## Status Implementasi
- ✅ **Interface Design** - Complete
- ✅ **Real-time Updates** - Working
- ✅ **WebSocket Integration** - Functional
- ✅ **Event Handling** - Complete
- ✅ **Responsive Layout** - Ready
- ✅ **Dark Theme** - Implemented
- ✅ **Operational Logs** - Working
- ✅ **Gate-specific Routing** - Ready
- ✅ **Auto-run Scripts** - Available

Interface operasional ini siap untuk deployment sebagai aplikasi utama di setiap gate dengan semua fitur monitoring dan control yang dibutuhkan untuk operasional parkir manless. 