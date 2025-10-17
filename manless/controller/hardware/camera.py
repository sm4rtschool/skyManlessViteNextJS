"""
Camera Controller untuk Controller Application
Menangani operasi kamera untuk sistem parkir manless
"""

import cv2
import asyncio
import base64
import logging
from datetime import datetime
import numpy as np
from typing import Optional, Dict, AsyncGenerator
import os

logger = logging.getLogger(__name__)

class CameraController:
    """Controller untuk menangani operasi kamera"""
    
    def __init__(self, camera_source: str = "0"):
        self.camera_source = camera_source
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_streaming = False
        self.frame_width = 640
        self.frame_height = 480
        self.fps = 30
        self.capture_dir = "captures"
        
        # Ensure capture directory exists
        os.makedirs(self.capture_dir, exist_ok=True)
        
    async def initialize(self):
        """Initialize camera controller"""
        try:
            # Convert string to int if it's a number (webcam)
            if self.camera_source.isdigit():
                source = int(self.camera_source)
            else:
                source = self.camera_source
                
            self.cap = cv2.VideoCapture(source)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera source: {self.camera_source}")
                return False
                
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            logger.info(f"Camera initialized successfully: {self.camera_source}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup camera resources"""
        if self.cap:
            self.cap.release()
            logger.info("Camera resources cleaned up")
    
    async def start_stream(self):
        """Start camera streaming"""
        if not self.cap or not self.cap.isOpened():
            await self.initialize()
            
        self.is_streaming = True
        logger.info("Camera streaming started")
    
    async def stop_stream(self):
        """Stop camera streaming"""
        self.is_streaming = False
        logger.info("Camera streaming stopped")
    
    async def get_frame(self) -> Optional[Dict]:
        """Get single frame from camera"""
        if not self.cap or not self.cap.isOpened():
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to read frame from camera")
            return None
            
        # Encode frame to base64
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "frame": frame_base64,
            "timestamp": datetime.now().isoformat(),
            "width": frame.shape[1],
            "height": frame.shape[0]
        }
    
    async def get_frame_stream(self) -> AsyncGenerator[Dict, None]:
        """Get continuous frame stream"""
        while self.is_streaming:
            frame_data = await self.get_frame()
            if frame_data:
                yield frame_data
            await asyncio.sleep(1/self.fps)  # Control frame rate
    
    async def capture_image(self) -> Optional[str]:
        """Capture and save image"""
        if not self.cap or not self.cap.isOpened():
            await self.initialize()
            
        ret, frame = self.cap.read()
        if not ret:
            logger.error("Failed to capture image")
            return None
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join(self.capture_dir, filename)
        
        # Save image
        success = cv2.imwrite(filepath, frame)
        if success:
            logger.info(f"Image captured: {filepath}")
            return filepath
        else:
            logger.error("Failed to save captured image")
            return None
    
    async def get_camera_info(self) -> Dict:
        """Get camera information"""
        if not self.cap or not self.cap.isOpened():
            return {
                "connected": False,
                "source": self.camera_source,
                "status": "disconnected"
            }
            
        return {
            "connected": True,
            "source": self.camera_source,
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": int(self.cap.get(cv2.CAP_PROP_FPS)),
            "streaming": self.is_streaming,
            "status": "connected"
        }
    
    async def is_connected(self) -> bool:
        """Check if camera is connected"""
        if not self.cap:
            return False
        return self.cap.isOpened()

    async def get_status(self) -> Dict:
        """Get camera status"""
        info = await self.get_camera_info()
        return {
            "name": "Camera",
            "connected": info["connected"],
            "streaming": self.is_streaming,
            "source": self.camera_source,
            "details": info
        }
    
    async def set_source(self, new_source: str) -> bool:
        """Change camera source"""
        # Stop current stream
        await self.stop_stream()
        
        # Release current camera
        if self.cap:
            self.cap.release()
            
        # Set new source and reinitialize
        self.camera_source = new_source
        success = await self.initialize()
        
        if success:
            logger.info(f"Camera source changed to: {new_source}")
        else:
            logger.error(f"Failed to change camera source to: {new_source}")
            
        return success
    
    async def set_resolution(self, width: int, height: int) -> bool:
        """Set camera resolution"""
        if not self.cap or not self.cap.isOpened():
            return False
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Verify the resolution was set
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if actual_width == width and actual_height == height:
            self.frame_width = width
            self.frame_height = height
            logger.info(f"Camera resolution set to: {width}x{height}")
            return True
        else:
            logger.warning(f"Camera resolution set to: {actual_width}x{actual_height} (requested: {width}x{height})")
            return False
    
    async def get_http_stream(self):
        """Get HTTP stream generator for FastAPI StreamingResponse"""
        async def generate():
            while self.is_streaming:
                frame_data = await self.get_frame()
                if frame_data:
                    # Decode base64 back to bytes for HTTP streaming
                    frame_bytes = base64.b64decode(frame_data["frame"])
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                await asyncio.sleep(1/self.fps)
        
        return generate()
    
    def get_available_cameras(self) -> list:
        """Get list of available camera sources"""
        available_cameras = []
        
        # Check webcams (0-10)
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append({
                    "id": str(i),
                    "name": f"Webcam {i}",
                    "type": "webcam"
                })
                cap.release()
        
        # TODO: Add IP camera detection if needed
        
        return available_cameras 