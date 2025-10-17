"""
Manless Parking System - Backend API
FastAPI backend untuk sistem parkir otomatis dengan fitur:
- Live camera streaming via WebSocket
- Database management
- API untuk komunikasi dengan controller
- Real-time logging
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
import requests
import threading
import websockets

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.api.routes import router as api_router
from app.database.database import engine, get_db
from app.database.model import Base
from app.hardware.camera import CameraController
# from app.hardware.arduino import ArduinoController  # Dihapus - Arduino ada di controller
# from app.hardware.card_reader import CardReaderController  # Dihapus - Card reader ada di controller
from camera_config import DEFAULT_CAMERA_URL, get_camera_url, get_camera_url_for_gate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Controller configuration
CONTROLLER_HOST = "localhost"
CONTROLLER_PORT = 8001
CONTROLLER_URL = f"http://{CONTROLLER_HOST}:{CONTROLLER_PORT}"

class ControllerClient:
    """Client untuk komunikasi dengan controller menggunakan requests"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 5
        
    async def start(self):
        """Initialize controller client"""
        logger.info("Controller client initialized")
        
    async def stop(self):
        """Cleanup controller client"""
        self.session.close()
        logger.info("Controller client stopped")
    
    def get_controller_status(self) -> dict:
        """Get status dari controller (synchronous)"""
        try:
            logger.info(f"Requesting status from controller: {CONTROLLER_URL}/api/status")
            response = self.session.get(f"{CONTROLLER_URL}/api/status", timeout=5)
            logger.info(f"Controller response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Controller status received successfully")
                logger.debug(f"Controller data: {data}")
                return data
            else:
                logger.error(f"Controller API error: {response.status_code} - {response.text}")
                return {"error": f"Controller API error: {response.status_code}"}
        except requests.ConnectionError as e:
            logger.error(f"Error connecting to controller: {e}")
            return {"error": f"Controller connection failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error getting controller status: {e}")
            return {"error": str(e)}
    
    def send_gate_command(self, action: str, gate_id: str = "gate_in") -> dict:
        """Send gate control command to controller (synchronous)"""
        try:
            response = self.session.post(
                f"{CONTROLLER_URL}/api/backend/gate/control",
                json={"action": action, "duration": 10},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Gate control error: {response.status_code}")
                return {"error": f"Gate control failed: {response.status_code}"}
        except Exception as e:
            logger.error(f"Error sending gate command: {e}")
            return {"error": str(e)}

# Create FastAPI app
app = FastAPI(
    title="Manless Parking System API",
    description="Backend API untuk sistem parkir otomatis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware untuk komunikasi dengan React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ubah ke wildcard agar semua origin diizinkan
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

# Global connection manager
manager = ConnectionManager()

# Hardware controllers (hanya camera di backend)
camera_controller = None

# Controller client
controller_client = ControllerClient()

# Pydantic models untuk API
class SystemStatus(BaseModel):
    camera: bool = False
    arduino: bool = False  # Status dari controller
    card_reader: bool = False  # Status dari controller
    gate_status: str = "closed"  # Status dari controller
    controller_connected: bool = False  # Status koneksi ke controller

class LogEntry(BaseModel):
    id: Optional[int] = None
    timestamp: datetime
    event_type: str
    details: str
    card_id: Optional[str] = None

class GateControlRequest(BaseModel):
    action: str  # "open" or "close"
    gate_id: str = "gate_in"  # "gate_in" or "gate_out"

# Global system status
system_status = SystemStatus()

@app.on_event("startup")
async def startup_event():
    """Initialize camera controller and database on startup"""
    global camera_controller
    
    logger.info("Starting Manless Parking System Backend...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Initialize controller client
    try:
        await controller_client.start()
        logger.info("Controller client initialized")
    except Exception as e:
        logger.error(f"Error initializing controller client: {e}")
    
    # Initialize camera controller (hanya camera di backend)
    try:
        # Camera controller dengan Dahua IP camera untuk Gate IN
        gate_in_camera_url = get_camera_url_for_gate("gate_in", "primary")
        logger.info(f"Initializing Gate IN camera: {gate_in_camera_url}")
        camera_controller = CameraController(camera_source=gate_in_camera_url)
        system_status.camera = await camera_controller.initialize()
        
        logger.info(f"Camera initialization complete. Status: {system_status.camera}")
        
    except Exception as e:
        logger.error(f"Error initializing camera: {e}")
    
    # Mulai background task untuk mendengarkan controller
    asyncio.create_task(listen_to_controller_task())

async def listen_to_controller_task():
    """Menghubungkan ke WebSocket controller dan meneruskan pesan ke frontend."""
    controller_ws_url = f"ws://{CONTROLLER_HOST}:{CONTROLLER_PORT}/ws"
    while True:
        try:
            async with websockets.connect(controller_ws_url) as websocket:
                logger.info(f"✅ Terhubung ke WebSocket Controller di {controller_ws_url}")
                system_status.controller_connected = True
                while True:
                    message_str = await websocket.recv()
                    message = json.loads(message_str)
                    logger.debug(f"Menerima dari Controller: {message}")

                    # Teruskan pesan hardware_status langsung ke semua klien frontend
                    if message.get("type") == "hardware_status":
                        await manager.broadcast(json.dumps(message))
                        
                        # Update status global di backend juga
                        payload = message.get("payload", {})
                        system_status.arduino = payload.get("arduino", {}).get("connected", False)
                        system_status.card_reader = payload.get("card_reader", {}).get("connected", False)
                        system_status.gate_status = payload.get("arduino", {}).get("gate_status", "unknown").split(',')[0]

        except (websockets.exceptions.ConnectionClosedError, ConnectionRefusedError) as e:
            logger.warning(f"Koneksi ke Controller WebSocket terputus: {e}. Mencoba lagi dalam 5 detik...")
            system_status.controller_connected = False
            system_status.arduino = False
            system_status.card_reader = False
        except Exception as e:
            logger.error(f"Error pada listener Controller WebSocket: {e}. Mencoba lagi dalam 5 detik...")
        
        await asyncio.sleep(5)

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Manless Parking System Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "architecture": "Backend hanya menangani camera dan database. Hardware control ada di controller terpisah."
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system_status": system_status.dict()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint untuk real-time communication"""
    await manager.connect(websocket)
    
    try:
        # Kirim status awal (mungkin tidak sepenuhnya akurat hingga pesan pertama dari controller)
        initial_status_payload = {
            "type": "hardware_status",
            "payload": {
                "arduino": {"connected": system_status.arduino, "gate_status": system_status.gate_status},
                "card_reader": {"connected": system_status.card_reader},
                "camera": {"connected": system_status.camera}
            }
        }
        await manager.send_personal_message(json.dumps(initial_status_payload), websocket)
        
        while True:
            # Tetap buka koneksi untuk menerima pesan dari frontend jika diperlukan
            data = await websocket.receive_text()
            message = json.loads(data)
            await handle_websocket_message(message, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Frontend client disconnected")
    except Exception as e:
        logger.error(f"Frontend WebSocket error: {e}")
        manager.disconnect(websocket)

@app.websocket("/ws/camera")
async def camera_websocket_endpoint(websocket: WebSocket):
    """Camera WebSocket endpoint untuk streaming video"""
    await manager.connect(websocket)
    
    try:
        # Send camera info
        if camera_controller:
            camera_info = {
                "connected": camera_controller.is_connected(),
                "source": getattr(camera_controller, 'current_source', 'webcam'),
                "resolution": getattr(camera_controller, 'resolution', '1280x720'),
                "fps": getattr(camera_controller, 'fps', 30)
            }
            await manager.send_personal_message(
                json.dumps({
                    "type": "camera_info",
                    "payload": camera_info
                }),
                websocket
            )
            
            # Start camera streaming
            await camera_controller.start_stream()
            
            # Stream frames
            async for frame_data in camera_controller.get_frame_stream():
                if websocket in manager.active_connections:
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "camera_frame",
                            "payload": {
                                "frame": frame_data,
                                "timestamp": datetime.now().isoformat(),
                                "camera_info": camera_info
                            }
                        }),
                        websocket
                    )
                    await asyncio.sleep(0.033)  # ~30 FPS
                else:
                    break
        else:
            # Camera not available
            await manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "payload": {"message": "Camera not available"}
                }),
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Camera WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Camera WebSocket error: {e}")
        manager.disconnect(websocket)
    finally:
        # Stop streaming jika tidak ada koneksi kamera lagi
        if camera_controller:
            camera_connections = [conn for conn in manager.active_connections 
                                if hasattr(conn, '_camera_connection')]
            if not camera_connections:
                await camera_controller.stop_stream()

