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
    echo 2. Buka Frontend
    echo 0. Keluar
    echo.
    set /p choice="Pilih opsi (0-2): "
    
    if "%choice%"=="1" goto restart
    if "%choice%"=="2" goto open_frontend
    if "%choice%"=="0" goto exit
    goto exit
)

echo ✅ Sistem belum berjalan, memulai sistem...
echo.

REM Jalankan sistem lengkap
call RUN_SYSTEM.bat 1

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
echo    - Gunakan 'RUN_SYSTEM.bat' untuk kontrol penuh
echo    - Gunakan 'KILL_SYSTEM.bat' untuk menghentikan sistem
echo.
pause
goto exit

:restart
echo.
echo 🔄 Restart sistem...
call KILL_SYSTEM.bat
timeout /t 3 /nobreak >nul
call RUN_SYSTEM.bat 1
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