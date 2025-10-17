#!/usr/bin/env python3
"""
Gate OUT Controller - Sistem Parkir Manless
Port: 8002
Handles: Exit, Payment Processing, Receipt Printing, Gate Control
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
import config_gate_out as config

# Import hardware controllers (use existing from controller directory)
from hardware.camera import CameraController
from hardware.card_reader import CardReaderController  
from hardware.arduino import ArduinoController

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info(f"Starting {config.GATE_NAME} Controller...")
    
    # Initialize hardware
    if config.CAMERA_ENABLED:
        await camera.initialize()
        logger.info("Camera initialized")
    
    if config.CARD_READER_ENABLED:
        await card_reader.initialize()
        logger.info("Card reader initialized")
    
    if config.ARDUINO_ENABLED:
        await arduino.initialize()
        logger.info("Arduino initialized")
    
    logger.info(f"{config.GATE_NAME} Controller ready!")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {config.GATE_NAME} Controller...")
    
    # Cleanup hardware
    if config.CAMERA_ENABLED:
        await camera.cleanup()
    
    if config.CARD_READER_ENABLED:
        await card_reader.cleanup()
    
    if config.ARDUINO_ENABLED:
        await arduino.cleanup()

# Initialize FastAPI app
app = FastAPI(
    title=f"Gate OUT Controller - {config.GATE_NAME}",
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
class ParkingExitRequest(BaseModel):
    card_id: str
    license_plate: Optional[str] = None
    payment_method: Optional[str] = "cash"  # cash, card, subscription
    timestamp: Optional[str] = None

class PaymentRequest(BaseModel):
    card_id: str
    amount: float
    payment_method: str  # cash, card, qr_code
    currency: str = "IDR"

class GateControlRequest(BaseModel):
    action: str  # "open", "close"
    duration: int = config.GATE_OPEN_DURATION

class CameraControlRequest(BaseModel):
    command: str  # "capture_image", "start_stream", "stop_stream"

class ReceiptRequest(BaseModel):
    card_id: str
    amount: float
    payment_method: str
    entry_time: str
    exit_time: str

# Initialize hardware controllers
camera = CameraController(config.CAMERA_SOURCE)
card_reader = CardReaderController(config.CARD_READER_PORT, config.SIMULATION_MODE)
arduino = ArduinoController(config.ARDUINO_PORT, config.SIMULATION_MODE)

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
            # Handle card scan for exit
            card_id = payload.get("card_id", "TEST_CARD_001")
            
            # Process parking exit
            result = await process_parking_exit({
                "card_id": card_id,
                "license_plate": payload.get("license_plate"),
                "payment_method": payload.get("payment_method", "cash"),
                "timestamp": datetime.now().isoformat()
            })
            
            await websocket.send_json({
                "type": "exit_result",
                "payload": result
            })
            
        elif message_type == "payment_process":
            # Handle payment processing
            payment_data = payload
            result = await process_payment(payment_data)
            
            await websocket.send_json({
                "type": "payment_result",
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

async def process_parking_exit(request_data: dict) -> dict:
    """Process parking exit request"""
    try:
        card_id = request_data["card_id"]
        license_plate = request_data.get("license_plate")
        payment_method = request_data.get("payment_method", "cash")
        
        logger.info(f"Processing exit for card: {card_id}")
        
        # Simulate card validation and parking session lookup
        if config.SIMULATION_MODE:
            # Simulate parking session data
            card_valid = True
            entry_time = "2025-06-24T08:00:00"
            parking_duration = 2.5  # hours
            parking_fee = calculate_parking_fee(parking_duration)
            vehicle_type = "car"
        else:
            # Real validation would lookup from database
            card_valid = await validate_exit_card(card_id)
            if not card_valid:
                return {
                    "status": "denied",
                    "reason": "Invalid card or no entry record",
                    "card_id": card_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get parking session data
            session_data = await get_parking_session(card_id)
            entry_time = session_data["entry_time"]
            parking_duration = session_data["duration"]
            parking_fee = calculate_parking_fee(parking_duration)
            vehicle_type = session_data["vehicle_type"]
        
        # Process payment if required
        payment_result = None
        if parking_fee > 0:
            payment_result = await process_payment({
                "card_id": card_id,
                "amount": parking_fee,
                "payment_method": payment_method,
                "currency": "IDR"
            })
            
            if payment_result["status"] != "success":
                return {
                    "status": "payment_failed",
                    "reason": "Payment processing failed",
                    "card_id": card_id,
                    "amount": parking_fee,
                    "payment_result": payment_result,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Capture exit image
        image_path = None
        if config.CAMERA_ENABLED:
            image_path = await camera.capture_image()
        
        # Open gate
        gate_result = await arduino.open_gate(config.GATE_OPEN_DURATION)
        
        # Print receipt if payment was made
        receipt_result = None
        if parking_fee > 0:
            receipt_result = await print_receipt({
                "card_id": card_id,
                "amount": parking_fee,
                "payment_method": payment_method,
                "entry_time": entry_time,
                "exit_time": datetime.now().isoformat()
            })
        
        # Log exit
        exit_log = {
            "card_id": card_id,
            "license_plate": license_plate,
            "vehicle_type": vehicle_type,
            "entry_time": entry_time,
            "exit_time": datetime.now().isoformat(),
            "parking_duration": parking_duration,
            "parking_fee": parking_fee,
            "payment_method": payment_method,
            "payment_result": payment_result,
            "receipt_printed": receipt_result is not None,
            "image_path": image_path,
            "gate": config.GATE_ID,
            "gate_opened": gate_result
        }
        
        logger.info(f"Exit processed: {exit_log}")
        
        # Broadcast exit event
        await broadcast_to_all({
            "type": "exit_event",
            "payload": exit_log
        })
        
        return {
            "status": "approved",
            "card_id": card_id,
            "license_plate": license_plate,
            "vehicle_type": vehicle_type,
            "entry_time": entry_time,
            "exit_time": datetime.now().isoformat(),
            "parking_duration": parking_duration,
            "parking_fee": parking_fee,
            "payment_method": payment_method,
            "payment_result": payment_result,
            "receipt_printed": receipt_result is not None,
            "image_path": image_path,
            "gate": config.GATE_ID,
            "timestamp": datetime.now().isoformat(),
            "message": "Exit approved, gate opened"
        }
        
    except Exception as e:
        logger.error(f"Error processing exit: {e}")
        return {
            "status": "error",
            "reason": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def process_payment(payment_data: dict) -> dict:
    """Process parking payment"""
    try:
        card_id = payment_data["card_id"]
        amount = payment_data["amount"]
        payment_method = payment_data["payment_method"]
        
        logger.info(f"Processing payment: {amount} IDR via {payment_method}")
        
        if config.SIMULATION_MODE:
            # Simulate payment processing
            await asyncio.sleep(1)  # Simulate processing time
            
            # Simulate different payment outcomes
            if amount > 100000:  # Simulate failure for large amounts
                return {
                    "status": "failed",
                    "reason": "Insufficient funds",
                    "amount": amount,
                    "payment_method": payment_method,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "success",
                    "transaction_id": f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "amount": amount,
                    "payment_method": payment_method,
                    "timestamp": datetime.now().isoformat()
                }
        else:
            # Real payment processing would go here
            # Integration with payment gateway, card terminal, etc.
            pass
            
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        return {
            "status": "error",
            "reason": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def print_receipt(receipt_data: dict) -> dict:
    """Print parking receipt"""
    try:
        logger.info(f"Printing receipt for card: {receipt_data['card_id']}")
        
        if config.SIMULATION_MODE:
            # Simulate receipt printing
            await asyncio.sleep(0.5)
            receipt_id = f"RCP_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return {
                "status": "printed",
                "receipt_id": receipt_id,
                "card_id": receipt_data["card_id"],
                "amount": receipt_data["amount"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Real receipt printer integration would go here
            pass
            
    except Exception as e:
        logger.error(f"Receipt printing error: {e}")
        return {
            "status": "error",
            "reason": str(e),
            "timestamp": datetime.now().isoformat()
        }

def calculate_parking_fee(duration_hours: float) -> float:
    """Calculate parking fee based on duration"""
    # Simple fee calculation (can be made more complex)
    base_fee = 5000  # IDR for first hour
    hourly_fee = 3000  # IDR per additional hour
    
    if duration_hours <= 1:
        return base_fee
    else:
        additional_hours = duration_hours - 1
        return base_fee + (additional_hours * hourly_fee)

async def validate_exit_card(card_id: str) -> bool:
    """Validate parking card for exit"""
    # In simulation mode, accept most cards
    if config.SIMULATION_MODE:
        return card_id not in ["BLOCKED_001", "NO_ENTRY_001"]
    
    # Real validation would check database for entry record
    return True

async def get_parking_session(card_id: str) -> dict:
    """Get parking session data"""
    # Simulate parking session data
    return {
        "entry_time": "2025-06-24T08:00:00",
        "duration": 2.5,  # hours
        "vehicle_type": "car"
    }

async def control_gate(action: str, duration: Optional[int] = None) -> dict:
    """Control gate manually"""
    try:
        if duration is None:
            duration = config.GATE_OPEN_DURATION
        
        if action == "open":
            result = await arduino.open_gate(duration)
            logger.info(f"Gate opened manually for {duration} seconds")
        elif action == "close":
            result = await arduino.close_gate()
            logger.info("Gate closed manually")
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }
        
        return {
            "status": "success",
            "action": action,
            "duration": duration if action == "open" else None,
            "gate": config.GATE_ID,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error controlling gate: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# API Endpoints
@app.get("/api/status")
async def get_status():
    """Get controller status"""
    return {
        "gate_id": config.GATE_ID,
        "gate_type": config.GATE_TYPE,
        "gate_name": config.GATE_NAME,
        "location": config.GATE_LOCATION,
        "status": "online",
        "hardware": {
            "camera": {
                "enabled": config.CAMERA_ENABLED,
                "connected": await camera.is_connected() if config.CAMERA_ENABLED else False,
                "source": config.CAMERA_SOURCE
            },
            "card_reader": {
                "enabled": config.CARD_READER_ENABLED,
                "connected": card_reader.is_connected if config.CARD_READER_ENABLED else False,
                "port": config.CARD_READER_PORT
            },
            "arduino": {
                "enabled": config.ARDUINO_ENABLED,
                "connected": arduino.is_connected if config.ARDUINO_ENABLED else False,
                "port": config.ARDUINO_PORT
            }
        },
        "features": {
            "payment_processing": True,
            "receipt_printing": True,
            "fee_calculation": True
        },
        "simulation_mode": config.SIMULATION_MODE,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/parking/exit")
async def parking_exit(request: ParkingExitRequest):
    """Process parking exit"""
    result = await process_parking_exit(request.dict())
    return result

@app.post("/api/payment/process")
async def payment_process(request: PaymentRequest):
    """Process payment"""
    result = await process_payment(request.dict())
    return result

@app.post("/api/receipt/print")
async def receipt_print(request: ReceiptRequest):
    """Print receipt"""
    result = await print_receipt(request.dict())
    return result

@app.post("/api/gate/control")
async def gate_control(request: GateControlRequest):
    """Manual gate control"""
    result = await control_gate(request.action, request.duration)
    return result

@app.post("/api/camera/control")
async def camera_control(request: CameraControlRequest):
    """Camera control"""
    try:
        if request.command == "capture_image":
            if config.CAMERA_ENABLED:
                image_path = await camera.capture_image()
                return {
                    "status": "success",
                    "image_path": image_path,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "disabled",
                    "message": "Camera is disabled"
                }
        
        elif request.command == "start_stream":
            if config.CAMERA_ENABLED:
                await camera.start_stream()
                return {
                    "status": "success",
                    "message": "Camera stream started"
                }
            else:
                return {
                    "status": "disabled",
                    "message": "Camera is disabled"
                }
        
        elif request.command == "stop_stream":
            if config.CAMERA_ENABLED:
                await camera.stop_stream()
                return {
                    "status": "success",
                    "message": "Camera stream stopped"
                }
            else:
                return {
                    "status": "disabled",
                    "message": "Camera is disabled"
                }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown command: {request.command}"
            }
    
    except Exception as e:
        logger.error(f"Camera control error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

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

# Startup and shutdown events now handled by lifespan context manager

if __name__ == "__main__":
    logger.info(f"Starting {config.GATE_NAME} Controller Server...")
    uvicorn.run(
        "main_gate_out:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    ) 