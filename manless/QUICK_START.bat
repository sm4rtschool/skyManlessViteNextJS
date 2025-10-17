@echo off
chcp 65001 >nul
cls

echo ================================================================
echo ⚡ QUICK START - SISTEM PARKIR MANLESS
echo ================================================================
echo.

echo 🚀 Memulai sistem secara otomatis...
echo.

REM Cek apakah sistem sudah berjalan
echo 🔍 Cek status sistem...
netstat -aon | findstr :8000 >nul
if not errorlevel 1 (
    echo ⚠️  Sistem sudah berjalan!
    echo.
    echo Pilihan:
    echo 1. Restart sistem
    echo 2. Buka Control Center
    echo 3. Buka Frontend
    echo 0. Keluar
    echo.
    set /p choice="Pilih opsi (0-3): "
    
    if "%choice%"=="1" goto restart
    if "%choice%"=="2" goto control_center
    if "%choice%"=="3" goto open_frontend
    if "%choice%"=="0" goto exit
    goto exit
)

echo ✅ Sistem belum berjalan, memulai sistem...
echo.

REM Jalankan sistem lengkap
cd /d ..
call start_centralized_system.bat 1
cd /d manless

echo.
echo ⏳ Menunggu sistem siap...
timeout /t 10 /nobreak >nul

echo.
echo 🌐 Membuka frontend di browser...
start http://localhost:5173

echo.
echo ✅ Sistem berhasil dijalankan!
echo.
echo 📊 Akses sistem:
echo    Frontend: http://localhost:5173
echo    Backend: http://localhost:8000
echo    Gate IN: http://localhost:8001
echo    Gate OUT: http://localhost:8002
echo.
echo 💡 Tips:
echo    - Gunakan 'manless_control_center.bat' untuk kontrol penuh
echo    - Gunakan 'check_system_status.bat' untuk monitoring
echo    - Gunakan 'restart_system.bat' untuk restart
echo.
pause
goto exit

:restart
echo.
echo 🔄 Restart sistem...
call restart_system.bat
goto exit

:control_center
echo.
echo 🏢 Membuka Control Center...
call manless_control_center.bat
goto exit

:open_frontend
echo.
echo 🌐 Membuka frontend...
start http://localhost:5173
goto exit

:exit
echo.
echo 👋 Terima kasih telah menggunakan Quick Start!
echo. 