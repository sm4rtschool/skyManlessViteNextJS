#!/usr/bin/env python3
"""
Backend Central Hub - Sistem Parkir Manless
Arsitektur Terpusat untuk Multiple Gate Controllers

Arsitektur:
Frontend ←→ Backend (Central Hub) ←→ Gate Controllers
                                   ├── Gate IN (port 8001)
                                   └── Gate OUT (port 8002)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
from app.database.database import engine, Base, init_database
from app.api.routes import router
import sys
import os
from gate_coordinator import gate_coordinator
import asyncio
import json
from datetime import datetime
import logging
from typing import List, Dict

# Add parent directory to path for gate_coordinator import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Pydantic models untuk API requests
class GateControlRequest(BaseModel):
    action: str
    duration: int = 10

class ParkingRequest(BaseModel):
    card_id: str
    license_plate: str | None = None
    payment_method: str = "card"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Parking System Central Hub",
    description="Central Hub untuk koordinasi multiple gate controllers",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React Create React App
        "http://localhost:5173",  # Vite React App
        "http://127.0.0.1:5173",  # Vite alternative
        "http://127.0.0.1:3000"   # React alternative
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API routes
app.include_router(router)

# Initialize database
init_database()

# WebSocket connections store
active_connections: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint untuk frontend"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info("WebSocket client connected to Central Hub")
    
    # Send welcome message with system status
    try:
        system_status = await gate_coordinator.get_system_status()
        await websocket.send_json({
            "type": "system_status",
            "payload": system_status
        })
    except Exception as e:
        logger.error(f"Error sending initial system status: {e}")
    
    try:
        while True:
            # Listen for messages from frontend
            data = await websocket.receive_text()
            await handle_websocket_message(data, websocket)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected from Central Hub")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

async def handle_websocket_message(message: str, websocket: WebSocket):
    """Handle incoming WebSocket messages dan route ke gate controller yang tepat"""
    try:
        data = json.loads(message)
        message_type = data.get("type")
        payload = data.get("payload", {})
        
        logger.info(f"Received message: {message_type}")
        
        if message_type == "parking_entry":
            # Route to Gate IN controller
            result = await gate_coordinator.process_parking_entry(payload)
            await websocket.send_json({
                "type": "parking_entry_result",
                "payload": result
            })
            
            # Broadcast to all connected clients
            await broadcast_to_all({
                "type": "parking_event",
                "payload": {
                    "event": "entry",
                    "gate": "gate_in",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            })
            
        elif message_type == "parking_exit":
            # Route to Gate OUT controller
            result = await gate_coordinator.process_parking_exit(payload)
            await websocket.send_json({
                "type": "parking_exit_result",
                "payload": result
            })
            
            # Broadcast to all connected clients
            await broadcast_to_all({
                "type": "parking_event",
                "payload": {
                    "event": "exit",
                    "gate": "gate_out",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            })
            
        elif message_type == "gate_control":
            # Manual gate control
            gate_id = payload.get("gate_id", "gate_in")
            action = payload.get("action", "open")
            duration = payload.get("duration", 10)
            
            result = await gate_coordinator.manual_gate_control(gate_id, action, duration)
            await websocket.send_json({
                "type": "gate_control_result",
                "payload": result
            })
            
        elif message_type == "camera_control":
            # Camera control for specific gate
            gate_id = payload.get("gate_id", "gate_in")
            command = payload.get("command")
            
            if command == "capture_image":
                result = await gate_coordinator.capture_image(gate_id)
                await websocket.send_json({
                    "type": "image_captured",
                    "payload": result
                })
            elif command == "get_stream_url":
                stream_url = await gate_coordinator.get_camera_stream_url(gate_id)
                await websocket.send_json({
                    "type": "camera_stream_url",
                    "payload": {
                        "gate_id": gate_id,
                        "stream_url": stream_url
                    }
                })
            
        elif message_type == "request_system_status":
            # Get comprehensive system status
            status = await gate_coordinator.get_system_status()
            await websocket.send_json({
                "type": "system_status",
                "payload": status
            })
            
        elif message_type == "request_parking_capacity":
            # Get parking capacity info
            capacity = await gate_coordinator.get_parking_capacity()
            await websocket.send_json({
                "type": "parking_capacity",
                "payload": capacity
            })
            
        elif message_type == "force_exit_session":
            # Force exit parking session (emergency)
            card_id = payload.get("card_id")
            reason = payload.get("reason", "manual")
            
            result = await gate_coordinator.force_exit_session(card_id, reason)
            await websocket.send_json({
                "type": "force_exit_result",
                "payload": result
            })
            
            # Broadcast emergency exit
            await broadcast_to_all({
                "type": "emergency_event",
                "payload": {
                    "event": "force_exit",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            })
            
        elif message_type == "request_logs":
            # Get logs from gates
            gate_id = payload.get("gate_id")  # None = all gates
            limit = payload.get("limit", 50)
            
            logs = await gate_coordinator.get_gate_logs(gate_id, limit)
            await websocket.send_json({
                "type": "system_logs",
                "payload": {
                    "logs": logs,
                    "gate_id": gate_id,
                    "limit": limit
                }
            })
            
        else:
            logger.warning(f"Unknown message type: {message_type}")
            await websocket.send_json({
                "type": "error",
                "payload": {
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat()
                }
            })
            
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")
        await websocket.send_json({
            "type": "error",
            "payload": {
                "message": f"Error processing message: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        })

async def broadcast_to_all(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    if not active_connections:
        return
    
    disconnected_connections = []
    
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting to connection: {e}")
            disconnected_connections.append(connection)
    
    # Remove disconnected connections
    for connection in disconnected_connections:
        active_connections.remove(connection)

# Central Hub API endpoints
@app.get("/api/status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        status = await gate_coordinator.get_system_status()
        return status
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"System status error: {str(e)}")

@app.get("/api/parking/capacity")
async def get_parking_capacity():
    """Get parking capacity information"""
    try:
        capacity = await gate_coordinator.get_parking_capacity()
        return capacity
    except Exception as e:
        logger.error(f"Error getting parking capacity: {e}")
        raise HTTPException(status_code=500, detail=f"Capacity error: {str(e)}")

@app.post("/api/parking/entry")
async def parking_entry(payload: dict):
    """Process parking entry"""
    try:
        result = await gate_coordinator.process_parking_entry(payload)
        
        # Broadcast event
        await broadcast_to_all({
            "type": "parking_event",
            "payload": {
                "event": "entry",
                "gate": "gate_in",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        return result
    except Exception as e:
        logger.error(f"Error processing parking entry: {e}")
        raise HTTPException(status_code=500, detail=f"Entry error: {str(e)}")

@app.post("/api/parking/exit")
async def parking_exit(payload: dict):
    """Process parking exit"""
    try:
        result = await gate_coordinator.process_parking_exit(payload)
        
        # Broadcast event
        await broadcast_to_all({
            "type": "parking_event",
            "payload": {
                "event": "exit",
                "gate": "gate_out",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        return result
    except Exception as e:
        logger.error(f"Error processing parking exit: {e}")
        raise HTTPException(status_code=500, detail=f"Exit error: {str(e)}")

@app.post("/api/gate/control/{gate_id}")
async def gate_control(gate_id: str, payload: dict):
    """Manual gate control"""
    try:
        action = payload.get("action", "open")
        duration = payload.get("duration", 10)
        
        result = await gate_coordinator.manual_gate_control(gate_id, action, duration)
        return result
    except Exception as e:
        logger.error(f"Error controlling gate {gate_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Gate control error: {str(e)}")

@app.get("/api/camera/stream/{gate_id}")
async def get_camera_stream_url(gate_id: str):
    """Get camera stream URL for specific gate"""
    try:
        stream_url = await gate_coordinator.get_camera_stream_url(gate_id)
        if stream_url is not None:
            return {"stream_url": stream_url, "gate_id": gate_id}
        else:
            raise HTTPException(status_code=404, detail=f"Camera not found for gate {gate_id}")
    except Exception as e:
        logger.error(f"Error getting camera stream for {gate_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Camera error: {str(e)}")

@app.post("/api/camera/capture/{gate_id}")
async def capture_image(gate_id: str):
    """Capture image from specific gate camera"""
    try:
        result = await gate_coordinator.capture_image(gate_id)
        return result
    except Exception as e:
        logger.error(f"Error capturing image from {gate_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Capture error: {str(e)}")

@app.get("/api/logs")
async def get_logs(gate_id: str = None, limit: int = 50):
    """Get system logs"""
    try:
        logs = await gate_coordinator.get_gate_logs(gate_id, limit)
        return {"logs": logs, "gate_id": gate_id, "limit": limit}
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=f"Logs error: {str(e)}")

@app.post("/api/emergency/force-exit")
async def force_exit_session(payload: dict):
    """Force exit parking session (emergency)"""
    try:
        card_id = payload.get("card_id")
        reason = payload.get("reason", "emergency")
        
        if not card_id:
            raise HTTPException(status_code=400, detail="Card ID is required")
        
        result = await gate_coordinator.force_exit_session(card_id, reason)
        
        # Broadcast emergency event
        await broadcast_to_all({
            "type": "emergency_event",
            "payload": {
                "event": "force_exit",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        return result
    except Exception as e:
        logger.error(f"Error force exit session: {e}")
        raise HTTPException(status_code=500, detail=f"Force exit error: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize gate coordinator on startup"""
    logger.info("Starting Parking System Central Hub...")
    
    try:
        await gate_coordinator.initialize()
        logger.info("Gate Coordinator initialized successfully")
        logger.info("Central Hub ready to coordinate gate controllers")
        
    except Exception as e:
        logger.error(f"Failed to initialize Gate Coordinator: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Central Hub...")
    
    try:
        await gate_coordinator.cleanup()
        logger.info("Gate Coordinator cleaned up successfully")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    logger.info("Starting Central Hub Server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
