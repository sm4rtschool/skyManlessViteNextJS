@echo off
chcp 65001 >nul
cls

:menu
echo ================================================================
echo 🏢 MANLESS CONTROL CENTER - SISTEM PARKIR MANLESS
echo ================================================================
echo.
echo 📋 Menu Utama:
echo.
echo 🚀 SISTEM OPERASI:
echo   1. Jalankan Sistem Lengkap
echo   2. Jalankan Komponen Terpisah
echo   3. Hentikan Semua Process
echo   4. Restart Sistem
echo.
echo 🔍 MONITORING & DIAGNOSTIC:
echo   5. Cek Status Sistem
echo   6. Test Koneksi
echo   7. Cek Logs
echo.
echo 🔧 MAINTENANCE:
echo   8. Backup & Restore
echo   9. Maintenance Sistem
echo   10. Install Dependencies
echo.
echo 📊 INFORMASI:
echo   11. Bantuan & Dokumentasi
echo   12. Tentang Sistem
echo.
echo   0. Keluar
echo.

set /p choice="Pilih opsi (0-12): "

if "%choice%"=="1" goto run_system
if "%choice%"=="2" goto run_components
if "%choice%"=="3" goto stop_system
if "%choice%"=="4" goto restart_system
if "%choice%"=="5" goto check_status
if "%choice%"=="6" goto test_connections
if "%choice%"=="7" goto check_logs
if "%choice%"=="8" goto backup_restore
if "%choice%"=="9" goto maintenance
if "%choice%"=="10" goto install_deps
if "%choice%"=="11" goto help
if "%choice%"=="12" goto about
if "%choice%"=="0" goto exit
goto invalid

:run_system
cls
echo ================================================================
echo 🚀 MENJALANKAN SISTEM LENGKAP
echo ================================================================
echo.
cd /d ..
call start_centralized_system.bat
cd /d manless
goto menu

:run_components
cls
echo ================================================================
echo 🎛️  MENJALANKAN KOMPONEN TERPISAH
echo ================================================================
echo.
cd /d ..
call start_centralized_system.bat
cd /d manless
goto menu

:stop_system
cls
echo ================================================================
echo 🔪 MENGENTIKAN SEMUA PROCESS
echo ================================================================
echo.
cd /d ..
call start_centralized_system.bat 5
cd /d manless
echo.
echo ✅ Semua process telah dihentikan!
echo.
pause
goto menu

:restart_system
cls
echo ================================================================
echo 🔄 RESTART SISTEM
echo ================================================================
echo.
call restart_system.bat
goto menu

:check_status
cls
echo ================================================================
echo 🔍 CEK STATUS SISTEM
echo ================================================================
echo.
call check_system_status.bat
goto menu

:test_connections
cls
echo ================================================================
echo 🔗 TEST KONEKSI
echo ================================================================
echo.
call test_connections.bat
goto menu

:check_logs
cls
echo ================================================================
echo 📝 CEK LOGS
echo ================================================================
echo.

echo 📁 Logs yang tersedia:
echo.

if exist "controller\logs\controller.log" (
    echo 📄 Controller Log: controller\logs\controller.log
    echo    Ukuran: 
    for %%A in ("controller\logs\controller.log") do echo    %%~zA bytes
    echo.
    echo 📋 10 baris terakhir:
    echo ----------------------------------------
    tail -10 "controller\logs\controller.log" 2>nul || echo    (Log kosong atau tidak dapat dibaca)
    echo ----------------------------------------
) else (
    echo ❌ Controller log tidak ditemukan
)

echo.
echo 💡 Tips:
echo - Gunakan 'notepad controller\logs\controller.log' untuk melihat full log
echo - Logs akan otomatis di-cleanup setiap 30 hari
echo.
pause
goto menu

:backup_restore
cls
echo ================================================================
echo 💾 BACKUP & RESTORE
echo ================================================================
echo.
call backup_restore.bat
goto menu

:maintenance
cls
echo ================================================================
echo 🔧 MAINTENANCE SISTEM
echo ================================================================
echo.
call maintenance.bat
goto menu

:install_deps
cls
echo ================================================================
echo 📦 INSTALL DEPENDENCIES
echo ================================================================
echo.
cd /d ..
call start_centralized_system.bat 6
cd /d manless
goto menu

