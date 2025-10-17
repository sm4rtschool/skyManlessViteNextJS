# 🚀 Cara Menjalankan Sistem Parkir Manless

## ✅ **Cara Mudah (Manual - Recommended)**

### **Langkah 1: Buka 2 PowerShell/Terminal**

1. **Terminal 1 - Untuk Backend Python:**
   ```powershell
   cd C:\skyparking\manless\manless\backend
   python run_backend.py
   ```

2. **Terminal 2 - Untuk Frontend React:**
   ```powershell
   cd C:\skyparking\manless\manless\frontend  
   npm run dev
   ```

### **Langkah 2: Akses Aplikasi**
- **Frontend (Dashboard):** http://localhost:5173
- **Backend (API):** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

---

## 🔧 **Cara Otomatis (Menggunakan Script)**

Jika ingin menggunakan script otomatis:
```powershell
.\start_system.ps1
```

---

## ❗ **Troubleshooting**

### **Jika Python tidak ditemukan:**
```powershell
# Refresh PATH
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
python --version
```

### **Jika ada error CSS/dependencies:**
```powershell
cd manless\frontend
npm install
npm run dev
```

### **Jika port sudah digunakan:**
- Backend: Ubah port di `run_backend.py` (line: `port=8000`)
- Frontend: Ubah port dengan `npm run dev -- --port 3000`

---

## 📱 **Fitur Aplikasi**

### **Frontend (React):**
- ✅ Dashboard sistem parkir
- ✅ Live camera view
- ✅ Card reader interface  
- ✅ Log viewer kendaraan
- ✅ Gate control
- ✅ System statistics
- ✅ Responsive design

### **Backend (Python):**
- ✅ REST API endpoints
- ✅ WebSocket real-time updates
- ✅ Hardware controllers (camera, Arduino, card reader)
- ✅ Database management
- ✅ Health monitoring

---

## 💡 **Tips:**
- **Untuk development:** Gunakan cara manual (2 terminal)
- **Untuk demo/produksi:** Gunakan script otomatis
- **Hot reload:** Frontend otomatis refresh saat ada perubahan code
- **Stop aplikasi:** Tekan `Ctrl+C` di masing-masing terminal

---

## 🆘 **Jika Masih Bermasalah:**

1. **Pastikan dependencies terinstall:**
   ```powershell
   python --version  # Harus ada Python 3.12+
   node --version    # Harus ada Node.js 18+
   ```

2. **Install dependencies:**
   ```powershell
   # Backend
   cd manless\backend
   pip install -r requirements.txt
   
   # Frontend  
   cd manless\frontend
   npm install
   ```

3. **Test manual:**
   ```powershell
   # Test backend
   curl http://localhost:8000/health
   
   # Test frontend
   curl http://localhost:5173
   ``` 