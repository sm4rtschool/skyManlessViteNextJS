@echo off
echo ================================================
echo   STARTING MANLESS PARKING WEBSOCKET SYSTEM
echo ================================================
echo.

:: Set window titles and colors
color 0A

echo [1/3] Starting Backend WebSocket Server...
start "Backend WebSocket Server" cmd /k "cd /d backend && python main_websocket.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Controller Gate IN...
start "Controller Gate IN" cmd /k "cd /d controller && python main_websocket.py gate_in"
timeout /t 2 /nobreak >nul

echo [3/3] Starting Controller Gate OUT...
start "Controller Gate OUT" cmd /k "cd /d controller && python main_websocket.py gate_out"
timeout /t 2 /nobreak >nul

echo.
echo ================================================
echo   ALL COMPONENTS STARTED SUCCESSFULLY
echo ================================================
echo.
echo Backend WebSocket Server: http://localhost:8000
echo   - WebSocket gate_in:    ws://localhost:8000/ws/gate_in
echo   - WebSocket gate_out:   ws://localhost:8000/ws/gate_out
echo   - WebSocket gate_all:   ws://localhost:8000/ws/gate_all
echo   - WebSocket admin:      ws://localhost:8000/ws/admin
echo.
echo Controllers:
echo   - Gate IN Controller:   WebSocket Client -> gate_in
echo   - Gate OUT Controller:  WebSocket Client -> gate_out
echo.
echo Frontend dapat terhubung ke:
echo   - ws://localhost:8000/ws/gate_in   (untuk gate masuk)
echo   - ws://localhost:8000/ws/gate_out  (untuk gate keluar)
echo   - ws://localhost:8000/ws/gate_all  (untuk monitoring semua)
echo   - ws://localhost:8000/ws/admin     (untuk admin)
echo.
echo Tekan Ctrl+C untuk menghentikan script ini.
echo Window lain akan tetap berjalan.
echo.
pause 