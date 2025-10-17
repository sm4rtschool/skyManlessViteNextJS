# 📹 Panduan Penggunaan Kamera - Manless Parking System

## Overview
Sistem parkir Manless dilengkapi dengan fitur kamera yang mendukung webcam laptop dan IP camera untuk monitoring gerbang parkir secara real-time.

## Fitur Kamera

### ✅ Yang Didukung:
- **Webcam Laptop** - Kamera built-in laptop/PC
- **IP Camera HTTP** - Kamera IP dengan stream HTTP
- **IP Camera RTSP** - Kamera IP dengan protokol RTSP
- **Live Streaming** - Real-time video feed
- **Capture Image** - Ambil foto untuk dokumentasi
- **Pengaturan Dinamis** - Ganti sumber kamera tanpa restart

### 🎯 Penggunaan

#### 1. Webcam Laptop
Sistem secara otomatis akan mencoba menggunakan webcam laptop yang tersedia:
- Webcam 0 (default)
- Webcam 1, 2, dst. (jika ada multiple webcam)

#### 2. IP Camera
Untuk menggunakan IP camera, masukkan URL sesuai format:
- **HTTP Stream**: `http://192.168.1.100:8080/video`
- **RTSP Stream**: `rtsp://192.168.1.100:554/stream`

#### 3. Kontrol Kamera
- **Live View**: Tampilan video real-time
- **Capture**: Ambil foto saat diperlukan
- **Settings**: Atur sumber kamera dan parameter webcam
- **Fullscreen**: Mode layar penuh untuk monitoring

## Cara Menggunakan

### 🚀 Menjalankan Sistem
1. **Start Backend**:
   ```bash
   cd manless/backend
   python main.py
   ```

2. **Start Frontend**:
   ```bash
   cd manless/frontend
   npm run dev
   ```

3. **Akses Dashboard**: Buka http://localhost:5173

### 📊 Dashboard Kamera
1. Buka halaman Dashboard
2. Panel "Live Camera" akan menampilkan video feed
3. Status koneksi ditampilkan dengan indikator warna:
   - 🟢 **Hijau**: Terhubung dan streaming
   - 🔴 **Merah**: Terputus atau error

### ⚙️ Mengatur Sumber Kamera

#### Via Settings Panel:
1. Klik tombol **Settings** (⚙️) di panel Live Camera
2. Pilih sumber kamera yang tersedia:
   - **Webcam 0, 1, 2...** - Webcam laptop
   - **IP Camera** - Contoh IP camera
3. Atau masukkan URL kustom untuk IP camera Anda

#### Format URL IP Camera:
```
HTTP: http://[IP]:[PORT]/[PATH]
RTSP: rtsp://[IP]:[PORT]/[PATH]

Contoh:
- http://192.168.1.100:8080/video
- rtsp://192.168.1.100:554/stream1
- http://admin:password@192.168.1.100:8080/videostream.cgi
```

### 🎛️ Pengaturan Webcam
Untuk webcam laptop, Anda dapat menyesuaikan:
- **Brightness** - Kecerahan
- **Contrast** - Kontras
- **Saturation** - Saturasi warna
- **Exposure** - Eksposur

### 📸 Capture Image
1. Klik tombol **Capture** (📹) di panel Live Camera
2. Gambar akan disimpan di folder `captures/` di backend
3. Nama file menggunakan timestamp: `capture_YYYYMMDD_HHMMSS.jpg`

## Troubleshooting

### ❌ Kamera Tidak Terdeteksi
1. **Pastikan webcam terpasang** dan driver terinstall
2. **Tutup aplikasi lain** yang menggunakan kamera (Zoom, Skype, dll.)
3. **Coba ganti sumber kamera** ke index lain (0, 1, 2...)
4. **Restart browser** dan coba lagi

### ❌ IP Camera Tidak Terhubung
1. **Periksa koneksi jaringan** - pastikan IP camera dapat diakses
2. **Cek URL stream** - pastikan format URL benar
3. **Firewall/Antivirus** - pastikan tidak memblokir koneksi
4. **Username/Password** - untuk camera yang memerlukan autentikasi:
   ```
   http://username:password@192.168.1.100:8080/video
   ```

### ❌ Stream Lambat/Lag
1. **Kurangi resolusi** camera jika memungkinkan
2. **Periksa bandwidth** jaringan
3. **Tutup aplikasi** yang menggunakan bandwidth tinggi
4. **Gunakan kabel ethernet** daripada WiFi untuk IP camera

### ❌ Error "Cannot open camera"
Sistem akan beralih ke **Demo Mode** yang menampilkan:
- Frame dummy dengan informasi sistem
- Simulasi activity dengan objek bergerak
- Timestamp real-time
- Counter frame

## Tips Penggunaan

### 🎯 Optimal Performance
- **Webcam**: Gunakan resolusi 1280x720 untuk performa terbaik
- **IP Camera**: Sesuaikan quality/bitrate camera untuk mengurangi lag
- **Browser**: Chrome/Edge memiliki performa WebSocket terbaik

### 🔧 Setup IP Camera
1. **Pastikan IP camera** dalam jaringan yang sama
2. **Test URL** di browser terlebih dahulu
3. **Catat credentials** username/password jika diperlukan
4. **Dokumentasikan setting** yang berhasil untuk referensi

### 📱 Mobile Access
- Interface responsive dan dapat diakses dari mobile device
- Gunakan WiFi yang sama untuk performance terbaik
- Beberapa fitur mungkin terbatas pada mobile browser

## Integrasi dengan Hardware

### 🚧 Gate Controller
Kamera dapat diintegrasikan dengan:
- **Motion Detection** - Deteksi pergerakan kendaraan
- **License Plate Recognition** - Pembacaan plat nomor (future feature)
- **Automatic Capture** - Foto otomatis saat gate terbuka

### 💳 Card Reader
- **Capture on Card Read** - Foto otomatis saat kartu terbaca
- **Event Logging** - Dokumentasi visual untuk setiap transaksi

## Security & Privacy

### 🔒 Keamanan
- Stream video hanya dalam jaringan lokal
- Tidak ada penyimpanan video permanen
- Capture image tersimpan lokal di server

### 🛡️ Privacy
- Matikan kamera saat tidak diperlukan
- Review captured images secara berkala
- Hapus file lama jika tidak diperlukan

---

## Support
Untuk bantuan lebih lanjut:
1. Periksa log di browser console (F12)
2. Periksa log backend di terminal
3. Restart sistem jika diperlukan

**Selamat menggunakan fitur kamera Manless Parking System! 🚗📹** 