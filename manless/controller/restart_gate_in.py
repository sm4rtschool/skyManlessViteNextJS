#!/usr/bin/env python3
"""
Script untuk restart Gate IN controller dengan konfigurasi yang benar
"""

import os
import sys
import subprocess

def set_environment():
    """Set environment variables yang benar"""
    print("🔧 Setting correct environment variables...")
    
    # Clear any existing Arduino port override
    if "GATE_IN_ARDUINO_PORT" in os.environ:
        del os.environ["GATE_IN_ARDUINO_PORT"]
        print("   Cleared GATE_IN_ARDUINO_PORT")
    
    # Set simulation mode to false
    os.environ["SIMULATION_MODE"] = "false"
    print("   Set SIMULATION_MODE=false")
    
    # Ensure Arduino port is COM10
    os.environ["GATE_IN_ARDUINO_PORT"] = "COM10"
    print("   Set GATE_IN_ARDUINO_PORT=COM10")
    
    print("✅ Environment configured")

def check_config():
    """Check current configuration"""
    print("\n📋 Current Configuration:")
    
    try:
        import config_gate_in as config
        print(f"   Arduino Port: {config.ARDUINO_PORT}")
        print(f"   Simulation Mode: {config.SIMULATION_MODE}")
        print(f"   Arduino Enabled: {config.ARDUINO_ENABLED}")
    except Exception as e:
        print(f"   Error reading config: {e}")

def main():
    print("=" * 50)
    print("GATE IN CONTROLLER RESTART")
    print("=" * 50)
    
    # Set environment
    set_environment()
    
    # Check config
    check_config()
    
    print("\n🚀 Starting Gate IN Controller...")
    print("   Arduino should connect to COM10")
    print("   Simulation mode: disabled")
    print("   Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Start controller
        subprocess.run([sys.executable, "main_gate_in.py"], check=True)
    except KeyboardInterrupt:
        print("\n✅ Controller stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting controller: {e}")

if __name__ == "__main__":
    main() 