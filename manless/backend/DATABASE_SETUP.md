# Setup Database MySQL untuk SkyParking

## Prasyarat

1. **MySQL Server** harus terinstall dan berjalan
2. **Python dependencies** sudah terinstall (run `pip install -r requirements.txt`)

## Konfigurasi Database

Database menggunakan konfigurasi berikut:
- **Host**: localhost
- **Port**: 3306
- **Username**: root
- **Password**: (kosong)
- **Database Name**: skyparking

## Langkah Setup

### 1. Pastikan MySQL Server Berjalan

Pastikan MySQL server sudah berjalan di port 3306.

### 2. Jalankan Setup Script

```bash
cd manless/backend
python setup_mysql.py
```

Script akan:
- Mengecek koneksi ke MySQL server
- Membuat database `skyparking` (jika belum ada)
- Membuat semua tabel yang diperlukan
- Menambahkan data konfigurasi awal

### 3. Verifikasi Setup

Setelah setup berhasil, Anda dapat mengecek database:

```sql
USE skyparking;
SHOW TABLES;
```

Tabel yang akan dibuat:
- `parking_log` - Log semua event sistem
- `vehicles` - Data kendaraan terdaftar
- `cards` - Data kartu akses
- `system_config` - Konfigurasi sistem
- `parking_slots` - Slot parkir (future feature)
- `payments` - Data pembayaran (future feature)
- `system_alerts` - Alert sistem (future feature)

## Troubleshooting

### Error: Access denied for user 'root'

Pastikan user `root` MySQL tidak memiliki password, atau update konfigurasi di `app/database/database.py`:

```python
DATABASE_URL = "mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/skyparking"
```

### Error: Can't connect to MySQL server

1. Pastikan MySQL service berjalan
2. Cek port 3306 tidak diblokir firewall
3. Pastikan MySQL dikonfigurasi untuk menerima koneksi lokal

### Error: Unknown database 'skyparking'

Script `setup_mysql.py` akan otomatis membuat database. Jika masih error, buat manual:

```sql
CREATE DATABASE skyparking CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Backup dan Restore

### Backup Database

```python
from app.database.database import DatabaseManager
DatabaseManager.backup_database("backup_skyparking.sql")
```

### Restore Database

```bash
mysql -u root -p skyparking < backup_skyparking.sql
```

## Environment Variables

Untuk production, gunakan environment variables:

```bash
export DATABASE_URL="mysql+pymysql://user:password@host:port/database"
```

## Migrasi dari SQLite

Jika sebelumnya menggunakan SQLite, data perlu dimigrasikan manual ke MySQL. Script migrasi akan dibuat jika diperlukan. 