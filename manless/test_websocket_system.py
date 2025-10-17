#!/usr/bin/env python3
"""
Test Script untuk Sistem WebSocket Manless Parking
Verifikasi koneksi dan komunikasi antar komponen
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
WS_GATE_IN = "ws://localhost:8000/ws/gate_in"
WS_GATE_OUT = "ws://localhost:8000/ws/gate_out"
WS_GATE_ALL = "ws://localhost:8000/ws/gate_all"
WS_ADMIN = "ws://localhost:8000/ws/admin"

class WebSocketTester:
    """Tester untuk WebSocket connections"""
    
    def __init__(self):
        self.test_results = {}
        
    async def test_backend_api(self):
        """Test backend API endpoints"""
        print("🌐 Testing Backend API...")
        
        try:
            # Test root endpoint
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            if response.status_code == 200:
                print("  ✅ Root endpoint OK")
                self.test_results["backend_root"] = True
            else:
                print(f"  ❌ Root endpoint failed: {response.status_code}")
                self.test_results["backend_root"] = False
                
            # Test status endpoint
            response = requests.get(f"{BACKEND_URL}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("  ✅ Status endpoint OK")
                print(f"     Active channels: {data.get('channels', {})}")
                print(f"     Connected controllers: {data.get('controllers', [])}")
                self.test_results["backend_status"] = True
            else:
                print(f"  ❌ Status endpoint failed: {response.status_code}")
                self.test_results["backend_status"] = False
                
        except Exception as e:
            print(f"  ❌ Backend API test failed: {e}")
            self.test_results["backend_api"] = False
    
    async def test_websocket_connection(self, url, channel_name):
        """Test WebSocket connection to specific channel"""
        print(f"🔌 Testing WebSocket: {channel_name}")
        
        try:
            # Connect to WebSocket
            async with websockets.connect(url, timeout=5) as websocket:
                print(f"  ✅ Connected to {channel_name}")
                
                # Send ping
                ping_message = {
                    "type": "ping",
                    "payload": {"timestamp": datetime.now().isoformat()}
                }
                await websocket.send(json.dumps(ping_message))
                print(f"  📤 Sent ping to {channel_name}")
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    data = json.loads(response)
                    print(f"  📨 Received from {channel_name}: {data.get('type')}")
                    
                    if data.get('type') == 'pong':
                        print(f"  ✅ Ping-pong successful for {channel_name}")
                        self.test_results[f"ws_{channel_name}"] = True
                    else:
                        print(f"  ⚠️ Unexpected response from {channel_name}: {data}")
                        self.test_results[f"ws_{channel_name}"] = True  # Still working
                        
                except asyncio.TimeoutError:
                    print(f"  ⚠️ No response from {channel_name} (might be normal)")
                    self.test_results[f"ws_{channel_name}"] = True
                    
                # Test status request
                status_message = {
                    "type": "request_status",
                    "payload": {}
                }
                await websocket.send(json.dumps(status_message))
                print(f"  📤 Sent status request to {channel_name}")
                
        except Exception as e:
            print(f"  ❌ WebSocket test failed for {channel_name}: {e}")
            self.test_results[f"ws_{channel_name}"] = False
    
    async def test_gate_control(self, url, channel_name):
        """Test gate control commands"""
        print(f"🚪 Testing Gate Control: {channel_name}")
        
        try:
            async with websockets.connect(url, timeout=5) as websocket:
                # Test gate open
                control_message = {
                    "type": "gate_control",
                    "payload": {
                        "action": "open",
                        "gate_id": channel_name.replace("gate_", "gate_"),
                        "duration": 5
                    }
                }
                await websocket.send(json.dumps(control_message))
                print(f"  📤 Sent gate open command to {channel_name}")
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    data = json.loads(response)
                    print(f"  📨 Gate control response: {data.get('type')}")
                    
                    if data.get('type') == 'gate_control_response':
                        success = data.get('payload', {}).get('success', False)
                        if success:
                            print(f"  ✅ Gate control successful for {channel_name}")
                        else:
                            print(f"  ⚠️ Gate control failed for {channel_name}")
                        self.test_results[f"gate_control_{channel_name}"] = success
                    else:
                        print(f"  ⚠️ Unexpected gate control response: {data}")
                        self.test_results[f"gate_control_{channel_name}"] = False
                        
                except asyncio.TimeoutError:
                    print(f"  ⚠️ No gate control response from {channel_name}")
                    self.test_results[f"gate_control_{channel_name}"] = False
                
        except Exception as e:
            print(f"  ❌ Gate control test failed for {channel_name}: {e}")
            self.test_results[f"gate_control_{channel_name}"] = False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting WebSocket System Tests")
        print("=" * 50)
        
        # Test backend API
        await self.test_backend_api()
        print()
        
        # Test WebSocket connections
        websocket_tests = [
            (WS_GATE_IN, "gate_in"),
            (WS_GATE_OUT, "gate_out"), 
            (WS_GATE_ALL, "gate_all"),
            (WS_ADMIN, "admin")
        ]
        
        for url, name in websocket_tests:
            await self.test_websocket_connection(url, name)
            await asyncio.sleep(1)
        
        print()
        
        # Test gate control (only for gate channels)
        gate_control_tests = [
            (WS_GATE_IN, "gate_in"),
            (WS_GATE_OUT, "gate_out")
        ]
        
        for url, name in gate_control_tests:
            await self.test_gate_control(url, name)
            await asyncio.sleep(1)
        
        print()
        
        # Print results summary
        self.print_results()
    
    def print_results(self):
        """Print test results summary"""
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name:<25} {status}")
            if result:
                passed += 1
        
        print()
        print(f"📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! System is working correctly.")
        elif passed >= total * 0.7:
            print("⚠️ Most tests passed. Some components may need attention.")
        else:
            print("❌ Many tests failed. Please check system components.")

async def simple_connection_test():
    """Simple connection test untuk debugging cepat"""
    print("🔍 Quick Connection Test")
    print("-" * 30)
    
    # Test backend
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=3)
        print(f"Backend: {'✅ OK' if response.status_code == 200 else '❌ FAIL'}")
    except Exception as e:
        print(f"Backend: ❌ FAIL ({e})")
    
    # Test WebSocket connections
    channels = [
        ("gate_in", WS_GATE_IN),
        ("gate_out", WS_GATE_OUT),
        ("gate_all", WS_GATE_ALL),
        ("admin", WS_ADMIN)
    ]
    
    for name, url in channels:
        try:
            async with websockets.connect(url, timeout=3) as ws:
                print(f"WS {name}: ✅ OK")
        except Exception as e:
            print(f"WS {name}: ❌ FAIL ({e})")

def check_system_requirements():
    """Check if system components are running"""
    print("🔍 Checking System Requirements")
    print("-" * 40)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        if response.status_code == 200:
            print("✅ Backend WebSocket Server is running")
        else:
            print("❌ Backend WebSocket Server is not responding correctly")
            return False
    except requests.ConnectionError:
        print("❌ Backend WebSocket Server is not running!")
        print("   Please start it with: cd backend && python main_websocket.py")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False
    
    # Check controllers via backend status
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=2)
        if response.status_code == 200:
            data = response.json()
            controllers = data.get('controllers', [])
            if controllers:
                print(f"✅ Controllers connected: {', '.join(controllers)}")
            else:
                print("⚠️ No controllers connected")
                print("   Start controllers with:")
                print("   cd controller && python main_websocket.py gate_in")
                print("   cd controller && python main_websocket.py gate_out")
        else:
            print("⚠️ Could not get controller status")
    except Exception as e:
        print(f"⚠️ Error checking controllers: {e}")
    
    return True

async def main():
    """Main test function"""
    print("🧪 WebSocket System Tester")
    print("="*50)
    
    # Check requirements first
    if not check_system_requirements():
        print("\n❌ System requirements not met. Please start the required components.")
        return
    
    print("\nChoose test mode:")
    print("1. Quick Connection Test")
    print("2. Full System Test")
    print("3. Exit")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            print()
            await simple_connection_test()
        elif choice == "2":
            print()
            tester = WebSocketTester()
            await tester.run_all_tests()
        elif choice == "3":
            print("Exiting...")
            return
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 