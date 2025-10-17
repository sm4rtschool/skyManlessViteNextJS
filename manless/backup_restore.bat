@echo off
chcp 65001 >nul
cls

echo ================================================================
echo 💾 BACKUP & RESTORE SISTEM PARKIR MANLESS
echo ================================================================
echo.

echo Pilihan operasi:
echo 1. Backup sistem (Database + Config)
echo 2. Restore sistem dari backup
echo 3. Backup database saja
echo 4. Restore database saja
echo 0. Keluar
echo.

set /p choice="Pilih opsi (0-4): "

if "%choice%"=="1" goto backup_all
if "%choice%"=="2" goto restore_all
if "%choice%"=="3" goto backup_db
if "%choice%"=="4" goto restore_db
if "%choice%"=="0" goto exit
goto invalid

:backup_all
echo.
echo 💾 Membuat backup lengkap sistem...
echo.

REM Buat folder backup dengan timestamp
set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
set backup_folder=backup_%timestamp%

if not exist "%backup_folder%" mkdir "%backup_folder%"

echo 📁 Membuat folder backup: %backup_folder%
echo.

REM Backup database
echo 📊 Backup database...
if exist "backend\parking_system.db" (
    copy "backend\parking_system.db" "%backup_folder%\parking_system.db"
    echo ✅ Database berhasil di-backup
) else (
    echo ⚠️  Database tidak ditemukan
)

REM Backup config files
echo ⚙️  Backup config files...
if exist "controller\config.py" (
    copy "controller\config.py" "%backup_folder%\controller_config.py"
    echo ✅ Controller config berhasil di-backup
)

if exist "backend\camera_config.py" (
    copy "backend\camera_config.py" "%backup_folder%\camera_config.py"
    echo ✅ Camera config berhasil di-backup
)

REM Backup logs
echo 📝 Backup logs...
if exist "controller\logs" (
    xcopy "controller\logs" "%backup_folder%\logs\" /E /I /Y >nul
    echo ✅ Logs berhasil di-backup
)

echo.
echo ✅ Backup lengkap berhasil dibuat di folder: %backup_folder%
echo.
pause
goto exit

:restore_all
echo.
echo 🔄 Restore sistem dari backup...
echo.

set /p backup_folder="Masukkan nama folder backup: "

if not exist "%backup_folder%" (
    echo ❌ Folder backup tidak ditemukan!
    pause
    goto exit
)

echo ⚠️  Peringatan: Ini akan menimpa data yang ada!
set /p confirm="Apakah Anda yakin ingin restore? (y/n): "

if /i not "%confirm%"=="y" (
    echo ❌ Restore dibatalkan.
    pause
    goto exit
)

echo.
echo 🔄 Memulai restore...

REM Stop semua process dulu
echo 🔪 Menghentikan semua process...
cd /d ..
call start_centralized_system.bat 5 >nul 2>&1
cd /d manless

REM Restore database
if exist "%backup_folder%\parking_system.db" (
    copy "%backup_folder%\parking_system.db" "backend\parking_system.db"
    echo ✅ Database berhasil di-restore
)

REM Restore config files
if exist "%backup_folder%\controller_config.py" (
    copy "%backup_folder%\controller_config.py" "controller\config.py"
    echo ✅ Controller config berhasil di-restore
)

if exist "%backup_folder%\camera_config.py" (
    copy "%backup_folder%\camera_config.py" "backend\camera_config.py"
    echo ✅ Camera config berhasil di-restore
)

REM Restore logs
if exist "%backup_folder%\logs" (
    xcopy "%backup_folder%\logs" "controller\logs\" /E /I /Y >nul
    echo ✅ Logs berhasil di-restore
)

echo.
echo ✅ Restore berhasil selesai!
echo.
pause
goto exit

:backup_db
echo.
echo 📊 Backup database saja...
echo.

set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
set backup_file=db_backup_%timestamp%.db

if exist "backend\parking_system.db" (
    copy "backend\parking_system.db" "%backup_file%"
    echo ✅ Database berhasil di-backup: %backup_file%
) else (
    echo ❌ Database tidak ditemukan!
)

echo.
pause
goto exit

:restore_db
echo.
echo 🔄 Restore database saja...
echo.

set /p backup_file="Masukkan nama file backup database: "

if not exist "%backup_file%" (
    echo ❌ File backup tidak ditemukan!
    pause
    goto exit
)

echo ⚠️  Peringatan: Ini akan menimpa database yang ada!
set /p confirm="Apakah Anda yakin ingin restore database? (y/n): "

if /i not "%confirm%"=="y" (
    echo ❌ Restore dibatalkan.
    pause
    goto exit
)

REM Stop backend dulu
echo 🔪 Menghentikan backend...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a 2>nul

copy "%backup_file%" "backend\parking_system.db"
echo ✅ Database berhasil di-restore

echo.
pause
goto exit

:invalid
echo.
echo ❌ Pilihan tidak valid! Silakan pilih 0-4
echo.
pause
goto exit

:exit
echo.
echo 👋 Terima kasih telah menggunakan Backup & Restore System!
echo. 