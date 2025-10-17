#!/usr/bin/env python3
"""
Test Arduino Connection
Script untuk mengecek koneksi Arduino dan port yang tersedia
"""

import serial.tools.list_ports
import serial
import time

def list_available_ports():
    """List semua port serial yang tersedia"""
    print("=== Available Serial Ports ===")
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ Tidak ada port serial yang ditemukan")
        return []
    
    arduino_ports = []
    for port in ports:
        print(f"📡 {port.device} - {port.description}")
        
        # Check if it looks like Arduino
        if any(keyword in port.description.lower() for keyword in ['arduino', 'ch340', 'cp210', 'ftdi', 'usb']):
            arduino_ports.append(port.device)
            print(f"   ✅ Arduino-like device detected!")
    
    return arduino_ports

def test_arduino_connection(port, baudrate=9600):
    """Test koneksi ke Arduino di port tertentu"""
    print(f"\n=== Testing Arduino Connection ===")
    print(f"Port: {port}")
    print(f"Baudrate: {baudrate}")
    
    try:
        # Try to open serial connection
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print(f"✅ Serial connection opened successfully")
        
        # Wait for Arduino to initialize
        time.sleep(2)
        
        # Send test command
        test_command = "STATUS\n"
        print(f"📤 Sending: {test_command.strip()}")
        ser.write(test_command.encode())
        
        # Wait for response
        time.sleep(1)
        
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            print(f"📥 Received: {response}")
            ser.close()
            return True
        else:
            print("⚠️ No response received, but connection is open")
            ser.close()
            return True  # Connection successful even without response
            
    except serial.SerialException as e:
        print(f"❌ Serial connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_com10_specifically():
    """Test COM10 specifically (as configured in controller)"""
    print(f"\n=== Testing COM10 (Controller Config) ===")
    return test_arduino_connection("COM10", 9600)

def main():
    print("🔧 Arduino Connection Test")
    print("=" * 50)
    
    # List available ports
    arduino_ports = list_available_ports()
    
    # Test COM10 specifically
    com10_success = test_com10_specifically()
    
    # Test Arduino-like ports if found
    for port in arduino_ports:
        if port != "COM10":
            test_arduino_connection(port, 9600)
    
    print(f"\n=== Summary ===")
    if com10_success:
        print("✅ COM10 connection successful - Arduino should work in controller")
    else:
        print("❌ COM10 connection failed - Arduino will use simulation mode")
    
    if arduino_ports:
        print(f"📡 Found {len(arduino_ports)} Arduino-like device(s)")
    else:
        print("⚠️ No Arduino-like devices found")

if __name__ == "__main__":
    main() 