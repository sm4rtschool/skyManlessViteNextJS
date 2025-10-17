#!/usr/bin/env python3
"""
Script untuk menjalankan backend dengan error handling
"""

import sys
import os

def main():
    print("🐍 Starting Manless Parking Backend...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        # Test import dependencies
        print("📦 Testing dependencies...")
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")
        
        import uvicorn
        print(f"✅ Uvicorn")
        
        # Import our app
        print("📱 Loading application...")
        from app.main import app
        print("✅ Application loaded with MySQL integration")
        
        # Start server
        print("🚀 Starting server on http://localhost:8000...")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info",
            reload=False
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try: pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 