async def handle_websocket_message(message: dict, websocket: WebSocket):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    payload = message.get("payload", {})
    
    logger.info(f"📨 Received WebSocket message: type='{message_type}', payload={payload}")
    
    try:
        # Handle ping/pong for connection health
        if message_type == "ping":
            await manager.send_personal_message(
                json.dumps({
                    "type": "pong",
                    "payload": {
                        "timestamp": datetime.now().isoformat(),
                        "original_timestamp": payload.get("timestamp")
                    }
                }),
                websocket
            )
            return
            
        elif message_type == "request_camera_stream":
            if camera_controller:
                await camera_controller.start_stream()
                
        elif message_type == "stop_camera_stream":
            if camera_controller:
                await camera_controller.stop_stream()
                
        elif message_type == "gate_control":
            # Forward gate control ke controller via API
            gate_action = payload.get("action")
            gate_id = payload.get("gate_id", "gate_in")
            
            # TODO: Implement API call ke controller
            logger.info(f"Gate control request: {gate_action} for {gate_id}")
            
            # Send response back
            await manager.send_personal_message(
                json.dumps({
                    "type": "gate_control_response",
                    "payload": {
                        "success": True,
                        "action": gate_action,
                        "gate_id": gate_id,
                        "message": f"Gate control request sent to controller: {gate_action}"
                    }
                }),
                websocket
            )
            
        elif message_type == "get_system_status":
            # Send current system status
            await manager.send_personal_message(
                json.dumps({
                    "type": "system_status",
                    "payload": system_status.dict()
                }),
                websocket
            )
            
        else:
            logger.warning(f"Unknown message type: {message_type}")
            
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "payload": {"message": f"Error processing message: {str(e)}"}
            }),
            websocket
        )

