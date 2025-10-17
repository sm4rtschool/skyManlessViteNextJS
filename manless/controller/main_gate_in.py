#!/usr/bin/env python3
"""
Gate IN Controller - Sistem Parkir Manless
Port: 8001
Handles: Entry, Card Reading, Camera, Gate Control
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import uvicorn
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Import configuration
import config_gate_in as config

# Import hardware controllers (use existing from controller directory)
from hardware.camera import CameraController
from hardware.card_reader import CardReaderController  
from hardware.arduino import ArduinoController
from hardware_detector import hardware_detector

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# --- Helper Functions ---
async def broadcast_to_all(message: dict):
    """Broadcast message to all connected clients"""
    if not active_connections:
        return
    
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            disconnected.append(connection)
    
    for connection in disconnected:
        active_connections.remove(connection)

async def get_unified_system_status():
    """Membangun dan mengembalikan objek status sistem yang konsisten dari HardwareDetector."""
    hw_status = hardware_detector.get_status()
    
    # Ambil semua data dari HardwareDetector, sumber kebenaran tunggal
    arduino_status = hw_status.get("arduino", {}) if isinstance(hw_status, dict) else {}
    card_reader_status = hw_status.get("card_reader", {}) if isinstance(hw_status, dict) else {}
    
    # Ambil detail kamera (ini tidak menyebabkan konflik)
    camera_details = await camera.get_status() if config.CAMERA_ENABLED else {}
    cam_conn = camera_details.get("connected", False) if isinstance(camera_details, dict) else False
    
    unified_hardware_status = {
        "camera": {
            "connected": cam_conn,
            "source": camera_details.get("source") if isinstance(camera_details, dict) else None,
            "streaming": camera_details.get("streaming", False) if isinstance(camera_details, dict) else False
        },
        "arduino": {
            "connected": arduino_status.get("connected", False),
            "port": arduino_status.get("port"),
            "gate_status": arduino_status.get("gate_status", "unknown") # Ambil dari detector!
        },
        "card_reader": {
            "connected": card_reader_status.get("connected", False),
            "port": card_reader_status.get("port")
        }
    }
    
    return {
        "gate_id": config.GATE_ID,
        "gate_name": config.GATE_NAME,
        "timestamp": datetime.now().isoformat(),
        "hardware": unified_hardware_status,
        "status": "ok"
    }

async def broadcast_unified_status():
    """Builds the unified status and broadcasts it to all WebSocket clients."""
    unified_status = await get_unified_system_status()
    message = {
        "type": "hardware_status",
        "payload": unified_status.get('hardware', {}),
        "timestamp": datetime.now().isoformat()
    }
    await broadcast_to_all(message)
# --- End of Helper Functions ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info(f"Starting {config.GATE_NAME} Controller...")
    
    # Definisikan callback untuk hardware detector
    def hardware_status_callback(status):
        """Callback untuk menyiarkan status TERPADU yang baru ke frontend."""
        # Dapatkan event loop yang sedang berjalan atau buat yang baru jika tidak ada
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Pastikan ini dijalankan di event loop yang benar
        asyncio.run_coroutine_threadsafe(broadcast_unified_status(), loop)
    
    hardware_detector.set_status_callback(hardware_status_callback)
    
    # Inisialisasi dan mulai semua komponen
    if config.ARDUINO_ENABLED:
        await arduino.initialize()
    if config.CAMERA_ENABLED:
        await camera.initialize()
    if config.CARD_READER_ENABLED:
        await card_reader.initialize()
        
    hardware_detector.start_detection()
    
    logger.info("System startup complete. All components initialized.")
    
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down system...")
        hardware_detector.stop_detection()
        
        if config.ARDUINO_ENABLED:
            await arduino.cleanup()
        if config.CAMERA_ENABLED:
            await camera.cleanup()
        if config.CARD_READER_ENABLED:
            await card_reader.cleanup()
            
        logger.info("System shutdown complete.")

# Initialize FastAPI app
app = FastAPI(
    title=f"Gate IN Controller - {config.GATE_NAME}",
    description=f"Controller untuk {config.GATE_LOCATION}",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Controller dapat diakses dari central hub
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ParkingEntryRequest(BaseModel):
    card_id: str
    license_plate: Optional[str] = None
    timestamp: Optional[str] = None

class GateControlRequest(BaseModel):
    action: str  # "open", "close"
    duration: int = config.GATE_OPEN_DURATION

class CameraControlRequest(BaseModel):
    command: str  # "capture_image", "start_stream", "stop_stream"

# Initialize hardware controllers
camera = CameraController(config.CAMERA_SOURCE)
card_reader = CardReaderController(config.CARD_READER_PORT)
arduino = ArduinoController(config.ARDUINO_PORT)

# WebSocket connections
active_connections: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint untuk real-time communication"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WebSocket client connected to {config.GATE_NAME}")
    
    try:
        while True:
            data = await websocket.receive_text()
            await handle_websocket_message(data, websocket)
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from {config.GATE_NAME}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

async def handle_websocket_message(message: str, websocket: WebSocket):
    """Handle incoming WebSocket messages"""
    try:
        data = json.loads(message)
        message_type = data.get("type")
        payload = data.get("payload", {})
        
        if message_type == "card_scan":
            # Handle card scan simulation
            card_id = payload.get("card_id", "TEST_CARD_001")
            
            # Validate card and process entry
            result = await process_parking_entry({
                "card_id": card_id,
                "license_plate": payload.get("license_plate"),
                "timestamp": datetime.now().isoformat()
            })
            
            await websocket.send_json({
                "type": "entry_result",
                "payload": result
            })
            
        elif message_type == "gate_control":
            # Handle manual gate control
            action = payload.get("action", "open")
            duration = payload.get("duration", config.GATE_OPEN_DURATION)
            
            result = await control_gate(action, duration)
            await websocket.send_json({
                "type": "gate_status",
                "payload": result
            })
            
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")
        await websocket.send_json({
            "type": "error",
            "payload": {"message": str(e)}
        })

async def broadcast_hardware_status(status: dict):
    """DEPRECATED: This function is replaced by broadcast_unified_status to avoid confusion."""
    logger.warning("broadcast_hardware_status is deprecated. Use broadcast_unified_status.")
    await broadcast_unified_status()

async def process_parking_entry(request_data: dict) -> dict:
    """Process parking entry request"""
    try:
        card_id = request_data["card_id"]
        license_plate = request_data.get("license_plate")
        
        logger.info(f"Processing entry for card: {card_id}")
        
        # Simulate card validation
        if config.SIMULATION_MODE:
            # Simulate different card types
            card_valid = True
            card_type = "visitor"
            vehicle_type = "car"
        else:
            # Real card validation would go here
            card_valid = await validate_card(card_id)
            card_type = await get_card_type(card_id)
            vehicle_type = await detect_vehicle_type()
        
        if not card_valid:
            return {
                "status": "denied",
                "reason": "Invalid card",
                "card_id": card_id,
                "timestamp": datetime.now().isoformat()
            }
        
        # Capture image
        image_path = None
        if config.CAMERA_ENABLED:
            image_path = await camera.capture_image()
        
        # Open gate
        gate_result = await arduino.open_gate(config.GATE_OPEN_DURATION)
        
        # Log entry
        entry_log = {
            "card_id": card_id,
            "license_plate": license_plate,
            "card_type": card_type,
            "vehicle_type": vehicle_type,
            "image_path": image_path,
            "gate": config.GATE_ID,
            "timestamp": datetime.now().isoformat(),
            "gate_opened": gate_result
        }
        
        logger.info(f"Entry processed: {entry_log}")
        
        # Broadcast entry event
        await broadcast_to_all({
            "type": "entry_event",
            "payload": entry_log
        })
        
        return {
            "status": "approved",
            "card_id": card_id,
            "license_plate": license_plate,
            "card_type": card_type,
            "vehicle_type": vehicle_type,
            "image_path": image_path,
            "gate": config.GATE_ID,
            "timestamp": datetime.now().isoformat(),
            "message": "Entry approved, gate opened"
        }
        
    except Exception as e:
        logger.error(f"Error processing entry: {e}")
        return {
            "status": "error",
            "reason": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def validate_card(card_id: str) -> bool:
    """Validate parking card"""
    # In simulation mode, accept most cards
    if config.SIMULATION_MODE:
        return card_id not in ["BLOCKED_001", "EXPIRED_001"]
    
    # Real validation logic would go here
    return True

async def get_card_type(card_id: str) -> str:
    """Get card type"""
    # Simulate card type detection
    if card_id.startswith("EMP"):
        return "employee"
    elif card_id.startswith("VIP"):
        return "vip"
    elif card_id.startswith("MONTH"):
        return "monthly"
    else:
        return "visitor"

async def detect_vehicle_type() -> str:
    """Detect vehicle type using camera/sensors"""
    # Simulate vehicle detection
    return "car"  # Default

async def control_gate(action: str, duration: Optional[int] = None) -> dict:
    """Buka atau tutup gerbang menggunakan port dari hardware detector."""
    logger.info(f"Received gate control action: {action}")
    
    # Dapatkan status real-time dari hardware detector
    hw_status = hardware_detector.get_status()
    arduino_status = hw_status.get("arduino", {})
    
    is_arduino_connected = arduino_status.get("connected", False)
    arduino_port = arduino_status.get("port")
    
    if not is_arduino_connected or not arduino_port:
        logger.error("Cannot control gate: Arduino is not connected or port not found.")
        return {"status": "error", "message": "Arduino not connected"}

    logger.info(f"Executing gate control on port {arduino_port}")

    if action == "open":
        return await arduino.open_gate(duration or config.GATE_OPEN_DURATION, target_port=arduino_port)
    elif action == "close":
        return await arduino.close_gate(target_port=arduino_port)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid gate action: {action}")

# API Endpoints
@app.get("/api/status")
async def get_status():
    """Get the single, unified system status."""
    logger.debug("API request for unified system status")
    return await get_unified_system_status()

@app.post("/api/status")
async def post_status():
    return {"status": "ok", "message": "Status endpoint is read-only via POST."}

@app.post("/api/parking/entry")
async def parking_entry(request: ParkingEntryRequest):
    """Process parking entry"""
    return await process_parking_entry(request.dict())

@app.post("/api/gate/control")
async def gate_control(request: GateControlRequest):
    """Manual gate control"""
    return await control_gate(request.action, request.duration)

@app.post("/api/camera/control")
async def camera_control(request: CameraControlRequest):
    """Camera control"""
    if request.command == "capture_image":
        # Capture image
        image_path = await camera.capture_image()
        return {
            "command": request.command,
            "result": {"image_path": image_path},
            "timestamp": datetime.now().isoformat()
        }
    elif request.command == "start_stream":
        await camera.start_stream()
        return {
            "command": request.command,
            "result": "stream_started",
            "timestamp": datetime.now().isoformat()
        }
    elif request.command == "stop_stream":
        await camera.stop_stream()
        return {
            "command": request.command,
            "result": "stream_stopped", 
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=400, detail=f"Invalid command: {request.command}")

@app.get("/api/camera/stream")
async def get_camera_stream():
    """Get camera stream endpoint"""
    if not config.CAMERA_ENABLED:
        raise HTTPException(status_code=404, detail="Camera disabled")
    
    return f"http://{config.HOST}:{config.PORT}/api/camera/stream"

@app.get("/api/logs")
async def get_logs(limit: int = 50):
    """Get recent logs"""
    # This would read from log file in production
    return {
        "logs": [],
        "limit": limit,
        "gate": config.GATE_ID
    }

# ========================================
# BACKEND API ENDPOINTS
# ========================================

@app.post("/api/backend/gate/control")
async def backend_gate_control(request: GateControlRequest):
    """API endpoint untuk menerima perintah gate control dari backend"""
    try:
        logger.info(f"Backend gate control request: {request.action}")
        
        if request.action == "open":
            result = await control_gate("open", request.duration)
        elif request.action == "close":
            result = await control_gate("close")
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        return {
            "success": True,
            "action": request.action,
            "gate_status": result.get("status", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "controller_response": result
        }
        
    except Exception as e:
        logger.error(f"Error in backend gate control: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backend/hardware/status")
async def get_hardware_status_for_backend():
    """API endpoint untuk memberikan status hardware ke backend"""
    try:
        hardware_status = hardware_detector.get_status()
        logger.info(f"Hardware detector status: {hardware_status}")
        camera_status = await camera.get_status() if config.CAMERA_ENABLED else {"connected": False}
        arduino_status = await arduino.get_status() if config.ARDUINO_ENABLED else {"connected": False}
        status = {
            "arduino": hardware_status["arduino"]["connected"],
            "card_reader": hardware_status["card_reader"]["connected"],
            "camera": camera_status.get("connected", False),
            "gate_status": arduino_status.get("gate", {}).get("status", "closed"),
            "timestamp": datetime.now().isoformat(),
            "gate_id": config.GATE_ID,
            "gate_name": config.GATE_NAME,
            "hardware_details": hardware_status
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
        result = await process_parking_entry({
            "card_id": request.card_id,
            "license_plate": request.license_plate,
            "timestamp": request.timestamp or datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "card_id": request.card_id,
            "license_plate": request.license_plate,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in backend parking entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Startup and shutdown events now handled by lifespan context manager

if __name__ == "__main__":
    logger.info(f"Starting {config.GATE_NAME} Controller Server...")
    uvicorn.run(
        "main_gate_in:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    ) 