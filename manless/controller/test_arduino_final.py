#!/usr/bin/env python3
"""
Final Arduino Test - Simple and Clear
"""

import serial
import time

def test_arduino_final():
    print("🔍 Final Arduino Test")
    print("=" * 30)
    
    try:
        # Open connection
        ser = serial.Serial("COM8", 9600, timeout=2)
        print("✅ COM8 opened")
        
        # Wait for startup
        time.sleep(2)
        
        # Read any startup message
        if ser.in_waiting > 0:
            startup = ser.readline().decode('utf-8').strip()
            print(f"📥 Startup: {startup}")
        
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Test 1: PING
        print("\n📤 Sending: PING")
        ser.write(b"PING\n")
        ser.flush()
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            print(f"📥 Response: '{response}'")
            ping_ok = response == "PONG"
        else:
            print("📥 No response")
            ping_ok = False
        
        # Test 2: STATUS
        print("\n📤 Sending: STATUS")
        ser.write(b"STATUS\n")
        ser.flush()
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            print(f"📥 Response: '{response}'")
            status_ok = "GATE:" in response
        else:
            print("📥 No response")
            status_ok = False
        
        # Test 3: LED
        print("\n📤 Sending: LED_RED_ON")
        ser.write(b"LED_RED_ON\n")
        ser.flush()
        time.sleep(0.3)
        
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            print(f"📥 Response: '{response}'")
            led_ok = response == "LED_OK"
        else:
            print("📥 No response")
            led_ok = False
        
        ser.close()
        
        # Results
        print("\n📋 Results:")
        print(f"PING: {'✅' if ping_ok else '❌'}")
        print(f"STATUS: {'✅' if status_ok else '❌'}")
        print(f"LED: {'✅' if led_ok else '❌'}")
        
        return ping_ok and status_ok and led_ok
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_arduino_final()
    print(f"\n🎯 Overall: {'✅ PASSED' if success else '❌ FAILED'}") 