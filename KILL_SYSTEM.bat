@echo off
chcp 65001 >nul
cls

echo ================================================================
echo 🔪 KILL SYSTEM - SISTEM PARKIR MANLESS
echo ================================================================
echo.

echo 🔪 Menghentikan semua process sistem...
echo.

REM Kill semua process di port yang digunakan
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5174') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5175') do taskkill /f /pid %%a 2>nul

echo ✅ Semua process sistem telah dihentikan!
echo.
echo 📊 Port yang dibersihkan:
echo    - Port 8000 (Backend Central Hub)
echo    - Port 8001 (Gate IN Controller)
echo    - Port 8002 (Gate OUT Controller)
echo    - Port 5173/5174/5175 (Frontend)
echo.
echo 💡 Tips:
echo    - Gunakan 'START.bat' untuk menjalankan sistem kembali
echo    - Gunakan 'RUN_SYSTEM.bat' untuk kontrol penuh
echo.
pause 