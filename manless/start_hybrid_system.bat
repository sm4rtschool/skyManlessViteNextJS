@echo off
echo ================================================
echo   STARTING MANLESS PARKING HYBRID SYSTEM
echo ================================================
echo.

:: Set window titles and colors
color 0A

echo [1/3] Starting Backend Hybrid Server (API + WebSocket)...
start "Backend Hybrid Server" cmd /k "cd /d backend && python main_hybrid.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Controller Gate IN...
start "Controller Gate IN" cmd /k "cd /d controller && python main_websocket.py gate_in"
timeout /t 2 /nobreak >nul

echo [3/3] Starting Controller Gate OUT...
start "Controller Gate OUT" cmd /k "cd /d controller && python main_websocket.py gate_out"
timeout /t 2 /nobreak >nul

echo.
echo ================================================
echo   HYBRID SYSTEM STARTED SUCCESSFULLY
echo ================================================
echo.
echo Backend Hybrid Server: http://localhost:8000
echo   - HTTP API:         http://localhost:8000/api/v1
echo   - API Docs:         http://localhost:8000/api/docs
echo   - System Status:    http://localhost:8000/api/system/status
echo   - WebSocket Status: http://localhost:8000/api/websocket/status
echo.
echo WebSocket Endpoints:
echo   - Frontend gate_in:  ws://localhost:8000/ws/gate_in
echo   - Frontend gate_out: ws://localhost:8000/ws/gate_out
echo   - Frontend admin:    ws://localhost:8000/ws/gate_all
echo   - Controller gate_in: ws://localhost:8000/ws/controller/gate_in
echo   - Controller gate_out: ws://localhost:8000/ws/controller/gate_out
echo.
echo Frontend Routes (React):
echo   - Gate IN Kiosk:    http://localhost:3000/gate-in
echo   - Gate OUT Kiosk:   http://localhost:3000/gate-out
echo   - Admin Dashboard:  http://localhost:3000/admin
echo.
echo Controllers:
echo   - Gate IN Controller:   WebSocket Client -> gate_in
echo   - Gate OUT Controller:  WebSocket Client -> gate_out
echo.
echo Smart WebSocket Features:
echo   - Auto-detect channel dari URL frontend
echo   - /gate-in -> connect ke ws/gate_in
echo   - /gate-out -> connect ke ws/gate_out
echo   - /admin -> connect ke ws/gate_all
echo.
echo Next Steps:
echo   1. Start frontend: cd frontend && npm start
echo   2. Open browser:
echo      - Gate IN:  http://localhost:3000/gate-in
echo      - Gate OUT: http://localhost:3000/gate-out
echo      - Admin:    http://localhost:3000/admin
echo   3. Test system: python test_websocket_system.py
echo.
echo Tekan Ctrl+C untuk menghentikan script ini.
echo Window lain akan tetap berjalan.
echo.
pause 