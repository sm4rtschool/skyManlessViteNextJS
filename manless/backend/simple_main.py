"""
Simple FastAPI Backend untuk Testing
Backend sederhana tanpa hardware dependencies
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Manless Parking System API - Simple",
    description="Simple backend untuk testing frontend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
        
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Pydantic models
class SystemStatus(BaseModel):
    camera: bool = True
    arduino: bool = True
    card_reader: bool = True
    gate_status: str = "closed"

class LogEntry(BaseModel):
    id: int
    timestamp: str
    event_type: str
    details: str
    card_id: str = None

# Global data untuk simulasi
system_status = SystemStatus()
logs = []
stats = {
    "total_vehicles": 25,
    "daily_entries": 8,
    "current_occupancy": 12,
    "system_uptime": "2:45:30"
}

@app.get("/")
async def root():
    return {
        "message": "Manless Parking System API - Simple",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system_status": system_status.dict()
    }

@app.get("/api/v1/system/status")
async def get_system_status():
    return system_status.dict()

@app.get("/api/v1/logs")
async def get_logs():
    # Generate sample logs
    sample_logs = [
        {
            "id": i,
            "timestamp": datetime.now().isoformat(),
            "event_type": ["VEHICLE_ENTRY", "VEHICLE_EXIT", "CARD_READ", "GATE_OPEN", "GATE_CLOSE"][i % 5],
            "details": f"Sample log entry {i}",
            "card_id": f"CARD{i:03d}" if i % 2 == 0 else None
        }
        for i in range(1, 21)
    ]
    
    return {
        "logs": sample_logs,
        "total": len(sample_logs)
    }

@app.get("/api/v1/stats/summary")
async def get_stats():
    return stats

@app.post("/api/v1/gate/control")
async def control_gate(request: dict):
    action = request.get("action")
    if action in ["open", "close"]:
        system_status.gate_status = action
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "gate_status",
            "payload": {"status": action, "success": True}
        }))
        
        return {"success": True, "action": action}
    
    return {"success": False, "error": "Invalid action"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "system_status",
            "payload": system_status.dict()
        }))
        
        # Start background tasks
        asyncio.create_task(send_periodic_updates(websocket))
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "request_camera_stream":
                # Simulate camera frame
                await websocket.send_text(json.dumps({
                    "type": "camera_frame",
                    "payload": {
                        "frame": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAAAAAAD...",  # Dummy base64
                        "timestamp": datetime.now().isoformat()
                    }
                }))
            
            elif message.get("type") == "gate_control":
                action = message.get("payload", {}).get("action")
                if action in ["open", "close"]:
                    system_status.gate_status = action
                    await manager.broadcast(json.dumps({
                        "type": "gate_status", 
                        "payload": {"status": action, "success": True}
                    }))
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def send_periodic_updates(websocket: WebSocket):
    """Send periodic updates untuk simulasi real-time data"""
    while websocket in manager.active_connections:
        try:
            # Send random log entry
            log_entry = {
                "id": len(logs) + 1,
                "timestamp": datetime.now().isoformat(),
                "event_type": ["VEHICLE_ENTRY", "CARD_READ", "GATE_OPEN"][len(logs) % 3],
                "details": f"Simulated event {len(logs) + 1}",
                "card_id": f"CARD{(len(logs) % 5) + 1:03d}"
            }
            
            await websocket.send_text(json.dumps({
                "type": "log_entry",
                "payload": log_entry
            }))
            
            # Update stats
            stats["daily_entries"] += 1
            if stats["daily_entries"] % 2 == 0:
                stats["current_occupancy"] += 1
            
            await asyncio.sleep(10)  # Send update every 10 seconds
            
        except:
            break

if __name__ == "__main__":
    import uvicorn
    print("Starting simple backend server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 