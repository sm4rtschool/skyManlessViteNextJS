@echo off
echo ================================
echo    MANLESS PARKING SYSTEM
echo ================================
echo.
echo Starting frontend and backend...
echo.

:: Start backend in new window
echo [1/2] Starting Python Backend...
start "Manless Backend" cmd /k "cd /d %~dp0manless\backend && python simple_main.py"

:: Wait 3 seconds
timeout /t 3 /nobreak >nul

:: Start frontend in new window  
echo [2/2] Starting React Frontend...
start "Manless Frontend" cmd /k "cd /d %~dp0manless\frontend && npm run dev"

echo.
echo ================================
echo   SYSTEM STARTING...
echo ================================
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to open frontend in browser...
pause >nul

:: Open frontend in default browser
start http://localhost:5173

echo.
echo System is running!
echo Close this window to keep applications running.
echo.
pause 