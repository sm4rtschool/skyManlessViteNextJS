#!/usr/bin/env python3
"""
Test Hardware Detector
"""

import logging
from hardware_detector import HardwareDetector

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')

print("🔍 Testing Hardware Detector")
print("=" * 30)

# Create detector
detector = HardwareDetector()

# Test COM port detection
print("1. Testing COM port detection...")
detected = detector.detect_com_ports()
print(f"   Arduino ports: {detected['arduino']}")
print(f"   Card reader ports: {detected['card_reader']}")

# Test Arduino connection
if detected['arduino']:
    print(f"\n2. Testing Arduino on {detected['arduino'][0]}...")
    result = detector.test_arduino_connection(detected['arduino'][0])
    print(f"   Arduino connected: {result}")
else:
    print("\n2. No Arduino ports detected")

# Test card reader connection
if detected['card_reader']:
    print(f"\n3. Testing Card Reader on {detected['card_reader'][0]}...")
    result = detector.test_card_reader_connection(detected['card_reader'][0])
    print(f"   Card Reader connected: {result}")
else:
    print("\n3. No Card Reader ports detected")

print("\n✅ Test completed") 