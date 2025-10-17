@echo off
chcp 65001 >nul
cls

echo ================================================================
echo 🏢 SISTEM PARKIR MANLESS - START SYSTEM
echo ================================================================
echo.

echo 🔍 Cek struktur sistem...
echo.

REM Cek apakah kita di root directory
if exist "manless\backend\main.py" (
    echo ✅ Struktur sistem ditemukan
    set ROOT_DIR=.
) else if exist "backend\main.py" (
    echo ✅ Struktur sistem ditemukan (dalam folder manless)
    set ROOT_DIR=manless
) else (
    echo ❌ Struktur sistem tidak ditemukan!
    echo    Pastikan file ini dijalankan dari root directory sistem.
    pause
    exit /b 1
)

echo 📁 Root directory: %ROOT_DIR%
echo.

REM Cek virtual environment
if not exist "%ROOT_DIR%\venv\Scripts\activate.bat" (
    echo ⚠️  Virtual environment tidak ditemukan!
    echo    Membuat virtual environment baru...
    python -m venv %ROOT_DIR%\venv
    if errorlevel 1 (
        echo ❌ Gagal membuat virtual environment!
        echo    Pastikan Python sudah terinstall dengan benar.
        pause
        exit /b 1
    )
    echo ✅ Virtual environment berhasil dibuat!
)

REM Cek Node.js dan npm
where node >nul 2>nul
if errorlevel 1 (
    echo ❌ Node.js tidak ditemukan!
    echo    Silakan install Node.js terlebih dahulu.
    pause
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo ❌ npm tidak ditemukan!
    echo    Silakan install npm terlebih dahulu.
    pause
    exit /b 1
)

echo.
echo Pilihan menjalankan sistem:
echo 1. Jalankan semua (Backend + Controllers + Frontend)
echo 2. Jalankan Backend saja
echo 3. Jalankan Controllers saja
echo 4. Jalankan Frontend saja
echo 5. Kill semua process
echo 6. Install dependencies
echo 0. Keluar
echo.

set /p choice="Pilih opsi (0-6): "

if "%choice%"=="1" goto run_all
if "%choice%"=="2" goto run_backend
if "%choice%"=="3" goto run_controllers
if "%choice%"=="4" goto run_frontend
if "%choice%"=="5" goto kill_processes
if "%choice%"=="6" goto install_deps
if "%choice%"=="0" goto exit
goto invalid

:install_deps
echo.
echo 📦 Installing dependencies...
echo.

echo 📦 Installing Backend dependencies...
call %ROOT_DIR%\venv\Scripts\activate.bat
cd /d %ROOT_DIR%\backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Gagal install backend dependencies!
    pause
    goto exit
)

echo 📦 Installing Frontend dependencies...
cd /d %ROOT_DIR%\frontend
npm install
if errorlevel 1 (
    echo ❌ Gagal install frontend dependencies!
    pause
    goto exit
)

echo ✅ Semua dependencies berhasil diinstall!
echo.
pause
goto exit

:run_all
echo.
echo 🚀 Menjalankan semua komponen sistem...
echo.

REM Kill existing processes first
call :kill_processes_silent

echo 📡 Starting Backend Central Hub (port 8000)...
call %ROOT_DIR%\venv\Scripts\activate.bat
start "Backend Central Hub" cmd /k "cd /d %ROOT_DIR%\backend && python main.py"

timeout /t 5 /nobreak >nul

echo 🎮 Starting Gate IN Controller (port 8001)...
start "Gate IN Controller" cmd /k "cd /d %ROOT_DIR%\controller && python main_gate_in.py"

timeout /t 3 /nobreak >nul

echo 🎮 Starting Gate OUT Controller (port 8002)...
start "Gate OUT Controller" cmd /k "cd /d %ROOT_DIR%\controller && python main_gate_out.py"

timeout /t 3 /nobreak >nul

echo 🌐 Starting Frontend (port 5173/5174/5175)...
cd /d %ROOT_DIR%\frontend
start "Frontend" cmd /k "npm run dev"

echo.
echo ✅ Semua komponen sistem telah dijalankan!
echo.
echo 🌐 Frontend: http://localhost:5173 (atau 5174/5175)
echo 📡 Backend: http://localhost:8000
echo 🎮 Gate IN: http://localhost:8001
echo 🎮 Gate OUT: http://localhost:8002
echo.
pause
goto exit

:run_backend
echo.
echo 📡 Menjalankan Backend Central Hub saja...
echo.

REM Kill existing backend process
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a 2>nul

call %ROOT_DIR%\venv\Scripts\activate.bat
start "Backend Central Hub" cmd /k "cd /d %ROOT_DIR%\backend && python main.py"
echo ✅ Backend Central Hub dijalankan di port 8000
echo.
pause
goto exit

:run_controllers
echo.
echo 🎮 Menjalankan Gate Controllers saja...
echo.

REM Kill existing controller processes
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /f /pid %%a 2>nul

echo 🎮 Starting Gate IN Controller (port 8001)...
start "Gate IN Controller" cmd /k "cd /d %ROOT_DIR%\controller && python main_gate_in.py"
timeout /t 3 /nobreak >nul
echo 🎮 Starting Gate OUT Controller (port 8002)...
start "Gate OUT Controller" cmd /k "cd /d %ROOT_DIR%\controller && python main_gate_out.py"
echo ✅ Gate Controllers dijalankan di port 8001 dan 8002
echo.
pause
goto exit

:run_frontend
echo.
echo 🌐 Menjalankan Frontend saja...
echo.

REM Kill existing frontend process
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5174') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5175') do taskkill /f /pid %%a 2>nul

cd /d %ROOT_DIR%\frontend
start "Frontend" cmd /k "npm run dev"
echo ✅ Frontend dijalankan di port 5173 (atau 5174/5175)
echo.
pause
goto exit

:kill_processes
echo.
echo 🔪 Menghentikan semua process di port yang digunakan...
echo.
call :kill_processes_silent
echo ✅ Semua process di port 8000, 8001, 8002, 5173, 5174, 5175 telah dihentikan
echo.
pause
goto exit

:kill_processes_silent
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5174') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5175') do taskkill /f /pid %%a 2>nul
goto :eof

:invalid
echo.
echo ❌ Pilihan tidak valid! Silakan pilih 0-6
echo.
pause
goto exit

:exit
echo.
echo 👋 Terima kasih telah menggunakan Sistem Parkir Manless!
echo. 