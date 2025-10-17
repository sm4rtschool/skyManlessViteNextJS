@echo off
chcp 65001 >nul
cls

echo ================================================================
echo 🔧 MAINTENANCE SISTEM PARKIR MANLESS
echo ================================================================
echo.

echo Pilihan maintenance:
echo 1. Cleanup logs (hapus log lama)
echo 2. Optimize database
echo 3. Update dependencies
echo 4. Cleanup temporary files
echo 5. Check disk space
echo 6. Full maintenance (semua di atas)
echo 0. Keluar
echo.

set /p choice="Pilih opsi (0-6): "

if "%choice%"=="1" goto cleanup_logs
if "%choice%"=="2" goto optimize_db
if "%choice%"=="3" goto update_deps
if "%choice%"=="4" goto cleanup_temp
if "%choice%"=="5" goto check_disk
if "%choice%"=="6" goto full_maintenance
if "%choice%"=="0" goto exit
goto invalid

:cleanup_logs
echo.
echo 🧹 Cleanup logs...
echo.

REM Stop sistem dulu
echo 🔪 Menghentikan sistem...
cd /d ..
call start_centralized_system.bat 5 >nul 2>&1
cd /d manless

REM Cleanup logs yang lebih dari 30 hari
echo 📝 Menghapus log lama (lebih dari 30 hari)...
forfiles /p "controller\logs" /s /m *.log /d -30 /c "cmd /c del @path" 2>nul
echo ✅ Log lama berhasil dihapus

REM Cleanup captures yang lebih dari 7 hari
echo 📸 Menghapus capture lama (lebih dari 7 hari)...
forfiles /p "backend\captures" /s /m *.jpg /d -7 /c "cmd /c del @path" 2>nul
forfiles /p "controller\captures" /s /m *.jpg /d -7 /c "cmd /c del @path" 2>nul
echo ✅ Capture lama berhasil dihapus

echo.
echo ✅ Cleanup logs selesai!
echo.
pause
goto exit

:optimize_db
echo.
echo 📊 Optimize database...
echo.

REM Stop backend dulu
echo 🔪 Menghentikan backend...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a 2>nul

if exist "backend\parking_system.db" (
    echo 🔧 Optimizing database...
    
    REM Buat backup dulu
    copy "backend\parking_system.db" "backend\parking_system_backup.db"
    
    REM Optimize dengan SQLite
    echo VACUUM; | sqlite3 "backend\parking_system.db"
    echo ANALYZE; | sqlite3 "backend\parking_system.db"
    
    echo ✅ Database berhasil dioptimize
) else (
    echo ❌ Database tidak ditemukan!
)

echo.
pause
goto exit

:update_deps
echo.
echo 📦 Update dependencies...
echo.

echo 📦 Updating Backend dependencies...
call venv\Scripts\activate.bat
cd /d backend
pip install --upgrade -r requirements.txt
if errorlevel 1 (
    echo ❌ Gagal update backend dependencies!
) else (
    echo ✅ Backend dependencies berhasil diupdate
)

echo 📦 Updating Frontend dependencies...
cd /d frontend
npm update
if errorlevel 1 (
    echo ❌ Gagal update frontend dependencies!
) else (
    echo ✅ Frontend dependencies berhasil diupdate
)

echo.
echo ✅ Update dependencies selesai!
echo.
pause
goto exit

:cleanup_temp
echo.
echo 🗑️  Cleanup temporary files...
echo.

REM Cleanup Python cache
echo 🐍 Menghapus Python cache...
for /r . %%i in (__pycache__) do if exist "%%i" rmdir /s /q "%%i" 2>nul
for /r . %%i in (*.pyc) do if exist "%%i" del "%%i" 2>nul
echo ✅ Python cache berhasil dihapus

REM Cleanup Node modules cache
echo 📦 Menghapus Node modules cache...
if exist "frontend\node_modules\.cache" (
    rmdir /s /q "frontend\node_modules\.cache" 2>nul
    echo ✅ Node modules cache berhasil dihapus
)