async def camera_stream_handler(websocket: WebSocket):
    """Background task untuk camera streaming"""
    try:
        while websocket in manager.active_connections:
            if camera_controller and camera_controller.is_connected():
                # Update camera status
                system_status.camera = True
                
                # Send camera status update
                await manager.send_personal_message(
                    json.dumps({
                        "type": "camera_status_update",
                        "payload": {
                            "connected": True,
                            "timestamp": datetime.now().isoformat()
                        }
                    }),
                    websocket
                )
            else:
                system_status.camera = False
                
            await asyncio.sleep(5)  # Check every 5 seconds
            
    except Exception as e:
        logger.error(f"Camera stream handler error: {e}")

# API Endpoints untuk komunikasi dengan controller
@app.post("/api/v1/gate/control")
async def control_gate_api(request: GateControlRequest):
    """API endpoint untuk control gate (akan di-forward ke controller)"""
    try:
        logger.info(f"Gate control request: {request.action} for {request.gate_id}")
        
        # Forward request ke controller
        result = controller_client.send_gate_command(request.action, request.gate_id)
        
        if "error" not in result:
            # Update local status
            if request.action == "open":
                system_status.gate_status = "open"
            elif request.action == "close":
                system_status.gate_status = "closed"
                
            return {
                "success": True,
                "message": f"Gate control command sent successfully",
                "gate_id": request.gate_id,
                "action": request.action,
                "controller_response": result,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
        
    except Exception as e:
        logger.error(f"Error controlling gate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/system/status")
async def get_system_status():
    """Get current system status (combined from backend and controller)"""
    try:
        # Get fresh status from controller
        controller_status = controller_client.get_controller_status()
        
        if "error" not in controller_status:
            hardware = controller_status.get("hardware", {})
            
            # Parse Arduino status
            arduino_info = hardware.get("arduino", {})
            arduino_connected = False
            gate_status = "closed"
            
            if isinstance(arduino_info, dict):
                arduino_connected = arduino_info.get("connected", False)
                gate_info = arduino_info.get("gate", {})
                if isinstance(gate_info, dict):
                    gate_status = gate_info.get("status", "closed")
            
            # Parse Card Reader status  
            card_reader_info = hardware.get("card_reader", {})
            card_reader_connected = False
            if isinstance(card_reader_info, dict):
                card_reader_connected = card_reader_info.get("connected", False)
            
            # Combine backend camera status with controller hardware status
            combined_status = {
                "camera": system_status.camera,  # From backend
                "arduino": arduino_connected,  # From controller
                "card_reader": card_reader_connected,  # From controller
                "gate_status": gate_status,  # From controller
                "controller_connected": True,
                "timestamp": datetime.now().isoformat(),
                "backend_status": "online",
                "controller_info": {
                    "gate_id": controller_status.get("gate_id"),
                    "gate_name": controller_status.get("gate_name"),
                    "simulation_mode": controller_status.get("simulation_mode", False)
                }
            }
            
            # Update global status
            system_status.arduino = combined_status["arduino"]
            system_status.card_reader = combined_status["card_reader"]
            system_status.gate_status = combined_status["gate_status"]
            system_status.controller_connected = True
            
            return combined_status
        else:
            # Controller not available, return backend-only status
            return {
                "camera": system_status.camera,
                "arduino": False,
                "card_reader": False,
                "gate_status": "unknown",
                "controller_connected": False,
                "timestamp": datetime.now().isoformat(),
                "backend_status": "online",
                "error": controller_status.get("error", "Controller not available")
            }
            
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "camera": system_status.camera,
            "arduino": False,
            "card_reader": False,
            "gate_status": "unknown",
            "controller_connected": False,
            "timestamp": datetime.now().isoformat(),
            "backend_status": "online",
            "error": str(e)
        }

