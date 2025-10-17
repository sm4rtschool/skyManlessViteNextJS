"""
Camera Controller untuk Manless Parking System
Menggunakan OpenCV untuk capture dan streaming video dari webcam laptop atau IP camera
"""

import asyncio
import base64
import logging
from typing import Optional, AsyncGenerator
import cv2
import numpy as np
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class CameraController:
    def __init__(self, camera_source: str = "0"):
        """
        Initialize camera controller
        Args:
            camera_source: Camera source - bisa berupa:
                          - "0", "1", dst. untuk webcam laptop (device index)
                          - "http://ip:port/stream" untuk IP camera
                          - "rtsp://ip:port/stream" untuk RTSP camera
        """
        self.camera_source = camera_source
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_streaming = False
        self.is_initialized = False
        self.frame_count = 0
        self.last_frame = None
        self.camera_type = "unknown"
        
    def _parse_camera_source(self):
        """Parse camera source untuk menentukan tipe kamera"""
        if self.camera_source.isdigit():
            # Webcam laptop dengan device index
            self.camera_type = "webcam"
            return int(self.camera_source)
        elif self.camera_source.startswith(('http://', 'https://')):
            # IP Camera dengan HTTP stream
            self.camera_type = "ip_camera_http"
            return self.camera_source
        elif self.camera_source.startswith('rtsp://'):
            # IP Camera dengan RTSP stream
            self.camera_type = "ip_camera_rtsp" 
            return self.camera_source
        else:
            # Default ke webcam
            self.camera_type = "webcam"
            return 0
        
    async def initialize(self) -> bool:
        """Initialize camera connection"""
        try:
            camera_source = self._parse_camera_source()
            logger.info(f"Initializing camera: {self.camera_type} - {camera_source}")
            
            # Try to open camera
            self.cap = cv2.VideoCapture(camera_source)
            
            if not self.cap.isOpened():
                logger.warning(f"Cannot open camera {camera_source}, using dummy mode")
                self.cap = None
                self.is_initialized = True  # Dummy mode
                return True
            
            # Set camera properties untuk webcam
            if self.camera_type == "webcam":
                # Set resolusi yang umum didukung webcam laptop
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                # Auto-focus untuk webcam laptop
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            
            # Test capture
            ret, frame = self.cap.read()
            if ret:
                self.is_initialized = True
                logger.info(f"Camera initialized successfully: {self.camera_type}")
                logger.info(f"Resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
                return True
            else:
                logger.error("Failed to capture test frame")
                self.cap.release()
                self.cap = None
                return False
                
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            return False
    
    async def set_camera_source(self, new_source: str) -> bool:
        """Mengganti sumber kamera secara dinamis"""
        try:
            # Stop streaming jika sedang aktif
            was_streaming = self.is_streaming
            if was_streaming:
                await self.stop_stream()
            
            # Cleanup kamera lama
            await self.cleanup()
            
            # Set sumber baru
            self.camera_source = new_source
            self.is_initialized = False
            
            # Initialize kamera baru
            success = await self.initialize()
            
            # Resume streaming jika sebelumnya aktif
            if success and was_streaming:
                await self.start_stream()
                
            logger.info(f"Camera source changed to: {new_source}")
            return success
            
        except Exception as e:
            logger.error(f"Error changing camera source: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup camera resources"""
        try:
            self.is_streaming = False
            if self.cap:
                self.cap.release()
                self.cap = None
            self.is_initialized = False
            logger.info("Camera cleanup completed")
        except Exception as e:
            logger.error(f"Error during camera cleanup: {e}")
    
    def is_connected(self) -> bool:
        """Check if camera is connected"""
        return self.is_initialized and (self.cap is not None or True)  # True for dummy mode
    
    async def start_stream(self):
        """Start camera streaming"""
        if not self.is_initialized:
            await self.initialize()
        self.is_streaming = True
        logger.info("Camera streaming started")
    
    async def stop_stream(self):
        """Stop camera streaming"""
        self.is_streaming = False
        logger.info("Camera streaming stopped")
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame"""
        try:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.frame_count += 1
                    self.last_frame = frame
                    
                    # Flip frame untuk webcam laptop (mirror effect)
                    if self.camera_type == "webcam":
                        frame = cv2.flip(frame, 1)
                    
                    return frame
            
            # Dummy mode - generate a placeholder frame
            return self._generate_dummy_frame()
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return self._generate_dummy_frame()
    
    def _generate_dummy_frame(self) -> np.ndarray:
        """Generate a dummy frame for testing"""
        # Create a 1280x720 dummy frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        frame[:] = (30, 30, 50)  # Dark blue background
        
        # Add gradient effect
        for i in range(720):
            frame[i, :, 0] = min(255, 30 + i // 3)  # Blue gradient
        
        # Add text overlay
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, "MANLESS PARKING SYSTEM", (300, 250), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        cv2.putText(frame, f"Camera Demo Mode - {self.camera_type.upper()}", (400, 300), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, timestamp, (450, 350), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, f"Frame: {self.frame_count} | Source: {self.camera_source}", (50, 680), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Add a moving rectangle to simulate activity
        pos_x = int((self.frame_count * 3) % 1200)
        cv2.rectangle(frame, (pos_x, 400), (pos_x + 80, 450), (0, 0, 255), 3)
        
        # Add camera status indicator
        cv2.circle(frame, (100, 100), 30, (0, 255, 0), -1)
        cv2.putText(frame, "LIVE", (75, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        self.frame_count += 1
        return frame
    
    def frame_to_base64(self, frame: np.ndarray, quality: int = 80) -> str:
        """Convert frame to base64 string for WebSocket transmission"""
        try:
            # Resize frame untuk optimasi bandwidth jika terlalu besar
            height, width = frame.shape[:2]
            if width > 1280:
                scale = 1280 / width
                new_width = 1280
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Encode frame to JPEG
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
            _, buffer = cv2.imencode('.jpg', frame, encode_params)
            
            # Convert to base64
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            return frame_base64
            
        except Exception as e:
            logger.error(f"Error converting frame to base64: {e}")
            return ""
    
    async def get_frame_stream(self) -> AsyncGenerator[str, None]:
        """Async generator untuk streaming frames"""
        logger.info("Starting frame stream generator")
        
        while self.is_streaming:
            try:
                frame = self.capture_frame()
                if frame is not None:
                    frame_base64 = self.frame_to_base64(frame)
                    if frame_base64:
                        yield frame_base64
                
                # 30 FPS untuk webcam, 15 FPS untuk IP camera (untuk menghemat bandwidth)
                fps_delay = 0.033 if self.camera_type == "webcam" else 0.067
                await asyncio.sleep(fps_delay)
                
            except Exception as e:
                logger.error(f"Error in frame stream: {e}")
                await asyncio.sleep(1)
                
        logger.info("Frame stream generator stopped")
    
    async def capture_image(self, save_path: Optional[str] = None) -> Optional[str]:
        """Capture and save image"""
        try:
            frame = self.capture_frame()
            if frame is None:
                return None
            
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"captures/capture_{timestamp}.jpg"
            
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Save image
            success = cv2.imwrite(save_path, frame)
            if success:
                logger.info(f"Image saved: {save_path}")
                return save_path
            else:
                logger.error("Failed to save image")
                return None
                
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
            return None
    
    def get_camera_info(self) -> dict:
        """Get camera information"""
        info = {
            "camera_source": self.camera_source,
            "camera_type": self.camera_type,
            "is_connected": self.is_connected(),
            "is_streaming": self.is_streaming,
            "frame_count": self.frame_count,
            "is_initialized": self.is_initialized
        }
        
        if self.cap and self.cap.isOpened():
            info.update({
                "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": int(self.cap.get(cv2.CAP_PROP_FPS)),
                "codec": int(self.cap.get(cv2.CAP_PROP_FOURCC)),
                "brightness": self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
                "contrast": self.cap.get(cv2.CAP_PROP_CONTRAST)
            })
        
        return info

    async def set_camera_property(self, property_name: str, value: float) -> bool:
        """Set camera property (hanya untuk webcam)"""
        if not self.cap or not self.cap.isOpened() or self.camera_type != "webcam":
            return False
            
        try:
            property_map = {
                'brightness': cv2.CAP_PROP_BRIGHTNESS,
                'contrast': cv2.CAP_PROP_CONTRAST,
                'saturation': cv2.CAP_PROP_SATURATION,
                'hue': cv2.CAP_PROP_HUE,
                'gain': cv2.CAP_PROP_GAIN,
                'exposure': cv2.CAP_PROP_EXPOSURE
            }
            
            if property_name in property_map:
                return self.cap.set(property_map[property_name], value)
            return False
            
        except Exception as e:
            logger.error(f"Error setting camera property {property_name}: {e}")
            return False

    def get_available_cameras(self) -> list:
        """Deteksi kamera yang tersedia di sistem"""
        available_cameras = []
        
        # Check webcam devices (0-10)
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append({
                        'source': str(i),
                        'type': 'webcam',
                        'name': f'Webcam {i}',
                        'status': 'available'
                    })
                cap.release()
        
        return available_cameras

# Test function untuk debugging
async def test_camera():
    """Test camera functionality"""
    print("Testing Camera Controller...")
    
    # Test webcam
    camera = CameraController("0")
    success = await camera.initialize()
    print(f"Webcam initialization: {'Success' if success else 'Failed'}")
    
    if success:
        await camera.start_stream()
        print("Camera info:", camera.get_camera_info())
        
        # Capture beberapa frames
        for i in range(5):
            frame = camera.capture_frame()
            print(f"Frame {i+1}: {'OK' if frame is not None else 'Failed'}")
            await asyncio.sleep(0.1)
        
        await camera.stop_stream()
        await camera.cleanup()
    
    print("Camera test completed")

if __name__ == "__main__":
    asyncio.run(test_camera())