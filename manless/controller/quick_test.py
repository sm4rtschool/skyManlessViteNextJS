#!/usr/bin/env python3
"""
Quick Arduino Test
"""

import serial
import time

print("🔍 Quick Arduino Test")
print("=" * 20)

try:
    print("1. Opening COM8...")
    ser = serial.Serial("COM8", 9600, timeout=2)
    print("✅ COM8 opened successfully")
    
    print("2. Waiting for Arduino...")
    time.sleep(2)
    
    print("3. Reading startup message...")
    if ser.in_waiting > 0:
        startup = ser.readline().decode('utf-8').strip()
        print(f"   Startup: {startup}")
    else:
        print("   No startup message")
    
    print("4. Sending PING...")
    ser.write(b"PING\n")
    ser.flush()
    time.sleep(0.5)
    
    if ser.in_waiting > 0:
        response = ser.readline().decode('utf-8').strip()
        print(f"   Response: {response}")
    else:
        print("   No response")
    
    print("5. Closing connection...")
    ser.close()
    print("✅ Test completed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}") 