#!/usr/bin/env python3
"""
Konfigurasi Gate OUT Controller
Port: 8002
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gate Configuration
GATE_ID = "gate_out"
GATE_TYPE = "exit"
GATE_NAME = "Gate Keluar"
GATE_LOCATION = "Pintu Keluar Utama"

# Server Configuration
HOST = "0.0.0.0"
PORT = 8002
DEBUG = True
LOG_LEVEL = "INFO"

# Backend Configuration (Central Hub)
BACKEND_URL = "http://localhost:8000"
BACKEND_WEBSOCKET_URL = "ws://localhost:8000/ws"

# Hardware Configuration
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

# Camera Configuration
CAMERA_ENABLED = True
CAMERA_SOURCE = os.getenv("GATE_OUT_CAMERA_SOURCE", "0")  # Use same camera as Gate IN for testing
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Card Reader Configuration
CARD_READER_ENABLED = True
CARD_READER_PORT = os.getenv("GATE_OUT_CARD_READER_PORT", "COM5")
CARD_READER_BAUDRATE = 9600

# Arduino/Gate Controller Configuration
ARDUINO_ENABLED = True
ARDUINO_PORT = os.getenv("GATE_OUT_ARDUINO_PORT", "COM6")
ARDUINO_BAUDRATE = 9600
GATE_OPEN_DURATION = 10  # seconds

# Parking Configuration
PARKING_RATE_PER_HOUR = 5000  # IDR per jam
PARKING_MINIMUM_CHARGE = 3000  # IDR minimum charge
PARKING_MAX_DAILY_RATE = 50000  # IDR maximum per day

# Payment Configuration
ACCEPT_CASH = True
ACCEPT_CARD = True
ACCEPT_DIGITAL_WALLET = True
PAYMENT_TIMEOUT = 60  # seconds
CHANGE_DISPENSING = True

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - Gate OUT - %(message)s"
LOG_FILE = "logs/gate_out.log"

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
REQUIRE_PAYMENT_ON_EXIT = True
GRACE_PERIOD_MINUTES = 15  # Free parking under 15 minutes

# Alert Configuration
ENABLE_ALERTS = True
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "admin@parkir.com")
ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK", None)

# Performance Configuration
MAX_CONNECTIONS = 100
CONNECTION_TIMEOUT = 30
REQUEST_TIMEOUT = 10

# Cash/Payment Hardware Configuration
CASH_DISPENSER_ENABLED = True
CASH_DISPENSER_PORT = os.getenv("CASH_DISPENSER_PORT", "COM7")
CARD_PAYMENT_TERMINAL_ENABLED = True
CARD_PAYMENT_TERMINAL_PORT = os.getenv("CARD_TERMINAL_PORT", "COM8")

# Receipt Printer Configuration
RECEIPT_PRINTER_ENABLED = True
RECEIPT_PRINTER_PORT = os.getenv("RECEIPT_PRINTER_PORT", "COM9")
PRINT_RECEIPT = True
RECEIPT_TEMPLATE = "parking_receipt.template" 