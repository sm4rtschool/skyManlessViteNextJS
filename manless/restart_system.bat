@echo off
chcp 65001 >nul
cls

echo ================================================================
echo 🔄 RESTART SISTEM PARKIR MANLESS
echo ================================================================
echo.

echo ⚠️  Peringatan: Ini akan menghentikan semua process yang sedang berjalan
echo    dan menjalankan ulang sistem secara otomatis.
echo.

set /p confirm="Apakah Anda yakin ingin restart sistem? (y/n): "

if /i not "%confirm%"=="y" (
    echo ❌ Restart dibatalkan.
    pause
    exit /b 0
)

echo.
echo 🔄 Memulai restart sistem...
echo.

echo 🔪 Menghentikan semua process...
cd /d ..
call start_centralized_system.bat 5 >nul 2>&1

echo ⏳ Menunggu 3 detik...
timeout /t 3 /nobreak >nul

echo 🚀 Menjalankan ulang sistem...
call start_centralized_system.bat 1

echo.
echo ✅ Restart selesai!
echo.
pause 