#!/usr/bin/env python3
"""
Detailed Arduino Test
"""

import serial
import time

print("🔍 Detailed Arduino Test")
print("=" * 30)

try:
    print("1. Opening COM8...")
    ser = serial.Serial("COM8", 9600, timeout=2)
    print("✅ COM8 opened successfully")
    
    print("2. Waiting 3 seconds for Arduino startup...")
    time.sleep(3)
    
    print("3. Checking for startup message...")
    startup_messages = []
    while ser.in_waiting > 0:
        msg = ser.readline().decode('utf-8').strip()
        if msg:
            startup_messages.append(msg)
            print(f"   Startup: {msg}")
    
    if not startup_messages:
        print("   No startup messages received")
    
    print("4. Testing PING command...")
    ser.write(b"PING\n")
    ser.flush()
    print("   PING sent, waiting for response...")
    time.sleep(1)
    
    if ser.in_waiting > 0:
        response = ser.readline().decode('utf-8').strip()
        print(f"   PING response: '{response}'")
    else:
        print("   No PING response")
    
    print("5. Testing STATUS command...")
    ser.write(b"STATUS\n")
    ser.flush()
    print("   STATUS sent, waiting for response...")
    time.sleep(1)
    
    if ser.in_waiting > 0:
        response = ser.readline().decode('utf-8').strip()
        print(f"   STATUS response: '{response}'")
    else:
        print("   No STATUS response")
    
    print("6. Testing LED command...")
    ser.write(b"LED_RED_ON\n")
    ser.flush()
    print("   LED_RED_ON sent, waiting for response...")
    time.sleep(0.5)
    
    if ser.in_waiting > 0:
        response = ser.readline().decode('utf-8').strip()
        print(f"   LED response: '{response}'")
    else:
        print("   No LED response")
    
    print("7. Closing connection...")
    ser.close()
    print("✅ Test completed")
    
    # Summary
    print("\n📋 Summary:")
    print(f"Startup messages: {len(startup_messages)}")
    print("Commands tested: PING, STATUS, LED_RED_ON")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}") 