@app.get("/api/v1/logs")
async def get_logs(skip: int = 0, limit: int = 100):
    """Get system logs"""
    # TODO: Implement log retrieval dari database
    return {
        "logs": [],
        "total": 0,
        "skip": skip,
        "limit": limit
    }

# Camera endpoints (tetap ada di backend)
@app.get("/api/camera/info")
async def get_camera_info():
    """Get camera information"""
    if camera_controller:
        return {
            "connected": camera_controller.is_connected(),
            "source": getattr(camera_controller, 'current_source', 'webcam'),
            "resolution": getattr(camera_controller, 'resolution', '1280x720'),
            "fps": getattr(camera_controller, 'fps', 30),
            "status": "active"
        }
    else:
        return {
            "connected": False,
            "source": "none",
            "resolution": "none",
            "fps": 0,
            "status": "inactive"
        }

@app.get("/api/camera/available")
async def get_available_cameras():
    """Get list of available cameras"""
    cameras = [
        {
            "id": "gate_in_primary",
            "name": "Gate IN - Primary Camera",
            "url": get_camera_url_for_gate("gate_in", "primary"),
            "type": "dahua_ip",
            "status": "available"
        },
        {
            "id": "gate_in_backup",
            "name": "Gate IN - Backup Camera", 
            "url": get_camera_url_for_gate("gate_in", "backup"),
            "type": "webcam",
            "status": "available"
        }
    ]
    
    return {"cameras": cameras}

class CameraSourceRequest(BaseModel):
    source: str

