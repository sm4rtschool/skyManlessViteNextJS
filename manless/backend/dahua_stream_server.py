#!/usr/bin/env python3
"""
Dahua Camera MJPEG Stream Server
Mengkonversi RTSP stream dari camera Dahua ke MJPEG yang bisa ditampilkan di browser
"""

import cv2
import numpy as np
from flask import Flask, Response
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Camera configuration
DAHUA_RTSP_URL = "rtsp://admin:SKYUPH@2025@10.5.50.129:554/cam/realmonitor?channel=1&subtype=1"

# Global variables
camera = None
is_streaming = False

app = Flask(__name__)

def init_camera():
    """Initialize camera connection"""
    global camera
    try:
        camera = cv2.VideoCapture(DAHUA_RTSP_URL)
        if camera.isOpened():
            logger.info(f"✅ Camera connected: {DAHUA_RTSP_URL}")
            return True
        else:
            logger.error(f"❌ Failed to connect to camera: {DAHUA_RTSP_URL}")
            return False
    except Exception as e:
        logger.error(f"❌ Camera initialization error: {e}")
        return False

def generate_frames():
    """Generate MJPEG frames from RTSP stream"""
    global camera, is_streaming
    
    if not camera or not camera.isOpened():
        logger.error("❌ Camera not initialized")
        return
    
    is_streaming = True
    logger.info("🎥 Starting MJPEG stream...")
    
    while is_streaming:
        try:
            ret, frame = camera.read()
            if ret:
                # Resize frame for better performance
                frame = cv2.resize(frame, (640, 480))
                
                # Convert to JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    logger.warning("Failed to encode frame")
            else:
                logger.warning("Failed to read frame from camera")
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error generating frame: {e}")
            time.sleep(0.1)
    
    logger.info("🛑 MJPEG stream stopped")

@app.route('/')
def index():
    """Main page with video stream"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dahua Camera Live Stream</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                background: #1a1a1a; 
                color: white; 
                text-align: center;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
            }
            img { 
                max-width: 640px; 
                border: 2px solid #333; 
                border-radius: 8px; 
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            .status { 
                margin: 10px 0; 
                padding: 10px; 
                border-radius: 4px; 
                font-weight: bold;
            }
            .connected { background: #2d5a2d; }
            .disconnected { background: #5a2d2d; }
            .info {
                background: #2d2d5a;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📹 Dahua Camera Live Stream</h1>
            <div id="status" class="status connected">Status: Connected</div>
            
            <img src="/video_feed" alt="Camera Stream">
            
            <div class="info">
                <h3>📋 Camera Information:</h3>
                <ul>
                    <li><strong>IP Address:</strong> 10.5.50.129</li>
                    <li><strong>Stream Type:</strong> RTSP → MJPEG</li>
                    <li><strong>Resolution:</strong> 640x480 (optimized)</li>
                    <li><strong>Quality:</strong> 80% JPEG</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/video_feed')
def video_feed():
    """MJPEG video stream endpoint"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def get_status():
    """Get camera status"""
    global camera, is_streaming
    if camera and camera.isOpened():
        return {"status": "connected", "streaming": is_streaming}
    else:
        return {"status": "disconnected", "streaming": False}

def cleanup():
    """Cleanup camera resources"""
    global camera, is_streaming
    is_streaming = False
    if camera:
        camera.release()
    logger.info("🧹 Camera resources cleaned up")

if __name__ == "__main__":
    try:
        # Initialize camera
        if init_camera():
            logger.info("🚀 Starting MJPEG stream server...")
            logger.info("📺 Access stream at: http://localhost:8001")
            
            # Start Flask app
            app.run(host='0.0.0.0', port=8001, debug=False, threaded=True)
        else:
            logger.error("❌ Failed to initialize camera. Exiting.")
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
    finally:
        cleanup() 