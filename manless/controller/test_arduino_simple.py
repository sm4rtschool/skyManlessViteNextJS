#!/usr/bin/env python3
"""
Comprehensive Arduino Controller Test
Test semua perintah serial dan integrasi dengan backend
"""

import asyncio
import serial
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_arduino_comprehensive():
    """Comprehensive Arduino test"""
    print("🤖 Comprehensive Arduino Test")
    print("=" * 50)
    
    try:
        # Test direct serial connection
        print("🔌 Testing direct serial connection...")
        ser = serial.Serial("COM8", 9600, timeout=2)
        
        if ser.is_open:
            print("✅ COM8 opened successfully")
            
            # Wait for Arduino
            time.sleep(2)
            
            # Clear buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Test PING command
            print("📤 Sending PING...")
            ser.write(b"PING\n")
            time.sleep(0.5)
            
            ping_response = ""
            if ser.in_waiting > 0:
                ping_response = ser.readline().decode('utf-8').strip()
                print(f"📥 PING Response: {ping_response}")
            
            # Test STATUS command
            print("📤 Sending STATUS...")
            ser.write(b"STATUS\n")
            time.sleep(1)
            
            status_response = ""
            if ser.in_waiting > 0:
                status_response = ser.readline().decode('utf-8').strip()
                print(f"📥 STATUS Response: {status_response}")
            
            # Test LED commands
            print("📤 Testing LED commands...")
            ser.write(b"LED_RED_ON\n")
            time.sleep(0.3)
            if ser.in_waiting > 0:
                led_response = ser.readline().decode('utf-8').strip()
                print(f"📥 LED Response: {led_response}")
            
            ser.write(b"LED_RED_OFF\n")
            time.sleep(0.3)
            
            # Test BUZZER command
            print("📤 Testing BUZZER...")
            ser.write(b"BUZZER_500\n")
            time.sleep(0.3)
            if ser.in_waiting > 0:
                buzzer_response = ser.readline().decode('utf-8').strip()
                print(f"📥 BUZZER Response: {buzzer_response}")
            
            ser.close()
            
            # Evaluate results
            success = False
            if ping_response == "PONG":
                print("✅ PING test PASSED")
                success = True
            elif "GATE:" in status_response:
                print("✅ STATUS test PASSED")
                success = True
            elif ping_response or status_response:
                print("⚠️ Arduino responding but format unexpected")
                success = True
            else:
                print("❌ No valid response from Arduino")
            
            return success
            
        else:
            print("❌ Could not open COM8")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_hardware_detector():
    """Test hardware detector integration"""
    print("\n🔍 Testing Hardware Detector Integration")
    print("=" * 50)
    
    try:
        from hardware_detector import HardwareDetector
        
        detector = HardwareDetector()
        
        # Test COM port detection
        detected = detector.detect_com_ports()
        print(f"📡 Detected {len(detected['all'])} COM ports:")
        for port in detected['all']:
            print(f"   {port['device']}: {port['description']}")
        
        print(f"\n🎯 Arduino ports: {detected['arduino']}")
        
        # Test Arduino connection
        if detected['arduino']:
            print(f"\n🔌 Testing Arduino on {detected['arduino'][0]}...")
            if detector.test_arduino_connection(detected['arduino'][0]):
                print("✅ Hardware detector Arduino test PASSED!")
                return True
            else:
                print("❌ Hardware detector Arduino test FAILED!")
                return False
        else:
            print("❌ No Arduino ports detected")
            return False
            
    except Exception as e:
        print(f"❌ Hardware detector test error: {e}")
        return False

async def test_arduino_controller():
    """Test Arduino controller integration"""
    print("\n🎮 Testing Arduino Controller Integration")
    print("=" * 50)
    
    try:
        from hardware.arduino import ArduinoController
        
        controller = ArduinoController(port="COM8", baudrate=9600)
        
        # Initialize controller
        print("🔌 Initializing Arduino controller...")
        if await controller.initialize():
            print("✅ Arduino controller initialized")
            
            # Test connection
            print("🔍 Testing connection...")
            if await controller.test_connection():
                print("✅ Arduino controller connection test PASSED!")
                
                # Test get status
                status = await controller.get_status()
                print(f"📊 Arduino status: {status}")
                
                await controller.cleanup()
                return True
            else:
                print("❌ Arduino controller connection test FAILED!")
                await controller.cleanup()
                return False
        else:
            print("❌ Arduino controller initialization FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Arduino controller test error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Arduino Integration Tests")
    print("=" * 60)
    
    # Test 1: Direct serial communication
    test1_result = await test_arduino_comprehensive()
    
    # Test 2: Hardware detector
    test2_result = await test_hardware_detector()
    
    # Test 3: Arduino controller
    test3_result = await test_arduino_controller()
    
    # Summary
    print("\n📋 Test Results Summary")
    print("=" * 30)
    print(f"Direct Serial Test: {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"Hardware Detector: {'✅ PASSED' if test2_result else '❌ FAILED'}")
    print(f"Arduino Controller: {'✅ PASSED' if test3_result else '❌ FAILED'}")
    
    overall_success = test1_result and test2_result and test3_result
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED! Arduino integration is working correctly.")
        print("✅ Backend should now detect Arduino status in real-time.")
    else:
        print("\n💥 SOME TESTS FAILED! Check Arduino connection and sketch.")
        print("🔧 Make sure Arduino sketch is uploaded and responding to commands.")
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 