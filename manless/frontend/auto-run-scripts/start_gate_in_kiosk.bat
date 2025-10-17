@echo off
echo ========================================
echo   GATE IN KIOSK MODE - AUTO START
echo ========================================
echo.
echo Starting Gate IN Dashboard in Kiosk Mode...
echo Monitor: 10" Touch Screen
echo Gate: Entry Gate (gate_in)
echo.

REM Kill existing Chrome processes untuk clean start
taskkill /f /im chrome.exe >nul 2>&1
taskkill /f /im msedge.exe >nul 2>&1

REM Wait untuk Chrome process shutdown
timeout /t 2 /nobreak >nul

REM Start Chrome in kiosk mode untuk Gate IN
start "Gate IN Kiosk" chrome.exe ^
  --kiosk ^
  --start-fullscreen ^
  --disable-web-security ^
  --disable-features=VizDisplayCompositor,TranslateUI ^
  --disable-background-timer-throttling ^
  --disable-backgrounding-occluded-windows ^
  --disable-renderer-backgrounding ^
  --disable-field-trial-config ^
  --disable-ipc-flooding-protection ^
  --no-first-run ^
  --no-default-browser-check ^
  --disable-default-apps ^
  --disable-popup-blocking ^
  --disable-translate ^
  --disable-background-networking ^
  --disable-sync ^
  --disable-extensions ^
  --disable-component-extensions-with-background-pages ^
  --app="http://localhost:5173?gate=gate_in"

echo.
echo ✅ Gate IN Kiosk Mode started successfully!
echo.
echo 🖥️  Monitor akan menampilkan dashboard Gate IN
echo 🚪  Hanya menampilkan aktivitas Gate Masuk
echo ⏰  Auto-refresh setiap 6 jam untuk stabilitas
echo 🔒  Kiosk mode - F11/F12/Right-click disabled
echo.
echo Tekan Enter untuk exit script (Chrome tetap berjalan)...
pause >nul 