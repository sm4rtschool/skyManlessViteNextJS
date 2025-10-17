#!/usr/bin/env python3
"""
Test Arduino Connection pada COM8
"""

import serial
import serial.tools.list_ports
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_arduino_com8():
    """Test koneksi Arduino di COM8"""
    print("🤖 Arduino COM8 Connection Test")
    print("=" * 50)
    
    # List available ports
    ports = serial.tools.list_ports.comports()
    print(f"✅ Found {len(ports)} serial port(s):")
    for port in ports:
        print(f"   📍 {port.device}: {port.description}")
    
    # Check if COM8 exists
    com8_found = any(port.device == "COM8" for port in ports)
    if not com8_found:
        print("❌ COM8 not found in available ports!")
        return False
    
    print(f"\n🔌 Testing Arduino connection on COM8...")
    
    try:
        # Try to open COM8
        ser = serial.Serial("COM8", 9600, timeout=2)
        print("✅ Successfully opened COM8")
        
        # Wait for Arduino to initialize
        time.sleep(2)
        
        # Send test command
        print("📤 Sending STATUS command...")
        ser.write(b"STATUS\n")
        time.sleep(0.5)
        
        # Check for response
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            print(f"📥 Arduino response: {response}")
        else:
            print("⚠️  No response from Arduino")
        
        # Send PING command
        print("📤 Sending PING command...")
        ser.write(b"PING\n")
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            print(f"📥 Arduino response: {response}")
        else:
            print("⚠️  No response from Arduino")
        
        # Close connection
        ser.close()
        print("✅ Test completed successfully")
        return True
        
    except serial.SerialException as e:
        print(f"❌ Serial connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_arduino_com8()
    if success:
        print("\n🎉 Arduino COM8 test PASSED!")
    else:
        print("\n💥 Arduino COM8 test FAILED!") 