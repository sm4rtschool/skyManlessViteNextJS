@echo off
chcp 65001 >nul
cls

echo ================================================================
echo 🔍 STATUS SISTEM PARKIR MANLESS
echo ================================================================
echo.

echo 📊 Cek port yang sedang digunakan:
echo.

echo 🔍 Port 8000 (Backend Central Hub):
netstat -aon | findstr :8000
if errorlevel 1 (
    echo ❌ Port 8000 tidak aktif
) else (
    echo ✅ Port 8000 aktif
)
echo.

echo 🔍 Port 8001 (Gate IN Controller):
netstat -aon | findstr :8001
if errorlevel 1 (
    echo ❌ Port 8001 tidak aktif
) else (
    echo ✅ Port 8001 aktif
)
echo.

echo 🔍 Port 8002 (Gate OUT Controller):
netstat -aon | findstr :8002
if errorlevel 1 (
    echo ❌ Port 8002 tidak aktif
) else (
    echo ✅ Port 8002 aktif
)
echo.

echo 🔍 Port 5173/5174/5175 (Frontend):
netstat -aon | findstr :5173
netstat -aon | findstr :5174
netstat -aon | findstr :5175
if errorlevel 1 (
    echo ❌ Port Frontend tidak aktif
) else (
    echo ✅ Port Frontend aktif
)
echo.

echo 📁 Cek file penting:
echo.

if exist "venv\Scripts\activate.bat" (
    echo ✅ Virtual environment ditemukan
) else (
    echo ❌ Virtual environment tidak ditemukan
)

if exist "backend\main.py" (
    echo ✅ Backend main.py ditemukan
) else (
    echo ❌ Backend main.py tidak ditemukan
)

if exist "controller\main_gate_in.py" (
    echo ✅ Gate IN controller ditemukan
) else (
    echo ❌ Gate IN controller tidak ditemukan
)

if exist "controller\main_gate_out.py" (
    echo ✅ Gate OUT controller ditemukan
) else (
    echo ❌ Gate OUT controller tidak ditemukan
)

if exist "frontend\package.json" (
    echo ✅ Frontend package.json ditemukan
) else (
    echo ❌ Frontend package.json tidak ditemukan
)

echo.
echo 💡 Tips:
echo - Jalankan 'start_centralized_system.bat' untuk menjalankan sistem
echo - Gunakan opsi 5 untuk menghentikan semua process
echo - Gunakan opsi 6 untuk install dependencies
echo.
pause 