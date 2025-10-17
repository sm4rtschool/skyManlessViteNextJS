#!/usr/bin/env python3
"""
Konfigurasi Gate IN Controller
Port: 8001
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gate Configuration
GATE_ID = "gate_in"
GATE_TYPE = "entry"
GATE_NAME = "Gate Masuk"
GATE_LOCATION = "Pintu Masuk Utama"

# Server Configuration
HOST = "0.0.0.0"
PORT = 8001
DEBUG = True
LOG_LEVEL = "INFO"

# Backend Configuration (Central Hub)
BACKEND_URL = "http://localhost:8000"
BACKEND_WEBSOCKET_URL = "ws://localhost:8000/ws"

# Hardware Configuration
SIMULATION_MODE = False  # Hard-coded to false

# Camera Configuration
CAMERA_ENABLED = True
CAMERA_SOURCE = os.getenv("GATE_IN_CAMERA_SOURCE", "0")  # Default webcam
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Card Reader Configuration
CARD_READER_ENABLED = True
CARD_READER_PORT = os.getenv("GATE_IN_CARD_READER_PORT", "COM1")
CARD_READER_BAUDRATE = 9600

# Arduino/Gate Controller Configuration
ARDUINO_ENABLED = True
ARDUINO_PORT = "COM8"  # Changed from COM10 to COM8
ARDUINO_BAUDRATE = 9600
GATE_OPEN_DURATION = 10  # seconds

# Parking Configuration
PARKING_RATE_PER_HOUR = 5000  # IDR per jam
PARKING_MINIMUM_CHARGE = 3000  # IDR minimum charge

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - Gate IN - %(message)s"
LOG_FILE = "logs/gate_in.log"

# Database Configuration (MySQL)
DATABASE_URL = os.getenv("DATABASE_URL", "mysql://parkir:parkir123@localhost/parkir_db")

# Security Configuration
ALLOWED_CARD_TYPES = ["employee", "visitor", "monthly", "vip"]
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_DURATION = 300  # seconds

# Business Rules
BUSINESS_HOURS_START = "06:00"
BUSINESS_HOURS_END = "22:00"
ALLOW_AFTER_HOURS = True
REQUIRE_PAYMENT_ON_ENTRY = False

# Alert Configuration
ENABLE_ALERTS = True
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "admin@parkir.com")
ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK", None)

# Performance Configuration
MAX_CONNECTIONS = 100
CONNECTION_TIMEOUT = 30
REQUEST_TIMEOUT = 10 