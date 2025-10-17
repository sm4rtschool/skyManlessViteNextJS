#!/usr/bin/env python3
"""
Debug script untuk melihat konfigurasi controller
"""

import os
import sys

def check_environment():
    """Check environment variables"""
    print("🔍 Environment Variables:")
    
    env_vars = [
        "GATE_IN_ARDUINO_PORT",
        "SIMULATION_MODE",
        "ARDUINO_PORT"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "NOT SET")
        print(f"   {var} = {value}")

def check_config_file():
    """Check config file values"""
    print("\n📄 Config File Values:")
    
    try:
        # Force reload config
        if 'config_gate_in' in sys.modules:
            del sys.modules['config_gate_in']
        
        import config_gate_in as config
        
        print(f"   ARDUINO_PORT = {config.ARDUINO_PORT}")
        print(f"   SIMULATION_MODE = {config.SIMULATION_MODE}")
        print(f"   ARDUINO_ENABLED = {config.ARDUINO_ENABLED}")
        
        return config
    except Exception as e:
        print(f"   Error: {e}")
        return None

def fix_environment():
    """Fix environment variables"""
    print("\n🔧 Fixing Environment Variables:")
    
    # Clear problematic env vars
    for var in ["GATE_IN_ARDUINO_PORT", "ARDUINO_PORT"]:
        if var in os.environ:
            del os.environ[var]
            print(f"   Cleared {var}")
    
    # Set correct values
    os.environ["GATE_IN_ARDUINO_PORT"] = "COM10"
    os.environ["SIMULATION_MODE"] = "false"
    
    print(f"   Set GATE_IN_ARDUINO_PORT = COM10")
    print(f"   Set SIMULATION_MODE = false")

def test_arduino_connection():
    """Test Arduino connection with correct port"""
    print("\n🔌 Testing Arduino Connection:")
    
    try:
        from hardware.arduino import ArduinoController
        
        # Test with COM10
        arduino = ArduinoController("COM10", False)  # Force hardware mode
        result = arduino.initialize()
        
        print(f"   Arduino COM10 initialization: {result}")
        print(f"   Arduino connected: {arduino.is_connected}")
        
        return arduino.is_connected
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    print("=" * 60)
    print("CONTROLLER CONFIGURATION DEBUG")
    print("=" * 60)
    
    # Check current state
    check_environment()
    config = check_config_file()
    
    # Fix environment
    fix_environment()
    
    # Recheck after fix
    print("\n" + "=" * 60)
    print("AFTER ENVIRONMENT FIX")
    print("=" * 60)
    
    check_environment()
    config = check_config_file()
    
    # Test Arduino
    arduino_ok = test_arduino_connection()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Arduino Connection: {'✅ OK' if arduino_ok else '❌ FAILED'}")
    
    if config:
        print(f"Config Arduino Port: {config.ARDUINO_PORT}")
        print(f"Config Simulation Mode: {config.SIMULATION_MODE}")
    
    print("\n🔄 Restart controller dengan environment yang sudah diperbaiki!")

if __name__ == "__main__":
    main() 