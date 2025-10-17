#!/usr/bin/env python3
"""
CONTROLLER APPLICATION - MANLESS PARKING SYSTEM
================================================
Aplikasi middleware yang berfungsi sebagai penghubung antara frontend dan backend.
Controller ini akan diletakkan di mini PC di dalam tiket dispenser.

Arsitektur: Frontend → Controller → Backend

Controller menangani:
- Hardware (kamera, card reader, Arduino/gate)
- Business logic parkir
- Komunikasi dengan backend untuk data management
- Komunikasi dengan frontend melalui API dan WebSocket
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import asyncio
import json
import logging
import aiohttp
import websockets
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

# Import hardware controllers
from hardware.camera import CameraController
from hardware.card_reader import CardReaderController
from hardware.arduino import ArduinoController
from hardware_detector import hardware_detector

# Pydantic models
class ParkingEntryRequest(BaseModel):
    card_id: str
    license_plate: Optional[str] = None

class ParkingExitRequest(BaseModel):
    card_id: str
    payment_method: str = "card"

class GateControlRequest(BaseModel):
    action: str  # "open" or "close"
    duration: Optional[int] = 10  # seconds

class CameraControlRequest(BaseModel):
    command: str  # "start_stream", "stop_stream", "capture_image"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_HOST = "localhost"
BACKEND_PORT = 8000
BACKEND_WS_URL = f"ws://{BACKEND_HOST}:{BACKEND_PORT}/ws"
BACKEND_API_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api"

class BackendClient:
    """Client untuk komunikasi dengan backend"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws_connection: Optional[websockets.WebSocketServerProtocol] = None
        
    async def start(self):
        """Initialize backend client"""
        self.session = aiohttp.ClientSession()
        logger.info("Backend client initialized")
        
    async def stop(self):
        """Cleanup backend client"""
        if self.session:
            await self.session.close()
        if self.ws_connection:
            await self.ws_connection.close()
        logger.info("Backend client stopped")
    
    async def send_to_backend(self, data: dict) -> dict:
        """Send data to backend via HTTP API"""
        try:
            async with self.session.post(
                f"{BACKEND_API_URL}/controller/data",
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Backend API error: {response.status}")
                    return {"error": f"Backend API error: {response.status}"}
        except Exception as e:
            logger.error(f"Error communicating with backend: {e}")
            return {"error": str(e)}
    
    async def get_from_backend(self, endpoint: str) -> dict:
        """Get data from backend via HTTP API"""
        try:
            async with self.session.get(
                f"{BACKEND_API_URL}/{endpoint}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Backend API error: {response.status}")
                    return {"error": f"Backend API error: {response.status}"}
        except Exception as e:
            logger.error(f"Error getting data from backend: {e}")
            return {"error": str(e)}

# Global instances
backend_client = BackendClient()
camera_controller = CameraController("0")  # Default webcam
card_reader_controller = CardReaderController()
arduino_controller = ArduinoController()

# WebSocket connections
active_connections: List[WebSocket] = []
camera_connections: List[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Controller Application...")
    await backend_client.start()
    await camera_controller.initialize()
    await card_reader_controller.initialize()
    await arduino_controller.initialize()
    
    # Start hardware detection
    def hardware_status_callback(status):
        """Callback untuk mengirim status hardware ke frontend"""
        asyncio.create_task(broadcast_hardware_status(status))
    
    hardware_detector.set_status_callback(hardware_status_callback)
    hardware_detector.start_detection()
    logger.info("✅ Hardware detection started")
    
    logger.info("✅ Controller Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down Controller Application...")
    hardware_detector.stop_detection()
    await backend_client.stop()
    await camera_controller.cleanup()
    await card_reader_controller.cleanup()
    await arduino_controller.cleanup()
    logger.info("✅ Controller Application shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title="Parking Controller API",
    description="Middleware controller untuk sistem parkir manless",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React Create React App
        "http://localhost:5173",  # Vite React App
        "http://127.0.0.1:5173",  # Vite alternative
        "http://127.0.0.1:3000",   # React alternative
        "http://localhost:8080"   # Additional frontend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# WEBSOCKET ENDPOINTS
# ========================================

@app.websocket("/ws")
async def controller_websocket(websocket: WebSocket):
    """Main WebSocket endpoint untuk komunikasi dengan frontend"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info("Frontend WebSocket connected")
    
    try:
        while True:
            data = await websocket.receive_text()
            await handle_websocket_message(data, websocket)
    except WebSocketDisconnect:
        logger.info("Frontend WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.websocket("/ws/camera")
async def camera_websocket(websocket: WebSocket):
    """WebSocket endpoint khusus untuk streaming kamera"""
    await websocket.accept()
    camera_connections.append(websocket)
    logger.info("Camera WebSocket connected")
    
    try:
        # Start camera streaming
        await camera_controller.start_stream()
        
        # Send camera info
        camera_info = await camera_controller.get_camera_info()
        await websocket.send_json({
            "type": "camera_info",
            "payload": camera_info
        })
        
        # Stream frames
        async for frame_data in camera_controller.get_frame_stream():
            if websocket in camera_connections:
                await websocket.send_json({
                    "type": "camera_frame",
                    "payload": {
                        "frame": frame_data["frame"],
                        "timestamp": datetime.now().isoformat(),
                        "camera_info": frame_data.get("info", {})
                    }
                })
            else:
                break
                
    except WebSocketDisconnect:
        logger.info("Camera WebSocket disconnected")
    except Exception as e:
        logger.error(f"Camera WebSocket error: {e}")
    finally:
        if websocket in camera_connections:
            camera_connections.remove(websocket)
        # Stop streaming if no camera connections
        if not camera_connections:
            await camera_controller.stop_stream()

async def handle_websocket_message(message: str, websocket: WebSocket):
    """Handle incoming WebSocket messages from frontend"""
    try:
        data = json.loads(message)
        message_type = data.get("type")
        payload = data.get("payload", {})
        
        logger.info(f"Received WebSocket message: {message_type}")
        
        if message_type == "parking_entry":
            await handle_parking_entry(payload, websocket)
            
        elif message_type == "parking_exit":
            await handle_parking_exit(payload, websocket)
            
        elif message_type == "gate_control":
            await handle_gate_control(payload, websocket)
            
        elif message_type == "camera_control":
            await handle_camera_control(payload, websocket)
            
        elif message_type == "card_scan":
            await handle_card_scan(payload, websocket)
            
        elif message_type == "system_status":
            await handle_system_status_request(websocket)
            
        else:
            logger.warning(f"Unknown message type: {message_type}")
            await websocket.send_json({
                "type": "error",
                "payload": {"message": f"Unknown message type: {message_type}"}
            })
            
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")
        await websocket.send_json({
            "type": "error",
            "payload": {"message": str(e)}
        })

# ========================================
# WEBSOCKET MESSAGE HANDLERS
# ========================================

async def handle_parking_entry(payload: dict, websocket: WebSocket):
    """Handle parking entry request"""
    card_id = payload.get("card_id")
    
    if not card_id:
        await websocket.send_json({
            "type": "error",
            "payload": {"message": "Card ID is required"}
        })
        return
    
    # Validasi kartu dengan backend
    card_data = await backend_client.get_from_backend(f"cards/{card_id}")
    
    if "error" in card_data:
        await websocket.send_json({
            "type": "entry_denied",
            "payload": {
                "reason": "Card validation failed",
                "card_id": card_id,
                "timestamp": datetime.now().isoformat()
            }
        })
        return
    
    # Jika kartu valid, buka gate
    gate_result = await arduino_controller.open_gate()
    
    # Capture image
    image_path = await camera_controller.capture_image()
    
    # Send entry data to backend
    entry_data = {
        "type": "parking_entry",
        "card_id": card_id,
        "image_path": image_path,
        "timestamp": datetime.now().isoformat(),
        "gate_status": gate_result
    }
    
    backend_response = await backend_client.send_to_backend(entry_data)
    
    # Send response to frontend
    await websocket.send_json({
        "type": "entry_approved",
        "payload": {
            "card_id": card_id,
            "image_path": image_path,
            "timestamp": datetime.now().isoformat(),
            "backend_response": backend_response
        }
    })

async def handle_parking_exit(payload: dict, websocket: WebSocket):
    """Handle parking exit request"""
    card_id = payload.get("card_id")
    payment_method = payload.get("payment_method", "card")
    
    if not card_id:
        await websocket.send_json({
            "type": "error",
            "payload": {"message": "Card ID is required"}
        })
        return
    
    # Get parking session from backend
    session_data = await backend_client.get_from_backend(f"parking-sessions/{card_id}")
    
    if "error" in session_data:
        await websocket.send_json({
            "type": "exit_denied",
            "payload": {
                "reason": "No active parking session found",
                "card_id": card_id,
                "timestamp": datetime.now().isoformat()
            }
        })
        return
    
    # Calculate payment
    payment_data = await backend_client.get_from_backend(f"calculate-payment/{card_id}")
    
    # Capture exit image
    image_path = await camera_controller.capture_image()
    
    # Process exit
    exit_data = {
        "type": "parking_exit",
        "card_id": card_id,
        "payment_method": payment_method,
        "payment_amount": payment_data.get("amount", 0),
        "image_path": image_path,
        "timestamp": datetime.now().isoformat()
    }
    
    backend_response = await backend_client.send_to_backend(exit_data)
    
    # Open gate for exit
    gate_result = await arduino_controller.open_gate()
    
    # Send response to frontend
    await websocket.send_json({
        "type": "exit_approved",
        "payload": {
            "card_id": card_id,
            "payment_amount": payment_data.get("amount", 0),
            "payment_method": payment_method,
            "image_path": image_path,
            "timestamp": datetime.now().isoformat(),
            "backend_response": backend_response
        }
    })

async def handle_gate_control(payload: dict, websocket: WebSocket):
    """Handle manual gate control"""
    action = payload.get("action", "close")
    duration = payload.get("duration", 10)
    
    if action == "open":
        result = await arduino_controller.open_gate(duration)
    elif action == "close":
        result = await arduino_controller.close_gate()
    else:
        await websocket.send_json({
            "type": "error",
            "payload": {"message": f"Invalid gate action: {action}"}
        })
        return
    
    await websocket.send_json({
        "type": "gate_status",
        "payload": {
            "action": action,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    })

async def handle_camera_control(payload: dict, websocket: WebSocket):
    """Handle camera control commands"""
    command = payload.get("command")
    
    if command == "start_stream":
        await camera_controller.start_stream()
        result = "stream_started"
    elif command == "stop_stream":
        await camera_controller.stop_stream()
        result = "stream_stopped"
    elif command == "capture_image":
        image_path = await camera_controller.capture_image()
        result = {"image_captured": image_path}
    else:
        await websocket.send_json({
            "type": "error",
            "payload": {"message": f"Invalid camera command: {command}"}
        })
        return
    
    camera_info = await camera_controller.get_camera_info()
    
    await websocket.send_json({
        "type": "camera_status",
        "payload": {
            "command": command,
            "result": result,
            "camera_info": camera_info,
            "timestamp": datetime.now().isoformat()
        }
    })

async def handle_card_scan(payload: dict, websocket: WebSocket):
    """Handle card scan request"""
    # Simulate or read actual card
    card_data = await card_reader_controller.read_card()
    
    if card_data:
        await websocket.send_json({
            "type": "card_detected",
            "payload": {
                "card_id": card_data.get("card_id"),
                "card_type": card_data.get("card_type"),
                "timestamp": datetime.now().isoformat()
            }
        })
    else:
        await websocket.send_json({
            "type": "card_scan_timeout",
            "payload": {
                "message": "No card detected",
                "timestamp": datetime.now().isoformat()
            }
        })

async def handle_system_status_request(websocket: WebSocket):
    """Handle system status request"""
    # Get hardware status from detector
    hardware_status = hardware_detector.get_status()
    
    camera_status = await camera_controller.get_status()
    card_reader_status = await card_reader_controller.get_status()
    arduino_status = await arduino_controller.get_status()
    
    # Get backend status
    backend_status = await backend_client.get_from_backend("system/status")
    
    await websocket.send_json({
        "type": "system_status",
        "payload": {
            "controller": {
                "camera": camera_status,
                "card_reader": card_reader_status,
                "arduino": arduino_status,
                "hardware_detector": hardware_status,
                "timestamp": datetime.now().isoformat()
            },
            "backend": backend_status
        }
    })

async def broadcast_hardware_status(status: dict):
    """Broadcast hardware status ke semua WebSocket connections"""
    message = {
        "type": "hardware_status",
        "payload": status,
        "timestamp": datetime.now().isoformat()
    }
    
    # Send ke semua active connections
    for websocket in active_connections:
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting hardware status: {e}")
            # Remove disconnected websocket
            if websocket in active_connections:
                active_connections.remove(websocket)

# ========================================
# API ENDPOINTS UNTUK BACKEND
# ========================================

@app.post("/api/backend/gate/control")
async def backend_gate_control(request: GateControlRequest):
    """API endpoint untuk menerima perintah gate control dari backend"""
    try:
        logger.info(f"Backend gate control request: {request.action}")
        
        if request.action == "open":
            success = await arduino_controller.open_gate(duration=request.duration)
        elif request.action == "close":
            success = await arduino_controller.close_gate()
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        # Send status update ke backend
        await backend_client.send_to_backend({
            "type": "gate_status_update",
            "gate_status": "open" if request.action == "open" else "closed",
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": success,
            "action": request.action,
            "gate_status": "open" if request.action == "open" else "closed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in backend gate control: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backend/hardware/status")
async def get_hardware_status():
    """API endpoint untuk memberikan status hardware ke backend"""
    try:
        # Get status dari hardware detector
        hardware_status = hardware_detector.get_status()
        
        # Debug logging
        logger.info(f"Hardware detector status: {hardware_status}")
        
        status = {
            "arduino": hardware_status["arduino"]["connected"],
            "card_reader": hardware_status["card_reader"]["connected"],
            "camera": camera_controller.is_connected() if camera_controller else False,
            "gate_status": "closed",  # TODO: Get actual gate status from Arduino
            "hardware_details": hardware_status,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Final hardware status: {status}")
        return status
        
    except Exception as e:
        logger.error(f"Error getting hardware status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backend/parking/entry")
async def backend_parking_entry(request: ParkingEntryRequest):
    """API endpoint untuk menerima parking entry dari backend"""
    try:
        logger.info(f"Backend parking entry: {request.card_id}")
        
        # Process parking entry
        # TODO: Add business logic here
        
        # Send confirmation ke backend
        await backend_client.send_to_backend({
            "type": "parking_entry_confirmed",
            "card_id": request.card_id,
            "license_plate": request.license_plate,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "card_id": request.card_id,
            "license_plate": request.license_plate,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in backend parking entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backend/parking/exit")
async def backend_parking_exit(request: ParkingExitRequest):
    """API endpoint untuk menerima parking exit dari backend"""
    try:
        logger.info(f"Backend parking exit: {request.card_id}")
        
        # Process parking exit
        # TODO: Add business logic here
        
        # Send confirmation ke backend
        await backend_client.send_to_backend({
            "type": "parking_exit_confirmed",
            "card_id": request.card_id,
            "payment_method": request.payment_method,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "card_id": request.card_id,
            "payment_method": request.payment_method,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in backend parking exit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# BACKGROUND TASKS
# ========================================

async def send_hardware_status_to_backend():
    """Background task untuk mengirim status hardware ke backend secara periodik"""
    while True:
        try:
            status = {
                "type": "hardware_status_update",
                "arduino": arduino_controller.is_connected() if arduino_controller else False,
                "card_reader": card_reader_controller.is_connected() if card_reader_controller else False,
                "camera": camera_controller.is_connected() if camera_controller else False,
                "gate_status": "closed",  # TODO: Get actual gate status
                "timestamp": datetime.now().isoformat()
            }
            
            await backend_client.send_to_backend(status)
            logger.debug("Hardware status sent to backend")
            
        except Exception as e:
            logger.error(f"Error sending hardware status to backend: {e}")
        
        await asyncio.sleep(30)  # Send status every 30 seconds

# ========================================
# EXISTING API ENDPOINTS
# ========================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Parking Controller API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def get_system_status():
    """Get comprehensive system status"""
    camera_status = await camera_controller.get_status()
    card_reader_status = await card_reader_controller.get_status()
    arduino_status = await arduino_controller.get_status()
    backend_status = await backend_client.get_from_backend("system/status")
    
    return {
        "controller": {
            "camera": camera_status,
            "card_reader": card_reader_status,
            "arduino": arduino_status
        },
        "backend": backend_status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/parking/entry")
async def parking_entry(request: ParkingEntryRequest):
    """Process parking entry via HTTP API"""
    # Similar logic to WebSocket handler
    card_data = await backend_client.get_from_backend(f"cards/{request.card_id}")
    
    if "error" in card_data:
        raise HTTPException(status_code=400, detail="Card validation failed")
    
    gate_result = await arduino_controller.open_gate()
    image_path = await camera_controller.capture_image()
    
    entry_data = {
        "type": "parking_entry",
        "card_id": request.card_id,
        "license_plate": request.license_plate,
        "image_path": image_path,
        "timestamp": datetime.now().isoformat()
    }
    
    backend_response = await backend_client.send_to_backend(entry_data)
    
    return {
        "status": "approved",
        "card_id": request.card_id,
        "image_path": image_path,
        "backend_response": backend_response,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/parking/exit")
async def parking_exit(request: ParkingExitRequest):
    """Process parking exit via HTTP API"""
    session_data = await backend_client.get_from_backend(f"parking-sessions/{request.card_id}")
    
    if "error" in session_data:
        raise HTTPException(status_code=400, detail="No active parking session found")
    
    payment_data = await backend_client.get_from_backend(f"calculate-payment/{request.card_id}")
    image_path = await camera_controller.capture_image()
    
    exit_data = {
        "type": "parking_exit",
        "card_id": request.card_id,
        "payment_method": request.payment_method,
        "payment_amount": payment_data.get("amount", 0),
        "image_path": image_path,
        "timestamp": datetime.now().isoformat()
    }
    
    backend_response = await backend_client.send_to_backend(exit_data)
    gate_result = await arduino_controller.open_gate()
    
    return {
        "status": "approved",
        "card_id": request.card_id,
        "payment_amount": payment_data.get("amount", 0),
        "payment_method": request.payment_method,
        "backend_response": backend_response,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/gate/control")
async def control_gate(request: GateControlRequest):
    """Manual gate control"""
    if request.action == "open":
        result = await arduino_controller.open_gate(request.duration)
    elif request.action == "close":
        result = await arduino_controller.close_gate()
    else:
        raise HTTPException(status_code=400, detail=f"Invalid gate action: {request.action}")
    
    return {
        "action": request.action,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/camera/control")
async def control_camera(request: CameraControlRequest):
    """Camera control endpoint"""
    if request.command == "start_stream":
        await camera_controller.start_stream()
        result = "stream_started"
    elif request.command == "stop_stream":
        await camera_controller.stop_stream()
        result = "stream_stopped"
    elif request.command == "capture_image":
        image_path = await camera_controller.capture_image()
        result = {"image_captured": image_path}
    else:
        raise HTTPException(status_code=400, detail=f"Invalid camera command: {request.command}")
    
    camera_info = await camera_controller.get_camera_info()
    
    return {
        "command": request.command,
        "result": result,
        "camera_info": camera_info,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/camera/stream")
async def get_camera_stream():
    """Get camera stream as HTTP endpoint"""
    return StreamingResponse(
        camera_controller.get_http_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Different port from backend
        reload=True,
        log_level="info"
    ) 