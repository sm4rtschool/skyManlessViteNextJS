#!/usr/bin/env python3
"""
RTSP to MJPEG HTTP Stream Converter
Mengkonversi RTSP stream dari camera Dahua ke MJPEG yang bisa ditampilkan di browser
"""

import cv2
import numpy as np
from flask import Flask, Response, render_template_string
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Camera configuration
DAHUA_RTSP_URL = "rtsp://admin:SKYUPH@2025@10.5.50.129:554/cam/realmonitor?channel=1&subtype=1"

# Global variables
camera = None
frame_buffer = None
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
        <title>Dahua Camera MJPEG Stream</title>
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
            .video-container {
                position: relative;
                display: inline-block;
                margin: 20px 0;
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
            .loading { background: #5a5a2d; }
            button { 
                padding: 10px 20px; 
                margin: 5px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 14px;
            }
            .start { background: #4CAF50; color: white; }
            .stop { background: #f44336; color: white; }
            .info {
                background: #2d2d5a;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                text-align: left;
            }
            .info h3 { margin-top: 0; }
            .info ul { margin: 10px 0; padding-left: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📹 Dahua Camera Live Stream</h1>
            <div id="status" class="status disconnected">Status: Disconnected</div>
            
            <div class="video-container">
                <img id="video" src="" alt="Camera Stream" style="display: none;">
                <div id="placeholder" style="width: 640px; height: 480px; background: #333; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px;">
                    Click "Start Stream" to view camera
                </div>
            </div>
            
            <br>
            <button class="start" onclick="startStream()">Start Stream</button>
            <button class="stop" onclick="stopStream()">Stop Stream</button>
            
            <div class="info">
                <h3>📋 Camera Information:</h3>
                <ul>
                    <li><strong>IP Address:</strong> 10.5.50.129</li>
                    <li><strong>Username:</strong> admin</li>
                    <li><strong>Stream Type:</strong> RTSP → MJPEG</li>
                    <li><strong>Resolution:</strong> 640x480 (optimized)</li>
                    <li><strong>Frame Rate:</strong> ~25 FPS</li>
                    <li><strong>Quality:</strong> 80% JPEG</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>🔧 Technical Details:</h3>
                <ul>
                    <li><strong>Source:</strong> RTSP Sub Stream (352x288)</li>
                    <li><strong>Conversion:</strong> OpenCV + Flask</li>
                    <li><strong>Protocol:</strong> HTTP MJPEG</li>
                    <li><strong>Browser Support:</strong> All modern browsers</li>
                    <li><strong>Latency:</strong> Low (direct conversion)</li>
                </ul>
            </div>
        </div>

        <script>
            let streamActive = false;
            
            function startStream() {
                if (streamActive) return;
                
                document.getElementById('status').textContent = 'Status: Connecting...';
                document.getElementById('status').className = 'status loading';
                
                const video = document.getElementById('video');
                const placeholder = document.getElementById('placeholder');
                
                // Start MJPEG stream
                video.src = '/video_feed?t=' + Date.now();
                video.style.display = 'block';
                placeholder.style.display = 'none';
                
                video.onload = function() {
                    document.getElementById('status').textContent = 'Status: Connected';
                    document.getElementById('status').className = 'status connected';
                    streamActive = true;
                };
                
                video.onerror = function() {
                    document.getElementById('status').textContent = 'Status: Connection Failed';
                    document.getElementById('status').className = 'status disconnected';
                    video.style.display = 'none';
                    placeholder.style.display = 'flex';
                    streamActive = false;
                };
            }
            
            function stopStream() {
                const video = document.getElementById('video');
                const placeholder = document.getElementById('placeholder');
                
                video.src = '';
                video.style.display = 'none';
                placeholder.style.display = 'flex';
                
                document.getElementById('status').textContent = 'Status: Disconnected';
                document.getElementById('status').className = 'status disconnected';
                streamActive = false;
            }
            
            // Auto-start stream when page loads
            window.onload = function() {
                setTimeout(startStream, 1000);
            };
        </script>
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

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

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
            logger.info("📊 Status check at: http://localhost:8001/status")
            
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