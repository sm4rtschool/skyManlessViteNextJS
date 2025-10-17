"""
Configuration file untuk Controller Application
Berisi pengaturan untuk hardware dan komunikasi dengan backend
"""

import os
from typing import Dict, Any

class ControllerConfig:
    """Konfigurasi untuk Controller Application"""
    
    # Server Configuration
    HOST = "0.0.0.0"
    PORT = 8001
    DEBUG = True
    
    # Backend Configuration
    BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
    BACKEND_API_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api"
    BACKEND_WS_URL = f"ws://{BACKEND_HOST}:{BACKEND_PORT}/ws"
    
    # Hardware Configuration
    CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "0")  # Default webcam
    CAMERA_WIDTH = int(os.getenv("CAMERA_WIDTH", "640"))
    CAMERA_HEIGHT = int(os.getenv("CAMERA_HEIGHT", "480"))
    CAMERA_FPS = int(os.getenv("CAMERA_FPS", "30"))
    
    # Card Reader Configuration
    CARD_READER_PORT = os.getenv("CARD_READER_PORT", "COM14")
    CARD_READER_BAUDRATE = int(os.getenv("CARD_READER_BAUDRATE", "9600"))
    CARD_READER_TIMEOUT = int(os.getenv("CARD_READER_TIMEOUT", "10"))
    
    # Arduino Configuration
    ARDUINO_PORT = os.getenv("ARDUINO_PORT", "COM8")
    ARDUINO_BAUDRATE = int(os.getenv("ARDUINO_BAUDRATE", "9600"))
    GATE_AUTO_CLOSE_DELAY = int(os.getenv("GATE_AUTO_CLOSE_DELAY", "10"))
    
    # Directory Configuration
    CAPTURE_DIR = os.getenv("CAPTURE_DIR", "captures")
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Security Configuration
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8080"
    ]
    
    # Hardware Simulation (for testing without actual hardware)
    SIMULATE_HARDWARE = os.getenv("SIMULATE_HARDWARE", "True").lower() == "true"
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [cls.CAPTURE_DIR, cls.LOG_DIR]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_hardware_config(cls) -> Dict[str, Any]:
        """Get hardware configuration as dictionary"""
        return {
            "camera": {
                "source": cls.CAMERA_SOURCE,
                "width": cls.CAMERA_WIDTH,
                "height": cls.CAMERA_HEIGHT,
                "fps": cls.CAMERA_FPS
            },
            "card_reader": {
                "port": cls.CARD_READER_PORT,
                "baudrate": cls.CARD_READER_BAUDRATE,
                "timeout": cls.CARD_READER_TIMEOUT
            },
            "arduino": {
                "port": cls.ARDUINO_PORT,
                "baudrate": cls.ARDUINO_BAUDRATE,
                "gate_auto_close_delay": cls.GATE_AUTO_CLOSE_DELAY
            },
            "simulation": cls.SIMULATE_HARDWARE
        }
    
    @classmethod
    def get_backend_config(cls) -> Dict[str, str]:
        """Get backend configuration as dictionary"""
        return {
            "host": cls.BACKEND_HOST,
            "port": str(cls.BACKEND_PORT),
            "api_url": cls.BACKEND_API_URL,
            "ws_url": cls.BACKEND_WS_URL
        }

# Development Configuration
class DevelopmentConfig(ControllerConfig):
    DEBUG = True
    SIMULATE_HARDWARE = True
    LOG_LEVEL = "DEBUG"

# Production Configuration
class ProductionConfig(ControllerConfig):
    DEBUG = False
    SIMULATE_HARDWARE = False
    LOG_LEVEL = "INFO"
    HOST = "0.0.0.0"

# Test Configuration
class TestConfig(ControllerConfig):
    DEBUG = True
    SIMULATE_HARDWARE = True
    LOG_LEVEL = "DEBUG"
    CAMERA_SOURCE = "0"
    
# Get configuration based on environment
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "test": TestConfig
}

ENV = os.getenv("CONTROLLER_ENV", "development")
config = config_map.get(ENV, DevelopmentConfig) 