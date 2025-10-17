#!/usr/bin/env python3
"""
Script untuk mengecek status port COM10
"""

import serial
import serial.tools.list_ports
import time

def list_all_ports():
    """List semua port COM yang tersedia"""
    print("🔍 Semua Port COM yang tersedia:")
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("   ❌ Tidak ada port COM ditemukan")
        return []
    
    for port in ports:
        print(f"   📡 {port.device}: {port.description}")
        print(f"      Hardware ID: {port.hwid}")
        print(f"      Manufacturer: {port.manufacturer}")
        print("")
    
    return [port.device for port in ports]

def test_com10():
    """Test khusus untuk COM10"""
    print("🔌 Testing COM10...")
    
    try:
        # Test buka port COM10
        ser = serial.Serial('COM10', 9600, timeout=1)
        print("   ✅ COM10 berhasil dibuka")
        
        # Test kirim command
        ser.write(b"STATUS\n")
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            print(f"   📨 Arduino response: {response}")
        else:
            print("   ⚠️ Tidak ada response dari Arduino")
        
        ser.close()
        return True
        
    except serial.SerialException as e:
        print(f"   ❌ Error: {e}")
        return False
    except PermissionError as e:
        print(f"   ❌ Permission Error: {e}")
        print("   💡 COM10 mungkin sedang digunakan aplikasi lain")
        return False

def find_arduino_ports():
    """Cari port yang kemungkinan Arduino"""
    print("🎯 Mencari port Arduino...")
    
    ports = serial.tools.list_ports.comports()
    arduino_ports = []
    
    for port in ports:
        description = port.description.lower()
        manufacturer = (port.manufacturer or "").lower()
        
        if any(keyword in description for keyword in ['arduino', 'uno', 'nano', 'mega', 'ch340', 'ftdi']):
            arduino_ports.append(port.device)
            print(f"   🎯 Kemungkinan Arduino: {port.device} - {port.description}")
        elif any(keyword in manufacturer for keyword in ['arduino', 'ch340', 'ftdi']):
            arduino_ports.append(port.device)
            print(f"   🎯 Kemungkinan Arduino: {port.device} - {port.description}")
    
    if not arduino_ports:
        print("   ❌ Tidak ditemukan port Arduino")
    
    return arduino_ports

def main():
    print("=" * 60)
    print("COM10 DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # List all ports
    all_ports = list_all_ports()
    
    # Check if COM10 exists
    if "COM10" not in all_ports:
        print("❌ COM10 tidak ditemukan di sistem!")
        print("💡 Arduino mungkin tidak terhubung atau menggunakan port lain")
    else:
        print("✅ COM10 ditemukan di sistem")
        
        # Test COM10
        com10_ok = test_com10()
        
        if not com10_ok:
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Tutup semua aplikasi yang menggunakan COM10 (Arduino IDE, Serial Monitor, dll)")
            print("2. Cabut dan colok ulang kabel USB Arduino")
            print("3. Restart komputer jika perlu")
    
    # Find alternative Arduino ports
    print("\n" + "=" * 60)
    print("ALTERNATIVE ARDUINO PORTS")
    print("=" * 60)
    
    arduino_ports = find_arduino_ports()
    
    if arduino_ports:
        print(f"\n💡 Coba gunakan port ini di config_gate_in.py:")
        for port in arduino_ports:
            print(f"   ARDUINO_PORT = \"{port}\"")

if __name__ == "__main__":
    main() 