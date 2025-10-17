@echo off
chcp 65001 >nul
cls

echo ================================================================
echo 🔗 TEST KONEKSI SISTEM PARKIR MANLESS
echo ================================================================
echo.

echo 🔍 Testing koneksi antar komponen...
echo.

echo 📡 Testing Backend Central Hub (port 8000)...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend Central Hub tidak merespon
) else (
    echo ✅ Backend Central Hub merespon
)

echo 🎮 Testing Gate IN Controller (port 8001)...
curl -s http://localhost:8001/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Gate IN Controller tidak merespon
) else (
    echo ✅ Gate IN Controller merespon
)

echo 🎮 Testing Gate OUT Controller (port 8002)...
curl -s http://localhost:8002/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Gate OUT Controller tidak merespon
) else (
    echo ✅ Gate OUT Controller merespon
)

echo 🌐 Testing Frontend (port 5173)...
curl -s http://localhost:5173 >nul 2>&1
if errorlevel 1 (
    echo ❌ Frontend tidak merespon
) else (
    echo ✅ Frontend merespon
)

echo.
echo 🔗 Testing WebSocket connections...
echo.

echo 📡 Testing WebSocket Backend...
curl -s -I http://localhost:8000/ws >nul 2>&1
if errorlevel 1 (
    echo ❌ WebSocket Backend tidak tersedia
) else (
    echo ✅ WebSocket Backend tersedia
)

echo 🎮 Testing WebSocket Gate IN...
curl -s -I http://localhost:8001/ws >nul 2>&1
if errorlevel 1 (
    echo ❌ WebSocket Gate IN tidak tersedia
) else (
    echo ✅ WebSocket Gate IN tersedia
)

echo 🎮 Testing WebSocket Gate OUT...
curl -s -I http://localhost:8002/ws >nul 2>&1
if errorlevel 1 (
    echo ❌ WebSocket Gate OUT tidak tersedia
) else (
    echo ✅ WebSocket Gate OUT tersedia
)

echo.
echo 📊 Ringkasan Status:
echo.

netstat -aon | findstr :8000 >nul && echo ✅ Port 8000: Backend Central Hub
netstat -aon | findstr :8001 >nul && echo ✅ Port 8001: Gate IN Controller  
netstat -aon | findstr :8002 >nul && echo ✅ Port 8002: Gate OUT Controller
netstat -aon | findstr :5173 >nul && echo ✅ Port 5173: Frontend

echo.
echo 💡 Tips:
echo - Jika ada komponen yang tidak merespon, restart sistem
echo - Gunakan 'check_system_status.bat' untuk detail lebih lanjut
echo - Gunakan 'restart_system.bat' untuk restart otomatis
echo.
pause 