REM Cleanup temporary files
echo 📄 Menghapus temporary files...
del /q *.tmp 2>nul
del /q *.temp 2>nul
echo ✅ Temporary files berhasil dihapus

echo.
echo ✅ Cleanup temporary files selesai!
echo.
pause
goto exit

:check_disk
echo.
echo 💾 Check disk space...
echo.

echo 📊 Disk space usage:
echo.

REM Check current directory space
for /f "tokens=3" %%a in ('dir /-c ^| findstr "bytes free"') do set free_space=%%a
for /f "tokens=3" %%a in ('dir /-c ^| findstr "bytes total"') do set total_space=%%a

echo 💾 Total space: %total_space%
echo 💾 Free space: %free_space%

REM Calculate percentage
set /a free_gb=%free_space:~0,-9%
if %free_gb% lss 1 (
    echo ⚠️  Disk space hampir penuh! (%free_gb% GB tersisa)
) else (
    echo ✅ Disk space masih cukup (%free_gb% GB tersisa)
)

echo.
echo 📁 Folder sizes:
echo.

REM Check folder sizes
for %%f in (backend controller frontend) do (
    if exist "%%f" (
        for /f "tokens=3" %%s in ('dir "%%f" /s ^| findstr "File(s)"') do (
            echo 📁 %%f: %%s files
        )
    )
)

echo.
pause
goto exit

:full_maintenance
echo.
echo 🔧 Full maintenance sistem...
echo.

echo ⚠️  Peringatan: Ini akan melakukan semua maintenance!
echo    Sistem akan dihentikan sementara.
echo.
set /p confirm="Apakah Anda yakin ingin melakukan full maintenance? (y/n): "

if /i not "%confirm%"=="y" (
    echo ❌ Full maintenance dibatalkan.
    pause
    goto exit
)

echo.
echo 🔧 Memulai full maintenance...
echo.

REM Stop semua process
echo 🔪 Menghentikan semua process...
cd /d ..
call start_centralized_system.bat 5 >nul 2>&1
cd /d manless

REM Cleanup logs
echo 🧹 Cleanup logs...
call :cleanup_logs_silent

REM Optimize database
echo 📊 Optimize database...
call :optimize_db_silent

REM Update dependencies
echo 📦 Update dependencies...
call :update_deps_silent

REM Cleanup temp files
echo 🗑️  Cleanup temporary files...
call :cleanup_temp_silent

echo.
echo ✅ Full maintenance selesai!
echo.
pause
goto exit

:cleanup_logs_silent
forfiles /p "controller\logs" /s /m *.log /d -30 /c "cmd /c del @path" 2>nul
forfiles /p "backend\captures" /s /m *.jpg /d -7 /c "cmd /c del @path" 2>nul
forfiles /p "controller\captures" /s /m *.jpg /d -7 /c "cmd /c del @path" 2>nul
goto :eof

:optimize_db_silent
if exist "backend\parking_system.db" (
    copy "backend\parking_system.db" "backend\parking_system_backup.db"
    echo VACUUM; | sqlite3 "backend\parking_system.db"
    echo ANALYZE; | sqlite3 "backend\parking_system.db"
)
goto :eof

:update_deps_silent
call venv\Scripts\activate.bat
cd /d backend
pip install --upgrade -r requirements.txt >nul 2>&1
cd /d frontend
npm update >nul 2>&1
goto :eof

:cleanup_temp_silent
for /r . %%i in (__pycache__) do if exist "%%i" rmdir /s /q "%%i" 2>nul
for /r . %%i in (*.pyc) do if exist "%%i" del "%%i" 2>nul
if exist "frontend\node_modules\.cache" rmdir /s /q "frontend\node_modules\.cache" 2>nul
del /q *.tmp 2>nul
del /q *.temp 2>nul
goto :eof

:invalid
echo.
echo ❌ Pilihan tidak valid! Silakan pilih 0-6
echo.
pause
goto exit

:exit
echo.
echo 👋 Terima kasih telah menggunakan Maintenance System!
echo. 