@app.post("/api/camera/source")
async def set_camera_source(request: CameraSourceRequest):
    """Set camera source"""
    try:
        if camera_controller:
            await camera_controller.set_source(request.source)
            return {
                "success": True,
                "message": f"Camera source changed to {request.source}",
                "current_source": request.source
            }
        else:
            raise HTTPException(status_code=404, detail="Camera controller not available")
            
    except Exception as e:
        logger.error(f"Error setting camera source: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class CameraSettingsRequest(BaseModel):
    property_name: str
    value: float

@app.post("/api/camera/settings")
async def set_camera_settings(request: CameraSettingsRequest):
    """Set camera settings"""
    try:
        if camera_controller:
            await camera_controller.set_property(request.property_name, request.value)
            return {
                "success": True,
                "message": f"Camera {request.property_name} set to {request.value}",
                "property": request.property_name,
                "value": request.value
            }
        else:
            raise HTTPException(status_code=404, detail="Camera controller not available")
            
    except Exception as e:
        logger.error(f"Error setting camera settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/camera/capture")
async def capture_image():
    """Capture image from camera"""
    try:
        if camera_controller and camera_controller.is_connected():
            image_data = await camera_controller.capture_image()
            return {
                "success": True,
                "image_data": image_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Camera not available")
            
    except Exception as e:
        logger.error(f"Error capturing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/camera/stream")
async def camera_stream_endpoint():
    """Camera stream endpoint"""
    if not camera_controller:
        raise HTTPException(status_code=404, detail="Camera not available")
    
    async def generate_stream():
        try:
            await camera_controller.start_stream()
            async for frame_data in camera_controller.get_frame_stream():
                yield frame_data
        except Exception as e:
            logger.error(f"Camera stream error: {e}")
    
    return StreamingResponse(
        generate_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/api/camera/mjpeg")
async def camera_mjpeg_stream():
    """MJPEG camera stream endpoint"""
    if not camera_controller:
        raise HTTPException(status_code=404, detail="Camera not available")
    
    async def generate_mjpeg():
        try:
            await camera_controller.start_stream()
            async for frame_data in camera_controller.get_frame_stream():
                yield f"--frame\r\nContent-Type: image/jpeg\r\n\r\n{frame_data}\r\n"
        except Exception as e:
            logger.error(f"MJPEG stream error: {e}")
    
    return StreamingResponse(
        generate_mjpeg(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# Parking management endpoints
class ParkingEntryRequest(BaseModel):
    card_id: str
    license_plate: Optional[str] = None
    vehicle_type: Optional[str] = "car"

class ParkingExitRequest(BaseModel):
    card_id: str
    payment_method: str = "card"
    amount: Optional[float] = None

@app.post("/api/v1/parking/entry")
async def parking_entry(request: ParkingEntryRequest):
    """Record parking entry"""
    try:
        # TODO: Implement database entry
        logger.info(f"Parking entry: Card {request.card_id}, License {request.license_plate}")
        
        return {
            "success": True,
            "message": "Parking entry recorded",
            "card_id": request.card_id,
            "license_plate": request.license_plate,
            "vehicle_type": request.vehicle_type,
            "entry_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error recording parking entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/parking/exit")
async def parking_exit(request: ParkingExitRequest):
    """Record parking exit"""
    try:
        # TODO: Implement database exit
        logger.info(f"Parking exit: Card {request.card_id}, Payment {request.payment_method}")
        
        return {
            "success": True,
            "message": "Parking exit recorded",
            "card_id": request.card_id,
            "payment_method": request.payment_method,
            "amount": request.amount,
            "exit_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error recording parking exit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/emergency/force-exit")
async def force_exit_session(request: dict):
    """Emergency force exit session"""
    try:
        # TODO: Implement emergency exit
        logger.warning(f"Emergency force exit requested: {request}")
        
        return {
            "success": True,
            "message": "Emergency exit executed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error executing emergency exit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/controller")
async def debug_controller():
    """Debug endpoint untuk test komunikasi dengan controller"""
    try:
        logger.info("=== DEBUG: Testing controller communication ===")
        
        # Test controller status
        controller_status = controller_client.get_controller_status()
        
        debug_info = {
            "controller_url": CONTROLLER_URL,
            "controller_response": controller_status,
            "backend_system_status": system_status.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Debug info: {debug_info}")
        return debug_info
        
    except Exception as e:
        logger.error(f"Debug error: {e}")
        return {
            "error": str(e),
            "controller_url": CONTROLLER_URL,
            "timestamp": datetime.now().isoformat()
        }

@app.get("/debug/test-controller-direct")
async def debug_test_controller_direct():
    """Debug endpoint untuk test controller langsung"""
    import requests
    try:
        response = requests.get("http://localhost:8001/api/status", timeout=5)
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 