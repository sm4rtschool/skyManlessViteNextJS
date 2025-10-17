#!/usr/bin/env python3
"""
Test script untuk mengecek koneksi ke controller
"""

import asyncio
import aiohttp
import json

CONTROLLER_URL = "http://localhost:8001"

async def test_controller_connection():
    """Test koneksi ke controller"""
    print("🔍 Testing controller connection...")
    print(f"Controller URL: {CONTROLLER_URL}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test controller status endpoint
            print("\n📡 Testing /api/status endpoint...")
            async with session.get(f"{CONTROLLER_URL}/api/status", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Controller responding!")
                    print(f"Status Code: {response.status}")
                    print("📋 Controller Status:")
                    print(json.dumps(data, indent=2))
                    
                    # Check hardware status
                    hardware = data.get("hardware", {})
                    arduino = hardware.get("arduino", {})
                    card_reader = hardware.get("card_reader", {})
                    
                    print("\n🔧 Hardware Status:")
                    print(f"  Arduino Connected: {arduino.get('connected', False)}")
                    print(f"  Card Reader Connected: {card_reader.get('connected', False)}")
                    print(f"  Gate Status: {arduino.get('gate', {}).get('status', 'unknown')}")
                    
                    return True
                else:
                    print(f"❌ Controller error: HTTP {response.status}")
                    return False
                    
    except aiohttp.ClientConnectorError as e:
        print(f"❌ Connection failed: {e}")
        print("🔧 Make sure controller is running on port 8001")
        return False
    except asyncio.TimeoutError:
        print("❌ Connection timeout")
        print("🔧 Controller might be slow or not responding")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_backend_status():
    """Test backend status endpoint"""
    print("\n🔍 Testing backend status endpoint...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/v1/system/status", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Backend responding!")
                    print("📋 Backend Status:")
                    print(json.dumps(data, indent=2))
                    return True
                else:
                    print(f"❌ Backend error: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False

async def main():
    print("=" * 50)
    print("CONTROLLER CONNECTION TEST")
    print("=" * 50)
    
    # Test controller
    controller_ok = await test_controller_connection()
    
    # Test backend
    backend_ok = await test_backend_status()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Controller (port 8001): {'✅ OK' if controller_ok else '❌ FAILED'}")
    print(f"Backend (port 8000): {'✅ OK' if backend_ok else '❌ FAILED'}")
    
    if not controller_ok:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Make sure controller is running: python main_gate_in.py")
        print("2. Check if port 8001 is available")
        print("3. Check controller logs for errors")
    
    if not backend_ok:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Make sure backend is running: python main.py")
        print("2. Check if port 8000 is available")
        print("3. Check backend logs for errors")

if __name__ == "__main__":
    asyncio.run(main()) 