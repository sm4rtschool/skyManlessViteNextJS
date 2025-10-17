Saya mempunyai program parkir menggunakan delphi 7. Saya ingin convert ke python yang akan menampilkan live view camera, komunikasi serial dengan arduino, log view untuk mencatat kendaraan datang, tekan tombol, buka gate, kendaraan sudah lewat gate, capture camera, posting data ke database. Tolong bantu buatkan, 

saya ingin solusi yang lebih tepat dengan arsitektur lengkap:

1. Frontend (React):

javascript- Interface pengguna
- Tampilan live camera
- Display log
- Status sistem

outputnya kira-kira seperti ini:
- Live camera view dengan WebSocket
- Card reader interface
- Log viewer
- Gate control
- Responsive design dengan Tailwind CSS

2. Backend (Python):

python- Akses hardware (kamera, card reader, Arduino)
- Manajemen database
- Business logic
- File handling
- API untuk frontend

outputnya kira-kira seperti ini:
- FastAPI untuk API dan WebSocket
- Kontroller untuk hardware (kamera, card reader, Arduino)
- Database SQLite dengan SQLAlchemy
- Sistem logging

3. Database mysql:

- Data kendaraan
- Data kartu
- Konfigurasi sistem

# ini table existing yang sudah saya buat

CREATE TABLE `parking_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime DEFAULT NULL,
  `event_type` varchar(50) DEFAULT NULL,
  `details` text DEFAULT NULL,
  `card_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

kamu buatkan saja desain table mysql sisanya untuk table

- Data kendaraan
- Data kartu
- Konfigurasi sistem

4. Hardware:

- Kamera
- Smart card reader
- Arduino untuk gate
- Sensor-sensor

Rekomendasi implementasi:

Gunakan Python untuk backend dengan:

FastAPI/Flask untuk API
OpenCV untuk kamera
PySerial untuk Arduino
SQL Alchemy untuk database
pyscard untuk card reader


React untuk frontend dengan:

Axios untuk API calls
WebSocket untuk real-time updates
Material-UI/Tailwind untuk UI


Komunikasi:

WebSocket untuk real-time updates
REST API untuk operasi CRUD
Serial communication untuk hardware

Contoh struktur project yang disarankan:
parking-system/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── services/        # API services
│   │   └── utils/           # Helper functions
│   └── package.json
│
├── backend/                  # Python backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── hardware/       # Hardware controllers
│   │   ├── models/         # Database models
│   │   └── utils/          # Utility functions
│   ├── requirements.txt
│   └── main.py
│
└── database/                # Database migrations & scripts