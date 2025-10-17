# Manless Parking System Startup Script
Write-Host "================================" -ForegroundColor Cyan
Write-Host "    MANLESS PARKING SYSTEM" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting frontend and backend..." -ForegroundColor Yellow
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start backend
Write-Host "[1/2] Starting Python Backend..." -ForegroundColor Green
$backendPath = Join-Path $scriptDir "manless\backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python simple_main.py" -WindowStyle Normal

# Wait 3 seconds
Start-Sleep -Seconds 3

# Start frontend
Write-Host "[2/2] Starting React Frontend..." -ForegroundColor Green
$frontendPath = Join-Path $scriptDir "manless\frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "   SYSTEM STARTING..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test connections
try {
    $frontendTest = Invoke-WebRequest -Uri "http://localhost:5173" -Method HEAD -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($frontendTest.StatusCode -eq 200) {
        Write-Host "✓ Frontend is running" -ForegroundColor Green
    } else {
        Write-Host "⚠ Frontend may still be starting..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Frontend may still be starting..." -ForegroundColor Yellow
}

try {
    $backendTest = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($backendTest.StatusCode -eq 200) {
        Write-Host "✓ Backend is running" -ForegroundColor Green
    } else {
        Write-Host "⚠ Backend may still be starting..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Backend may still be starting..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to open frontend in browser..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open frontend in browser
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "System is running!" -ForegroundColor Green
Write-Host "You can close this window now." -ForegroundColor White
Write-Host "" 