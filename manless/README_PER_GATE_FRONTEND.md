# 🖥️ Frontend Per-Gate Setup - Sistem Parkir Manless

## 📋 Overview

Frontend telah dimodifikasi untuk mendukung **mode per-gate**, dimana setiap monitor di tiket dispenser hanya menampilkan aktivitas dari gate tersebut saja. Sistem mendukung 3 mode:

1. **Gate IN Mode** - Monitor kiosk untuk gate masuk
2. **Gate OUT Mode** - Monitor kiosk untuk gate keluar  
3. **Monitoring Center** - Control center untuk monitoring semua gate

## 🚪 Mode Gate

### 1. Gate IN Mode (`?gate=gate_in`)
- **Lokasi**: Monitor 10" di tiket dispenser gate masuk
- **Fungsi**: Menampilkan aktivitas entry, card reading, camera gate IN
- **UI**: Dashboard khusus dengan info gate masuk, status hardware, recent events
- **Events**: Hanya menerima events dari `gate_in`

### 2. Gate OUT Mode (`?gate=gate_out`)
- **Lokasi**: Monitor 10" di tiket dispenser gate keluar
- **Fungsi**: Menampilkan aktivitas exit, payment, receipt printing
- **UI**: Dashboard khusus dengan info gate keluar, payment status, recent events
- **Events**: Hanya menerima events dari `gate_out`

### 3. Monitoring Center (`?gate=all`)
- **Lokasi**: Control center / desktop admin
- **Fungsi**: Monitor semua gate, switch antar gate, control penuh
- **UI**: Dashboard lengkap dengan gate selector, statistik komprehensif
- **Events**: Menerima semua events dari semua gate

## 🔧 Konfigurasi Gate

### URL Parameters
```
http://localhost:5173?gate=gate_in    # Gate IN Mode
http://localhost:5173?gate=gate_out   # Gate OUT Mode  
http://localhost:5173?gate=all        # Monitoring Center
```

### Deteksi Otomatis
Frontend akan otomatis mendeteksi gate dari:
1. **URL Parameter**: `?gate=gate_in`
2. **Hostname**: `gate-in.parkir.local`
3. **Path**: `/gate-in/`
4. **LocalStorage**: Tersimpan dari pilihan sebelumnya

## 🖥️ Auto-Run Setup untuk Mini PC

### File Script yang Tersedia:

#### 1. Gate IN Kiosk (`auto-run-scripts/start_gate_in_kiosk.bat`)
```batch
# Jalankan di mini PC gate masuk
start_gate_in_kiosk.bat
```
- Chrome kiosk mode fullscreen
- URL: `http://localhost:5173?gate=gate_in`
- Disable F11/F12/right-click
- Auto-refresh setiap 6 jam

#### 2. Gate OUT Kiosk (`auto-run-scripts/start_gate_out_kiosk.bat`)
```batch
# Jalankan di mini PC gate keluar
start_gate_out_kiosk.bat
```
- Chrome kiosk mode fullscreen
- URL: `http://localhost:5173?gate=gate_out`
- Disable F11/F12/right-click
- Auto-refresh setiap 6 jam

#### 3. Monitoring Center (`auto-run-scripts/start_monitoring_center.bat`)
```batch
# Jalankan di control center
start_monitoring_center.bat
```
- Chrome window mode maximized
- URL: `http://localhost:5173?gate=all`
- Full controls dan configuration

## ⚙️ Setup Mini PC Auto-Run

### 1. Windows Startup Folder
```
Windows + R → shell:startup
```
Copy script yang sesuai ke folder startup:
- Gate IN: `start_gate_in_kiosk.bat`
- Gate OUT: `start_gate_out_kiosk.bat`

### 2. Windows Task Scheduler
Buat scheduled task untuk auto-run saat boot:
```
General: Run whether user is logged on or not
Triggers: At startup
Actions: Start program → [path_to_script]
Settings: Allow task to be run on demand
```

### 3. Registry Auto-Run (Advanced)
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
```
Tambah entry:
- Name: `GateInKiosk`
- Value: `C:\path\to\start_gate_in_kiosk.bat`

## 🔒 Kiosk Mode Features

### Security Features:
- **Disable Right-click**: Context menu disabled
- **Disable F12**: Developer tools disabled
- **Disable Ctrl+Shift+I**: Inspect element disabled
- **Disable Ctrl+U**: View source disabled
- **Auto Fullscreen**: Fullscreen mode saat click pertama

### Stability Features:
- **Auto Refresh**: Refresh otomatis setiap 6 jam
- **Clean Start**: Kill existing Chrome sebelum start
- **Process Isolation**: Isolated Chrome instance
- **Error Recovery**: Graceful error handling

## 📊 Dashboard Per-Gate

### Gate IN Dashboard Features:
- **Status Hardware**: Camera, Card Reader, Arduino
- **Recent Events**: Entry events only
- **Quick Actions**: Manual gate open, capture image, test card
- **Parking Count**: Real-time capacity info
- **Connection Status**: WebSocket connection indicator

### Gate OUT Dashboard Features:
- **Status Hardware**: Camera, Card Reader, Arduino, Payment Terminal
- **Recent Events**: Exit events only  
- **Payment Info**: Payment processing status
- **Receipt Status**: Receipt printer status
- **Quick Actions**: Manual gate open, capture image, test card

### Monitoring Center Features:
- **Gate Selector**: Switch between gates or monitor all
- **Comprehensive Stats**: All gates statistics
- **System Control**: Full system control
- **Logs**: Centralized logging dari semua gate
- **Emergency Controls**: Force exit, manual override

## 🌐 Network Setup untuk Multiple Monitor

### Option 1: Single Frontend Server
```
Frontend Server (Port 5173)
├── Gate IN: http://192.168.1.100:5173?gate=gate_in
├── Gate OUT: http://192.168.1.100:5173?gate=gate_out
└── Control: http://192.168.1.100:5173?gate=all
```

### Option 2: Subdomain Setup
```
gate-in.parkir.local → Auto-detect Gate IN
gate-out.parkir.local → Auto-detect Gate OUT  
control.parkir.local → Auto-detect Monitoring
```

### Option 3: Path-based Setup
```
parkir.local/gate-in → Auto-detect Gate IN
parkir.local/gate-out → Auto-detect Gate OUT
parkir.local/control → Auto-detect Monitoring
```

## 🔄 Event Filtering

### WebSocket Event Filtering:
```javascript
// Gate IN: Hanya menerima events dengan gate='gate_in'
{
  "type": "parking_event",
  "payload": {
    "event": "entry",
    "gate": "gate_in",  // ✅ Akan diproses
    "result": {...}
  }
}

