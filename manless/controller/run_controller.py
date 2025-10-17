#!/usr/bin/env python3
"""
Script untuk menjalankan Controller Application
Manless Parking System
"""

import uvicorn
import sys
import os
import logging
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config import config

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory
    config.create_directories()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                os.path.join(config.LOG_DIR, "controller.log"),
                encoding='utf-8'
            )
        ]
    )

def main():
    """Main function to run the controller"""
    
    print("🚀 MANLESS PARKING CONTROLLER")
    print("=" * 50)
    print(f"Environment: {os.getenv('CONTROLLER_ENV', 'development')}")
    print(f"Host: {config.HOST}:{config.PORT}")
    print(f"Backend: {config.BACKEND_API_URL}")
    print(f"Hardware Simulation: {config.SIMULATE_HARDWARE}")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower(),
        access_log=True
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Controller application stopped by user")
    except Exception as e:
        print(f"❌ Error starting controller: {e}")
        sys.exit(1) 