:help
cls
echo ================================================================
echo 📚 BANTUAN & DOKUMENTASI
echo ================================================================
echo.

echo 📖 Dokumentasi Lengkap:
echo    - README_SISTEM_TERPUSAT.md
echo    - CARA_MENJALANKAN.md
echo    - DATABASE_SETUP.md
echo.

echo 🚀 Cara Cepat Menjalankan:
echo    1. Pilih opsi 1 untuk menjalankan sistem lengkap
echo    2. Tunggu semua komponen selesai loading
echo    3. Akses frontend di http://localhost:5173
echo.

echo 🛠️  Troubleshooting:
echo    - Jika port sudah digunakan: Pilih opsi 3
echo    - Jika ada error: Pilih opsi 5 untuk cek status
echo    - Jika perlu restart: Pilih opsi 4
echo    - Jika dependencies bermasalah: Pilih opsi 10
echo.

echo 🔧 Maintenance Rutin:
echo    - Backup: Pilih opsi 8
echo    - Cleanup: Pilih opsi 9
echo    - Update: Pilih opsi 9 sub-menu 3
echo.

echo 📞 Support:
echo    - Cek logs untuk debugging
echo    - Gunakan test koneksi untuk diagnosis
echo    - Backup sebelum melakukan perubahan besar
echo.

pause
goto menu

:about
cls
echo ================================================================
echo ℹ️  TENTANG SISTEM
echo ================================================================
echo.

echo 🏢 SISTEM PARKIR MANLESS
echo    Versi: 2.0 (Arsitektur Terpusat)
echo    Platform: Windows
echo    Bahasa: Python + React
echo.

echo 🏗️  Arsitektur:
echo    Frontend (5173) ←→ Backend Central Hub (8000)
echo                           ├── Gate IN Controller (8001)
echo                           └── Gate OUT Controller (8002)
echo.

echo 📦 Komponen:
echo    ✅ Backend Central Hub - Koordinasi sistem
echo    ✅ Gate Controllers - Kontrol hardware
echo    ✅ Frontend - Interface pengguna
echo    ✅ Database - SQLite
echo    ✅ WebSocket - Real-time communication
echo.

echo 🔧 Tools yang Tersedia:
echo    ✅ Control Center - Menu utama
echo    ✅ Status Checker - Monitoring
echo    ✅ Connection Tester - Diagnostic
echo    ✅ Backup & Restore - Data management
echo    ✅ Maintenance - System upkeep
echo.

echo 📊 Status Sistem:
echo    - Virtual Environment: 
if exist "venv\Scripts\activate.bat" (
    echo ✅ Tersedia
) else (
    echo ❌ Tidak ditemukan
)
echo    - Backend: 
if exist "backend\main.py" (
    echo ✅ Tersedia
) else (
    echo ❌ Tidak ditemukan
)
echo    - Controllers: 
if exist "controller\main_gate_in.py" (
    echo ✅ Tersedia
) else (
    echo ❌ Tidak ditemukan
)
echo    - Frontend: 
if exist "frontend\package.json" (
    echo ✅ Tersedia
) else (
    echo ❌ Tidak ditemukan
)

echo.
echo 💡 Tips:
echo    - Sistem ini dirancang untuk operasi 24/7
echo    - Lakukan backup rutin untuk keamanan data
echo    - Monitor logs untuk deteksi masalah dini
echo    - Update dependencies secara berkala
echo.

pause
goto menu

:invalid
echo.
echo ❌ Pilihan tidak valid! Silakan pilih 0-12
echo.
pause
goto menu

:exit
cls
echo ================================================================
echo 👋 TERIMA KASIH MENGGUNAKAN MANLESS CONTROL CENTER
echo ================================================================
echo.
echo 💡 Tips:
echo    - Sistem dapat dijalankan ulang kapan saja
echo    - Gunakan menu 5 untuk monitoring rutin
echo    - Backup data secara berkala
echo    - Jaga sistem tetap up-to-date
echo.
echo 🚀 Selamat menggunakan Sistem Parkir Manless!
echo.
timeout /t 3 /nobreak >nul
exit 