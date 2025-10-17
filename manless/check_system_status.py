#!/usr/bin/env python3
"""
System Status Checker - Manless Parking System
Memeriksa status semua komponen sistem
"""

import requests
import asyncio
import websockets
import json
from datetime import datetime

def print_header(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_status(component, status, details=""):
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {component:<30} {details}")

async def check_websocket(url):
    """Check WebSocket connection"""
    try:
        async with websockets.connect(url, timeout=5) as websocket:
            # Send ping
            await websocket.send(json.dumps({"type": "ping", "payload": {}}))
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            return True, "Connected successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_http_endpoint(url, endpoint_name):
    """Check HTTP endpoint"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, f"HTTP {response.status_code} - {len(response.text)} bytes"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

async def main():
    print_header("MANLESS PARKING SYSTEM - STATUS CHECK")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Backend Services
    print_header("BACKEND SERVICES")
    
    # Central Hub
    status, details = check_http_endpoint("http://localhost:8000/", "Central Hub")
    print_status("Central Hub (Port 8000)", status, details)
    
    # WebSocket Central Hub
    try:
        status, details = await check_websocket("ws://localhost:8000/ws")
        print_status("WebSocket Central Hub", status, details)
    except Exception as e:
        print_status("WebSocket Central Hub", False, f"Error: {str(e)}")
    
    # Gate Controllers
    print_header("GATE CONTROLLERS")
    
    # Gate IN Controller
    status, details = check_http_endpoint("http://localhost:8001/", "Gate IN Controller")
    print_status("Gate IN Controller (8001)", status, details)
    
    # Gate OUT Controller  
    status, details = check_http_endpoint("http://localhost:8002/", "Gate OUT Controller")
    print_status("Gate OUT Controller (8002)", status, details)
    
    # API Endpoints
    print_header("API ENDPOINTS")
    
    endpoints = [
        ("http://localhost:8000/api/system/status", "System Status"),
        ("http://localhost:8000/api/parking/capacity", "Parking Capacity"),
        ("http://localhost:8001/api/status", "Gate IN Status"),
        ("http://localhost:8002/api/status", "Gate OUT Status"),
    ]
    
    for url, name in endpoints:
        status, details = check_http_endpoint(url, name)
        print_status(name, status, details)
    
    # Frontend
    print_header("FRONTEND")
    status, details = check_http_endpoint("http://localhost:5173/", "Frontend Development Server")
    print_status("Frontend (Port 5173)", status, details)
    
    print_header("SYSTEM CHECK COMPLETED")
    print("Jika ada komponen yang tidak berjalan, silakan jalankan:")
    print("  Backend:     cd manless/backend && python main.py")
    print("  Gate IN:     cd manless/controller && python main_gate_in.py")  
    print("  Gate OUT:    cd manless/controller && python main_gate_out.py")
    print("  Frontend:    cd manless/frontend && npm run dev")

if __name__ == "__main__":
    asyncio.run(main()) 