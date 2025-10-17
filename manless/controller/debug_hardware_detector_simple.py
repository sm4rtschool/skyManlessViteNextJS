#!/usr/bin/env python3
"""
Debug Hardware Detector - Using same code as hardware_detector.py
"""

import serial
import time

def test_arduino_connection_same_as_hardware_detector(port: str, baudrate: int = 9600) -> bool:
    """Test koneksi ke Arduino dengan command PING dan STATUS - same as hardware_detector.py"""
    try:
        print(f"DEBUG: Opening {port}...")
        ser = serial.Serial(port, baudrate, timeout=1)
        
        if ser.is_open:
            print(f"DEBUG: Port {port} opened successfully")
            
            # Clear buffers
            print(f"DEBUG: Clearing buffers...")
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Wait for Arduino to be ready
            print(f"DEBUG: Waiting 0.5s...")
            time.sleep(0.5)
            
            # Test PING command first
            print(f"DEBUG: Sending PING...")
            ser.write(b"PING\n")
            print(f"DEBUG: Waiting 0.3s for PING response...")
            time.sleep(0.3)
            
            print(f"DEBUG: Bytes available: {ser.in_waiting}")
            ping_response = ""
            if ser.in_waiting > 0:
                ping_response = ser.readline().decode('utf-8').strip()
                print(f"DEBUG: PING response on {port}: '{ping_response}'")
            else:
                print(f"DEBUG: No PING response")
            
            # Test STATUS command
            print(f"DEBUG: Sending STATUS...")
            ser.write(b"STATUS\n")
            print(f"DEBUG: Waiting 0.5s for STATUS response...")
            time.sleep(0.5)
            
            print(f"DEBUG: Bytes available: {ser.in_waiting}")
            status_response = ""
            if ser.in_waiting > 0:
                status_response = ser.readline().decode('utf-8').strip()
                print(f"DEBUG: STATUS response on {port}: '{status_response}'")
            else:
                print(f"DEBUG: No STATUS response")
            
            print(f"DEBUG: Closing connection...")
            ser.close()
            
            # Check if we got valid responses
            if ping_response == "PONG" or "GATE:" in status_response:
                print(f"DEBUG: ✅ Arduino {port} responding correctly")
                return True
            elif ping_response or status_response:
                # Arduino is responding, even if format is unexpected
                print(f"DEBUG: ✅ Arduino {port} responding (format: PING='{ping_response}', STATUS='{status_response}')")
                return True
            else:
                print(f"DEBUG: ⚠️ Arduino {port} not responding to commands")
                return False
        else:
            print(f"DEBUG: Arduino port {port} is not open")
            return False
            
    except serial.SerialException as e:
        print(f"DEBUG: Arduino connection error on {port}: {e}")
        return False
    except Exception as e:
        print(f"DEBUG: Arduino test error on {port}: {e}")
        return False

print("🔍 Debug Hardware Detector - Same Code")
print("=" * 40)

result = test_arduino_connection_same_as_hardware_detector('COM8')
print(f"\n🎯 Final result: Arduino connected = {result}") 