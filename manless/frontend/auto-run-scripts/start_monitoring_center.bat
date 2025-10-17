@echo off
echo ========================================
echo  MONITORING CENTER - AUTO START
echo ========================================
echo.
echo Starting Control Center Dashboard...
echo Monitor: Full Desktop/Laptop Screen
echo Mode: Monitoring All Gates
echo.

REM Start Chrome in normal window mode untuk monitoring center
start "Monitoring Center" chrome.exe ^
  --new-window ^
  --start-maximized ^
  --disable-features=TranslateUI ^
  --no-first-run ^
  --no-default-browser-check ^
  "http://localhost:5173?gate=all"

echo.
echo ✅ Monitoring Center started successfully!
echo.
echo 🏢  Control Center - Monitor semua gate
echo 🚪  Dapat switch antara Gate IN, Gate OUT, atau All
echo 📊  Dashboard lengkap dengan statistik
echo ⚙️  Full control dan configuration
echo.
echo Browser akan terbuka dalam window mode normal...
echo Tekan Enter untuk exit script...
pause >nul 