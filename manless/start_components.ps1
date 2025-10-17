# PowerShell Script untuk Start Semua Komponen - Manless Parking System
Write-Host "🚀 Starting Manless Parking System Components..." -ForegroundColor Green

# Fungsi untuk check apakah port sudah digunakan
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Check dan start Backend (Port 8000)
Write-Host "`n📡 Checking Central Hub Backend (Port 8000)..." -ForegroundColor Cyan
if (Test-Port 8000) {
    Write-Host "✅ Backend sudah berjalan di port 8000" -ForegroundColor Green
} else {
    Write-Host "🔄 Starting Backend..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; python main.py"
    Start-Sleep 3
}

# Check dan start Gate IN Controller (Port 8001)
Write-Host "`n🚪 Checking Gate IN Controller (Port 8001)..." -ForegroundColor Cyan
if (Test-Port 8001) {
    Write-Host "✅ Gate IN Controller sudah berjalan di port 8001" -ForegroundColor Green
} else {
    Write-Host "🔄 Starting Gate IN Controller..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\controller'; python main_gate_in.py"
    Start-Sleep 2
}

# Check dan start Gate OUT Controller (Port 8002)
Write-Host "`n🚪 Checking Gate OUT Controller (Port 8002)..." -ForegroundColor Cyan
if (Test-Port 8002) {
    Write-Host "✅ Gate OUT Controller sudah berjalan di port 8002" -ForegroundColor Green
} else {
    Write-Host "🔄 Starting Gate OUT Controller..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\controller'; python main_gate_out.py"
    Start-Sleep 2
}

# Check dan start Frontend (Port 5173)
Write-Host "`n🖥️ Checking Frontend Development Server (Port 5173)..." -ForegroundColor Cyan
if (Test-Port 5173) {
    Write-Host "✅ Frontend sudah berjalan di port 5173" -ForegroundColor Green
} else {
    Write-Host "🔄 Starting Frontend..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"
    Start-Sleep 5
}

# Wait dan check status
Write-Host "`n⏳ Waiting for all services to start..." -ForegroundColor Yellow
Start-Sleep 5

# Final status check
Write-Host "`n📊 Final Status Check:" -ForegroundColor Magenta
Write-Host "=" * 50

$services = @(
    @{Name="Central Hub Backend"; Port=8000; URL="http://localhost:8000/api/parking/capacity"},
    @{Name="Gate IN Controller"; Port=8001; URL="http://localhost:8001/api/status"},
    @{Name="Gate OUT Controller"; Port=8002; URL="http://localhost:8002/api/status"},
    @{Name="Frontend Dev Server"; Port=5173; URL="http://localhost:5173"}
)

foreach ($service in $services) {
    if (Test-Port $service.Port) {
        Write-Host "✅ $($service.Name) - Port $($service.Port) RUNNING" -ForegroundColor Green
    } else {
        Write-Host "❌ $($service.Name) - Port $($service.Port) NOT RUNNING" -ForegroundColor Red
    }
}

Write-Host "`n🎯 Access URLs:" -ForegroundColor Cyan
Write-Host "Gate IN Interface:    http://localhost:5173/?gate=gate_in" -ForegroundColor White
Write-Host "Gate OUT Interface:   http://localhost:5173/?gate=gate_out" -ForegroundColor White  
Write-Host "Monitoring Center:    http://localhost:5173/" -ForegroundColor White
Write-Host "Test Tool:           .\test_frontend_gate_in.html" -ForegroundColor White

Write-Host "`n🔧 Troubleshooting:" -ForegroundColor Yellow
Write-Host "System Status Check:  python check_system_status.py" -ForegroundColor White
Write-Host "WebSocket Test:       python test_websocket_client.py simple" -ForegroundColor White

Write-Host "`n✅ Startup script completed!" -ForegroundColor Green
Write-Host "Tekan Enter untuk keluar..." -ForegroundColor Gray
Read-Host 