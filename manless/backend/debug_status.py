#!/usr/bin/env python3
"""
Debug script untuk mengecek status backend dan controller
"""

import requests
import json

def test_controller():
    """Test controller status"""
    print("🔍 Testing Controller (port 8001)...")
    try:
        response = requests.get("http://localhost:8001/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Controller OK!")
            print("📋 Controller Response:")
            print(json.dumps(data, indent=2))
            
            # Extract hardware info
            hardware = data.get("hardware", {})
            arduino = hardware.get("arduino", {})
            print(f"\n🔧 Arduino Connected: {arduino.get('connected', False)}")
            return True
        else:
            print(f"❌ Controller Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Controller Connection Failed: {e}")
        return False

def test_backend():
    """Test backend status"""
    print("\n🔍 Testing Backend (port 8000)...")
    try:
        response = requests.get("http://localhost:8000/api/v1/system/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend OK!")
            print("📋 Backend Response:")
            print(json.dumps(data, indent=2))
            
            print(f"\n🔧 Arduino Status: {data.get('arduino', False)}")
            print(f"🔧 Controller Connected: {data.get('controller_connected', False)}")
            return True
        else:
            print(f"❌ Backend Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Connection Failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("DEBUG STATUS TEST")
    print("=" * 50)
    
    controller_ok = test_controller()
    backend_ok = test_backend()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Controller: {'✅ OK' if controller_ok else '❌ FAILED'}")
    print(f"Backend: {'✅ OK' if backend_ok else '❌ FAILED'}")
    
    if not controller_ok:
        print("\n🔧 Controller Issues:")
        print("- Make sure controller is running on port 8001")
        print("- Check controller logs for errors")
    
    if not backend_ok:
        print("\n🔧 Backend Issues:")
        print("- Make sure backend is running on port 8000")
        print("- Check backend logs for errors")
        print("- Make sure aiohttp dependency is installed") 