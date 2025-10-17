@echo off
chcp 65001 >nul
cls

echo ================================================================
echo 🔍 CHECK STATUS - SISTEM PARKIR MANLESS
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

REM Cek struktur sistem
if exist "manless\backend\main.py" (
    echo ✅ Struktur sistem ditemukan (root directory)
    set ROOT_DIR=.
) else if exist "backend\main.py" (
    echo ✅ Struktur sistem ditemukan (dalam folder manless)
    set ROOT_DIR=manless
) else (
    echo ❌ Struktur sistem tidak ditemukan!
    goto end
)

if exist "%ROOT_DIR%\venv\Scripts\activate.bat" (
    echo ✅ Virtual environment ditemukan
) else (
    echo ❌ Virtual environment tidak ditemukan
)

if exist "%ROOT_DIR%\backend\main.py" (
    echo ✅ Backend main.py ditemukan
) else (
    echo ❌ Backend main.py tidak ditemukan
)

if exist "%ROOT_DIR%\controller\main_gate_in.py" (
    echo ✅ Gate IN controller ditemukan
) else (
    echo ❌ Gate IN controller tidak ditemukan
)

if exist "%ROOT_DIR%\controller\main_gate_out.py" (
    echo ✅ Gate OUT controller ditemukan
) else (
    echo ❌ Gate OUT controller tidak ditemukan
)

if exist "%ROOT_DIR%\frontend\package.json" (
    echo ✅ Frontend package.json ditemukan
) else (
    echo ❌ Frontend package.json tidak ditemukan
)

:end
echo.
echo 💡 Tips:
echo - Gunakan 'START.bat' untuk menjalankan sistem
echo - Gunakan 'RUN_SYSTEM.bat' untuk kontrol penuh
echo - Gunakan 'KILL_SYSTEM.bat' untuk menghentikan sistem
echo.
pause 