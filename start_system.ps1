# Manless Parking System Startup Script
param(
    [switch]$SkipBackend,
    [switch]$SkipFrontend
)

Write-Host "Starting Manless Parking System..." -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan

# Refresh PATH environment variable
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

# Check dependencies
Write-Host "Checking dependencies..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found!" -ForegroundColor Red
    exit 1
}

try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Start Backend
Write-Host "Starting Python Backend..." -ForegroundColor Blue
$backendCmd = "cd 'C:\skyparking\manless\manless\backend'; `$env:PATH = [System.Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('PATH','User'); python run_backend.py"

Start-Process powershell -ArgumentList @("-NoExit", "-Command", $backendCmd)
Write-Host "[OK] Backend window opened" -ForegroundColor Green

Start-Sleep -Seconds 3

# Start Frontend  
Write-Host "Starting React Frontend..." -ForegroundColor Blue
$frontendCmd = "cd 'C:\skyparking\manless\manless\frontend'; npm run dev"

Start-Process powershell -ArgumentList @("-NoExit", "-Command", $frontendCmd)
Write-Host "[OK] Frontend window opened" -ForegroundColor Green

Write-Host ""
Write-Host "System startup complete!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "   - Kedua aplikasi akan terbuka di window terpisah" -ForegroundColor Gray
Write-Host "   - Gunakan Ctrl+C di setiap window untuk stop" -ForegroundColor Gray
Write-Host "   - Frontend mendukung hot-reload" -ForegroundColor Gray
Write-Host ""

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Test frontend
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173" -Method HEAD -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "[OK] Frontend is running" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Frontend may still be starting..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARNING] Frontend may still be starting..." -ForegroundColor Yellow
}

# Test backend
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($backendResponse.StatusCode -eq 200) {
        Write-Host "[OK] Backend is running" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Backend may still be starting..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARNING] Backend may still be starting..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to open frontend in browser..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open browser
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "System is running!" -ForegroundColor Green
Write-Host "You can close this window now." -ForegroundColor Gray 