// Gate OUT: Events dengan gate='gate_out'
{
  "type": "parking_event", 
  "payload": {
    "event": "exit",
    "gate": "gate_out", // ✅ Akan diproses
    "result": {...}
  }
}

// System events tetap diproses di semua mode
{
  "type": "system_status", // ✅ Selalu diproses
  "payload": {...}
}
```

## 🛠️ Development & Testing

### Test Gate Modes:
```bash
# Test Gate IN
http://localhost:5173?gate=gate_in

# Test Gate OUT  
http://localhost:5173?gate=gate_out

# Test Monitoring
http://localhost:5173?gate=all
```

### Switch Gate Programmatically:
```javascript
import { gateConfig } from './services/gateConfig.js'

// Switch to Gate IN
gateConfig.setCurrentGate('gate_in')

// Switch to Gate OUT
gateConfig.setCurrentGate('gate_out')

// Switch to Monitoring All
gateConfig.setCurrentGate('all')
```

### Check Current Gate:
```javascript
console.log('Current gate:', gateConfig.getCurrentGate())
console.log('Gate info:', gateConfig.getGateInfo())
console.log('Is gate specific:', gateConfig.isGateSpecific())
```

## 🚀 Production Deployment

### Mini PC Specs (Recommended):
- **CPU**: Intel i3 atau setara
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 128GB SSD
- **Network**: Ethernet connection (stable)
- **Monitor**: 10" touch screen 1024x768
- **OS**: Windows 10/11 IoT atau Linux

### Network Requirements:
- **Bandwidth**: 10Mbps untuk video streaming
- **Latency**: <50ms ke central hub
- **Uptime**: 99.9% requirement
- **Backup**: Cellular backup untuk critical operations

### Monitoring Setup:
```
Control Center (Desktop/Laptop)
├── Monitor Gate IN status
├── Monitor Gate OUT status  
├── View all events & logs
├── Emergency controls
└── System configuration
```

## 📱 Mobile Responsive

Dashboard telah dioptimasi untuk:
- **10" Touch Screen**: 1024x768, touch-friendly buttons
- **Desktop Monitor**: Full resolution, mouse interaction
- **Tablet**: Responsive layout 
- **Mobile**: Compact view (emergency access)

## 🔐 Security Considerations

- **Network Isolation**: Separate VLAN untuk kiosk
- **Firewall Rules**: Block unnecessary ports
- **Automatic Updates**: Controlled update schedule
- **Remote Monitoring**: Central monitoring dari control room
- **Physical Security**: Lock down kiosk hardware

---

## ✅ Setup Checklist

### Gate IN Mini PC:
- [ ] Install Windows/Linux
- [ ] Install Chrome browser
- [ ] Setup network connection
- [ ] Copy `start_gate_in_kiosk.bat` to startup
- [ ] Test kiosk mode
- [ ] Configure touch screen
- [ ] Setup physical security

### Gate OUT Mini PC:
- [ ] Install Windows/Linux
- [ ] Install Chrome browser  
- [ ] Setup network connection
- [ ] Copy `start_gate_out_kiosk.bat` to startup
- [ ] Test kiosk mode
- [ ] Configure payment terminal
- [ ] Configure receipt printer
- [ ] Setup physical security

### Control Center:
- [ ] Setup desktop/laptop
- [ ] Install Chrome browser
- [ ] Setup `start_monitoring_center.bat`
- [ ] Test all gate connections
- [ ] Configure admin access
- [ ] Setup backup monitoring

---

## 🆘 Troubleshooting

### Common Issues:

**1. Gate tidak terdeteksi:**
```
- Check URL parameter: ?gate=gate_in
- Check localStorage: selected_gate
- Manual set: gateConfig.setCurrentGate('gate_in')
```

**2. Events tidak muncul:**
```
- Check WebSocket connection
- Verify gate filtering: shouldProcessEvent()
- Check Central Hub connectivity
```

**3. Kiosk mode tidak jalan:**
```
- Check Chrome flags
- Verify script permissions  
- Test manual Chrome kiosk mode
```

**4. Auto-run gagal:**
```
- Check startup folder
- Verify script path
- Test manual script execution
- Check Windows permissions
```

---

📞 **Support**: Hubungi tim development untuk setup dan troubleshooting per-gate monitoring. 