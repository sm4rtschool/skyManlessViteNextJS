#!/usr/bin/env python3
"""
Test Arduino Connection pada COM10
Quick test untuk memverifikasi Arduino terhubung dan responding
"""

import serial
import serial.tools.list_ports
import time
import sys
import os

def list_available_ports():
    """List semua port serial yang tersedia"""
    print("🔍 Scanning available serial ports...")
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ No serial ports found!")
        return []
    
    print(f"✅ Found {len(ports)} serial port(s):")
    for port in ports:
        print(f"   📍 {port.device}: {port.description}")
    
    return ports

def test_arduino_connection(port="COM10", baudrate=9600):
    """Test koneksi Arduino pada port tertentu"""
    print(f"\n🔌 Testing Arduino connection on {port}...")
    
    try:
        # Buka koneksi serial
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=3.0,
            write_timeout=3.0
        )
        
        print(f"✅ Serial port {port} opened successfully")
        
        # Wait for Arduino to initialize
        print("⏳ Waiting for Arduino to initialize...")
        time.sleep(2)
        
        # Clear any existing data
        if ser.in_waiting > 0:
            existing_data = ser.read_all()
            if existing_data:
                decoded_data = existing_data.decode('utf-8', errors='ignore')
                print(f"📄 Cleared existing data: {decoded_data.strip()}")
        
        # Test commands
        test_commands = [
            ("STATUS", "Check Arduino status"),
            ("LED_GREEN_ON", "Turn on green LED"),
            ("LED_GREEN_OFF", "Turn off green LED"),
            ("BUZZER_500", "Test buzzer for 500ms")
        ]
        
        print(f"\n🧪 Testing Arduino commands...")
        
        for command, description in test_commands:
            print(f"\n📤 Sending: {command} ({description})")
            
            # Send command
            ser.write(f"{command}\n".encode())
            time.sleep(0.5)
            
            # Read response
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"📥 Response: {response}")
                
                # Validate response
                if command == "STATUS" and "GATE:" in response:
                    print("✅ Status command successful")
                elif command.startswith("LED_") and "LED_OK" in response:
                    print("✅ LED command successful")
                elif command.startswith("BUZZER_") and "BUZZER_OK" in response:
                    print("✅ Buzzer command successful")
                else:
                    print(f"⚠️  Unexpected response: {response}")
            else:
                print("❌ No response received")
        
        # Final status check
        print(f"\n📊 Final status check...")
        ser.write(b"STATUS\n")
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            final_status = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"📥 Final status: {final_status}")
        
        ser.close()
        print(f"\n✅ Arduino connection test completed successfully!")
        return True
        
    except serial.SerialException as e:
        print(f"❌ Serial connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🤖 Arduino COM10 Connection Test")
    print("=" * 50)
    
    # List available ports
    available_ports = list_available_ports()
    
    # Check if COM10 is available
    com10_available = any(port.device == "COM10" for port in available_ports)
    
    if not com10_available:
        print(f"\n⚠️  COM10 not found in available ports!")
        print("Available ports:")
        for port in available_ports:
            print(f"   - {port.device}")
        
        # Ask user to select a port
        if available_ports:
            print(f"\nWould you like to test another port? (y/n)")
            choice = input().lower()
            if choice == 'y':
                print("Enter port name (e.g., COM3, COM4):")
                test_port = input().strip()
                if test_port:
                    test_arduino_connection(test_port)
        return
    
    # Test COM10
    success = test_arduino_connection("COM10")
    
    if success:
        print(f"\n🎉 Arduino pada COM10 siap digunakan!")
        print(f"📋 Next steps:")
        print(f"   1. Upload Arduino sketch (arduino_gate_controller.ino)")
        print(f"   2. Run Gate IN Controller: python main_gate_in.py")
        print(f"   3. Test frontend: http://localhost:5173/?gate=gate_in")
    else:
        print(f"\n❌ Arduino connection failed!")
        print(f"🔧 Troubleshooting:")
        print(f"   1. Check Arduino is connected to COM10")
        print(f"   2. Install CH340/FTDI driver if needed")
        print(f"   3. Upload correct Arduino sketch")
        print(f"   4. Check cable connection")
        print(f"   5. Try running as administrator")

if __name__ == "__main__":
    main() 