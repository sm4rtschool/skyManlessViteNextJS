# 🏢 SISTEM PARKIR MANLESS - ARSITEKTUR TERPUSAT

## 📋 Deskripsi Sistem

Sistem parkir manless dengan arsitektur terpusat yang terdiri dari:
- **Backend Central Hub** (port 8000) - Pusat kontrol dan koordinasi
- **Gate IN Controller** (port 8001) - Kontrol gate masuk
- **Gate OUT Controller** (port 8002) - Kontrol gate keluar  
- **Frontend** (port 5173/5174/5175) - Interface pengguna

## 🚀 Cara Menjalankan Sistem

### 1. File Batch Utama

#### `start_centralized_system.bat`
File utama untuk menjalankan sistem dengan pilihan:

- **Opsi 1**: Jalankan semua komponen (Backend + Controllers + Frontend)
- **Opsi 2**: Jalankan Backend Central Hub saja
- **Opsi 3**: Jalankan Gate Controllers saja
- **Opsi 4**: Jalankan Frontend saja
- **Opsi 5**: Kill semua process di port yang digunakan
- **Opsi 6**: Install dependencies (Backend + Frontend)
- **Opsi 0**: Keluar

### 2. File Batch Pendukung

#### `check_system_status.bat`
Untuk mengecek status sistem:
- Cek port yang sedang digunakan
- Cek keberadaan file-file penting
- Cek virtual environment

#### `restart_system.bat`
Untuk restart otomatis sistem:
- Menghentikan semua process
- Menjalankan ulang sistem secara otomatis

## 📦 Prerequisites

### Software yang Diperlukan:
1. **Python 3.8+** - Untuk backend dan controllers
2. **Node.js 16+** - Untuk frontend
3. **npm** - Package manager untuk Node.js

### Dependencies:
- Backend: Akan diinstall otomatis via `requirements.txt`
- Frontend: Akan diinstall otomatis via `npm install`

## 🔧 Setup Awal

### 1. Install Dependencies
```bash
# Jalankan file batch dan pilih opsi 6
start_centralized_system.bat
```

### 2. Virtual Environment
Sistem akan otomatis membuat virtual environment jika belum ada.

## 🌐 Akses Sistem

Setelah sistem berjalan:

- **Frontend**: http://localhost:5173 (atau 5174/5175)
- **Backend API**: http://localhost:8000
- **Gate IN**: http://localhost:8001
- **Gate OUT**: http://localhost:8002

## 🛠️ Troubleshooting

### Masalah Umum:

#### 1. Port Sudah Digunakan
```bash
# Gunakan opsi 5 untuk kill semua process
start_centralized_system.bat
```

#### 2. Virtual Environment Tidak Ada
Sistem akan otomatis membuat virtual environment baru.

#### 3. Dependencies Belum Terinstall
```bash
# Gunakan opsi 6 untuk install dependencies
start_centralized_system.bat
```

#### 4. Node.js/NPM Tidak Ditemukan
- Install Node.js dari https://nodejs.org/
- Pastikan Node.js dan npm ada di PATH

### Cek Status Sistem:
```bash
check_system_status.bat
```

### Restart Sistem:
```bash
restart_system.bat
```

## 📁 Struktur File

```
manless/
├── start_centralized_system.bat    # File utama
├── check_system_status.bat         # Cek status
├── restart_system.bat              # Restart sistem
├── backend/                        # Backend Central Hub
│   ├── main.py
│   └── requirements.txt
├── controller/                     # Gate Controllers
│   ├── main_gate_in.py
│   └── main_gate_out.py
├── frontend/                       # Frontend React
│   ├── package.json
│   └── src/
└── venv/                          # Virtual Environment
```

## 🔄 Workflow Sistem

1. **Start Backend Central Hub** (port 8000)
2. **Start Gate Controllers** (port 8001, 8002)
3. **Start Frontend** (port 5173)
4. **Sistem siap digunakan**

## 💡 Tips Penggunaan

- Selalu gunakan opsi 5 sebelum menjalankan sistem baru
- Gunakan `check_system_status.bat` untuk debugging
- Jika ada masalah, gunakan `restart_system.bat`
- Pastikan semua port (8000, 8001, 8002, 5173) tidak digunakan aplikasi lain

## 🆘 Support

Jika mengalami masalah:
1. Jalankan `check_system_status.bat`
2. Restart sistem dengan `restart_system.bat`
3. Periksa log di masing-masing terminal window
4. Pastikan semua prerequisites terinstall dengan benar 