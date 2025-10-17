#!/usr/bin/env python3
"""
Debug Hardware Detector
"""

import logging
import serial
import time

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def debug_arduino_connection():
    """Debug Arduino connection step by step"""
    print("🔍 Debug Arduino Connection")
    print("=" * 40)
    
    try:
        # Initialize response variables
        ping_response = ""
        status_response = ""
        
        # Step 1: Open serial connection
        print("1. Opening COM8...")
        ser = serial.Serial("COM8", 9600, timeout=1)
        
        if ser.is_open:
            print("✅ COM8 opened successfully")
            
            # Step 2: Wait for Arduino startup message
            print("2. Waiting for Arduino startup message...")
            time.sleep(2)
            
            # Step 3: Check for startup message
            print(f"3. Bytes available after startup: {ser.in_waiting}")
            if ser.in_waiting > 0:
                startup_msg = ser.readline().decode('utf-8').strip()
                print(f"   Startup message: '{startup_msg}'")
            
            # Step 4: Clear buffers
            print("4. Clearing buffers...")
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Step 5: Wait
            print("5. Waiting 0.5s...")
            time.sleep(0.5)
            
            # Step 6: Send PING
            print("6. Sending PING...")
            ser.write(b"PING\n")
            ser.flush()
            
            # Step 7: Wait for response
            print("7. Waiting for PING response...")
            time.sleep(0.5)
            
            # Step 8: Check response
            print(f"8. Bytes available: {ser.in_waiting}")
            if ser.in_waiting > 0:
                ping_response = ser.readline().decode('utf-8').strip()
                print(f"   PING response: '{ping_response}'")
            else:
                print("   No PING response")
            
            # Step 9: Send STATUS
            print("9. Sending STATUS...")
            ser.write(b"STATUS\n")
            ser.flush()
            
            # Step 10: Wait for response
            print("10. Waiting for STATUS response...")
            time.sleep(0.5)
            
            # Step 11: Check response
            print(f"11. Bytes available: {ser.in_waiting}")
            if ser.in_waiting > 0:
                status_response = ser.readline().decode('utf-8').strip()
                print(f"   STATUS response: '{status_response}'")
            else:
                print("   No STATUS response")
            
            # Step 12: Close
            print("12. Closing connection...")
            ser.close()
            
            # Step 13: Evaluate
            print("13. Evaluating results...")
            if ping_response == "PONG" or "GATE:" in status_response:
                print("✅ Valid responses detected")
                return True
            elif ping_response or status_response:
                print("⚠️ Responses detected but format unexpected")
                return True
            else:
                print("❌ No responses detected")
                return False
                
        else:
            print("❌ Could not open COM8")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = debug_arduino_connection()
    print(f"\n🎯 Final result: {'✅ PASSED' if result else '❌ FAILED'}") 