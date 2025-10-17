@echo off
echo =====================================
echo   MANLESS PARKING SYSTEM
echo =====================================
echo.

echo [1/3] Starting Backend...
start "Backend Python" cmd /k "cd /d C:\skyparking\manless\manless\backend && python run_backend.py"

echo [2/3] Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo [3/3] Starting Frontend...
start "Frontend React" cmd /k "cd /d C:\skyparking\manless\manless\frontend && npm run dev"

echo.
echo =====================================
echo   SYSTEM STARTED!
echo =====================================
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to open browser...
pause >nul

start http://localhost:5173

echo.
echo You can close this window now.
echo Use Ctrl+C in the other windows to stop the services.
pause 