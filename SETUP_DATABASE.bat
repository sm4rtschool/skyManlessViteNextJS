@echo off
chcp 65001 >nul
cls

echo ================================================================
echo 🗄️  SETUP DATABASE SKYPARKING
echo ================================================================
echo.
echo Script ini akan:
echo 1. Membuat database 'skyparking' di MySQL
echo 2. Membuat semua tabel yang diperlukan
echo 3. Mengisi data konfigurasi awal
echo 4. (Opsional) Mengimport sample data
echo.
echo ⚠️  PERHATIAN:
echo    - Pastikan MySQL server sudah berjalan
echo    - Username: root, Password: (kosong)
echo    - Port: 3306
echo.

set /p confirm="Lanjutkan setup database? (y/n): "
if /i not "%confirm%"=="y" goto exit

echo.
echo ================================================================
echo STEP 1: Setup Database dan Tabel
echo ================================================================
echo.

REM Set PowerShell encoding dan jalankan setup
powershell -Command "$OutputEncoding = [System.Text.Encoding]::UTF8; [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; python setup_database.py"

if errorlevel 1 (
    echo.
    echo ❌ Error saat setup database!
    echo.
    pause
    goto exit
)

echo.
echo ================================================================
echo STEP 2: Import Sample Data (Opsional)
echo ================================================================
echo.
echo Sample data berisi:
echo - 8 kartu akses (employee, visitor, monthly, vip)
echo - 10 kendaraan terdaftar
echo - 14 slot parkir
echo - 8 pembayaran
echo - 12 log parkir
echo - 8 alert sistem
echo.

set /p import_sample="Import sample data? (y/n): "
if /i "%import_sample%"=="y" (
    echo.
    powershell -Command "$OutputEncoding = [System.Text.Encoding]::UTF8; [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; python import_sample_data.py"
    
    if errorlevel 1 (
        echo.
        echo ❌ Error saat import sample data!
        echo    Database tetap bisa digunakan dengan data kosong.
        echo.
    )
) else (
    echo.
    echo ℹ️  Sample data di-skip. Database siap dengan tabel kosong.
    echo.
)

echo.
echo ================================================================
echo ✅ SETUP DATABASE SELESAI!
echo ================================================================
echo.
echo 📊 Database Information:
echo    • Database: skyparking
echo    • Host: localhost:3306
echo    • User: root
echo    • Tables: 7 tabel telah dibuat
echo.
echo 💡 Langkah Selanjutnya:
echo    1. Restart backend jika sudah berjalan
echo    2. Akses frontend: http://localhost:5173
echo    3. Data akan tersinkronisasi otomatis
echo.
echo 📝 File yang telah dibuat:
echo    • create_database.sql - SQL script manual
echo    • setup_database.py - Python setup script
echo    • import_sample_data.py - Python import script
echo.

:exit
echo.
pause

