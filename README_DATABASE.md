# 🗄️ Database SkyParking - Dokumentasi Lengkap

## 📋 Daftar Isi

1. [Overview](#overview)
2. [Struktur Database](#struktur-database)
3. [Setup Database](#setup-database)
4. [Troubleshooting](#troubleshooting)
5. [Maintenance](#maintenance)

---

## Overview

Database **skyparking** adalah database MySQL yang digunakan untuk menyimpan semua data sistem parkir manless, termasuk:
- Data kendaraan dan kartu akses
- Log parkir dan transaksi
- Slot parkir dan pembayaran
- Konfigurasi sistem dan alert

### Spesifikasi
- **Database Engine**: MySQL/MariaDB
- **Character Set**: utf8mb4
- **Collation**: utf8mb4_unicode_ci
- **Host**: localhost
- **Port**: 3306
- **Username**: root
- **Password**: (kosong)

---

## Struktur Database

### Tabel Utama

#### 1. `cards` - Data Kartu Akses
Menyimpan informasi kartu akses RFID/magnetic untuk pengguna.

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| id | INT | Primary key, auto increment |
| card_id | VARCHAR(100) | ID unik kartu (UNIQUE) |
| card_type | VARCHAR(50) | Tipe kartu: employee, visitor, monthly, vip |
| owner_name | VARCHAR(100) | Nama pemilik kartu |
| is_active | BOOLEAN | Status aktif kartu |
| registered_at | DATETIME | Waktu registrasi |
| last_used | DATETIME | Waktu terakhir digunakan |

**Indexes**: card_id (UNIQUE), is_active

---

#### 2. `vehicles` - Data Kendaraan
Menyimpan informasi kendaraan yang terdaftar di sistem.

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| id | INT | Primary key, auto increment |
| license_plate | VARCHAR(20) | Nomor plat kendaraan (UNIQUE) |
| owner_name | VARCHAR(100) | Nama pemilik kendaraan |
| vehicle_type | VARCHAR(50) | Tipe: car, motorcycle, truck |
| card_id | VARCHAR(100) | ID kartu yang terhubung |
| registered_at | DATETIME | Waktu registrasi |
| is_active | BOOLEAN | Status aktif |

**Indexes**: license_plate (UNIQUE), card_id, is_active

---

#### 3. `parking_slots` - Slot Parkir
Menyimpan informasi slot parkir yang tersedia.

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| id | INT | Primary key, auto increment |
| slot_number | VARCHAR(10) | Nomor slot (UNIQUE), contoh: A001, B001 |
| slot_type | VARCHAR(20) | Tipe: car, motorcycle, disabled, vip |
| is_occupied | BOOLEAN | Status terisi/kosong |
| current_vehicle_id | INT | ID kendaraan yang parkir (jika terisi) |
| occupied_since | DATETIME | Waktu mulai parkir |

**Indexes**: slot_number (UNIQUE), is_occupied

---

#### 4. `payments` - Pembayaran Parkir
Menyimpan informasi transaksi pembayaran parkir.

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| id | INT | Primary key, auto increment |
| vehicle_id | INT | ID kendaraan |
| card_id | VARCHAR(100) | ID kartu (jika ada) |
| amount | FLOAT | Jumlah pembayaran (IDR) |
| payment_method | VARCHAR(50) | Metode: cash, card, digital, monthly_pass, vip_pass |
| payment_status | VARCHAR(20) | Status: pending, completed, failed |
| entry_time | DATETIME | Waktu masuk parkir |
| exit_time | DATETIME | Waktu keluar parkir |
| duration_hours | FLOAT | Durasi parkir dalam jam |
| created_at | DATETIME | Waktu transaksi dibuat |

**Indexes**: vehicle_id, card_id, payment_status, created_at

---

#### 5. `parking_log` - Log Sistem
Menyimpan semua event dan aktivitas sistem.

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| id | INT | Primary key, auto increment |
| timestamp | DATETIME | Waktu event |
| event_type | VARCHAR(50) | Tipe event: entry, exit, gate, system, alert |
| details | TEXT | Detail event |
| card_id | VARCHAR(100) | ID kartu terkait (jika ada) |

**Indexes**: timestamp, event_type, card_id

---

#### 6. `system_alerts` - Alert Sistem
Menyimpan alert dan notifikasi sistem.

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| id | INT | Primary key, auto increment |
| alert_type | VARCHAR(50) | Tipe: hardware, system, security, payment |
| severity | VARCHAR(20) | Tingkat: low, medium, high, critical |
| message | TEXT | Pesan alert |
| is_resolved | BOOLEAN | Status resolved |
| created_at | DATETIME | Waktu alert dibuat |
| resolved_at | DATETIME | Waktu alert diselesaikan |

**Indexes**: alert_type, severity, is_resolved, created_at

---

#### 7. `system_config` - Konfigurasi Sistem
Menyimpan konfigurasi sistem dalam format key-value.

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| id | INT | Primary key, auto increment |
| config_key | VARCHAR(100) | Key konfigurasi (UNIQUE) |
| config_value | TEXT | Value konfigurasi |
| description | TEXT | Deskripsi konfigurasi |
| updated_at | DATETIME | Waktu terakhir diupdate |

**Indexes**: config_key (UNIQUE)

**Konfigurasi Default**:
- `gate_auto_close_delay`: 5 detik
- `camera_resolution`: 1920x1080
- `parking_rate_per_hour`: 2000 IDR
- `max_parking_capacity`: 100 slot
- `card_reader_timeout`: 10 detik
- `system_timezone`: Asia/Jakarta
- `backup_enabled`: true
- `notification_email`: admin@manlessparking.com
- `gate_open_duration`: 10 detik
- `log_retention_days`: 90 hari

---

## Setup Database

### Metode 1: Menggunakan Batch File (Paling Mudah)

```batch
SETUP_DATABASE.bat
```

Script ini akan:
1. Membuat database dan tabel secara otomatis
2. Mengisi konfigurasi awal
3. Menanyakan apakah ingin import sample data

### Metode 2: Menggunakan Python Script

```bash
# Step 1: Setup database dan tabel
python setup_database.py

# Step 2: Import sample data (opsional)
python import_sample_data.py
```

### Metode 3: Manual menggunakan SQL

```bash
# Menggunakan MySQL command line
mysql -u root -p < create_database.sql

# Atau import sample data
mysql -u root -p skyparking < sample_data.sql
```

---

## Troubleshooting

### Error: Can't connect to MySQL server

**Penyebab**: MySQL service tidak berjalan

**Solusi**:
1. Buka Services (services.msc)
2. Cari "MySQL" atau "MariaDB"
3. Start service jika stopped
4. Atau restart: `net stop mysql && net start mysql`

---

### Error: Access denied for user 'root'

**Penyebab**: Password MySQL tidak sesuai

**Solusi**:
1. Update password di script:
   - `setup_database.py`: ubah `DB_PASSWORD`
   - `import_sample_data.py`: ubah `DB_PASSWORD`
2. Atau reset password MySQL:
   ```sql
   ALTER USER 'root'@'localhost' IDENTIFIED BY '';
   ```

---

### Error: Unknown database 'skyparking'

**Penyebab**: Database belum dibuat

**Solusi**:
```bash
# Jalankan setup script
python setup_database.py

# Atau buat manual
mysql -u root -e "CREATE DATABASE skyparking CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

---

### Error: Table already exists

**Penyebab**: Tabel sudah ada dari setup sebelumnya

**Solusi**: Ini normal, bisa diabaikan. Script menggunakan `CREATE TABLE IF NOT EXISTS`.

---

### Backend masih error setelah setup database

**Solusi**:
1. Restart backend:
   - Tekan Ctrl+C di terminal backend
   - Jalankan ulang: `python main.py`
2. Cek koneksi database:
   ```python
   python -c "import pymysql; pymysql.connect(host='localhost', user='root', password='', database='skyparking'); print('OK')"
   ```

---

## Maintenance

### Backup Database

#### Menggunakan Python
```python
from manless.backend.app.database.database import DatabaseManager
DatabaseManager.backup_database("backup_skyparking.sql")
```

#### Menggunakan mysqldump
```bash
mysqldump -u root --single-transaction skyparking > backup_skyparking.sql
```

---

### Restore Database

```bash
mysql -u root skyparking < backup_skyparking.sql
```

---

### Cleanup Old Logs

Menghapus log lebih dari 90 hari:

```python
from manless.backend.app.database.database import DatabaseManager
DatabaseManager.cleanup_old_logs(days=90)
```

---

### Cek Ukuran Database

```sql
USE skyparking;

SELECT 
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'skyparking'
ORDER BY (data_length + index_length) DESC;
```

---

### Optimize Tables

```sql
USE skyparking;
OPTIMIZE TABLE cards;
OPTIMIZE TABLE vehicles;
OPTIMIZE TABLE parking_log;
OPTIMIZE TABLE payments;
OPTIMIZE TABLE parking_slots;
OPTIMIZE TABLE system_alerts;
OPTIMIZE TABLE system_config;
```

---

## Query Berguna

### Cek Status Parkir Real-time

```sql
SELECT 
    slot_type,
    COUNT(*) as total_slots,
    SUM(is_occupied) as occupied,
    COUNT(*) - SUM(is_occupied) as available
FROM parking_slots 
GROUP BY slot_type;
```

---

### Revenue Harian

```sql
SELECT 
    DATE(created_at) as date,
    COUNT(*) as transactions,
    SUM(amount) as revenue
FROM payments 
WHERE payment_status = 'completed'
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 30;
```

---

### Kartu Paling Aktif

```sql
SELECT 
    c.card_id,
    c.owner_name,
    c.card_type,
    COUNT(pl.id) as usage_count,
    MAX(pl.timestamp) as last_used
FROM cards c
LEFT JOIN parking_log pl ON c.card_id = pl.card_id
WHERE c.is_active = 1
GROUP BY c.id
ORDER BY usage_count DESC
LIMIT 10;
```

---

### Alert Belum Diselesaikan

```sql
SELECT 
    alert_type,
    severity,
    message,
    created_at
FROM system_alerts 
WHERE is_resolved = 0
ORDER BY 
    FIELD(severity, 'critical', 'high', 'medium', 'low'),
    created_at DESC;
```

---

## File Terkait

- `create_database.sql` - SQL script untuk membuat database
- `setup_database.py` - Python script untuk setup database
- `import_sample_data.py` - Python script untuk import sample data
- `sample_data.sql` - Sample data untuk testing
- `SETUP_DATABASE.bat` - Batch file untuk setup otomatis
- `manless/backend/app/database/database.py` - Database connection manager
- `manless/backend/app/database/model.py` - SQLAlchemy models

---

## Support

Jika mengalami masalah:
1. Cek log backend untuk error details
2. Periksa MySQL error log
3. Pastikan semua dependencies terinstall: `pip install pymysql sqlalchemy`
4. Verifikasi koneksi database menggunakan MySQL Workbench atau phpMyAdmin

---

**Last Updated**: 2025-10-17
**Version**: 1.0

