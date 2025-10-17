"""
Backend Hybrid - API Server + WebSocket Server
Sistem Parkir Manless dengan HTTP API dan WebSocket dalam satu aplikasi
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import existing components
from app.api.routes import router as api_router
from app.database.database import engine, get_db
from app.database.model import Base

# Import WebSocket server components
from websocket_server import websocket_manager, WebSocketChannel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Manless Parking System - Hybrid",
    description="HTTP API + WebSocket Server untuk sistem parkir otomatis",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include existing API routes
app.include_router(api_router, prefix="/api/v1")

# ========================================
# HTTP API ENDPOINTS
# ========================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Manless Parking System - Hybrid Server",
        "version": "2.0.0",
        "services": {
            "http_api": "/api/v1",
            "websocket": "/ws",
            "docs": "/api/docs"
        },
        "frontend_routes": {
            "gate_in": "/gate-in (connects to /ws/gate_in)",
            "gate_out": "/gate-out (connects to /ws/gate_out)",
            "admin": "/admin (connects to /ws/gate_all)"
        }
    }

@app.get("/api/system/status")
async def get_system_status():
    """Get comprehensive system status"""
    return {
        "server": "running",
        "timestamp": datetime.now().isoformat(),
        "websocket_channels": {
            name: len(channel.connections) 
            for name, channel in websocket_manager.channels.items()
        },
        "connected_controllers": list(websocket_manager.controller_connections.keys()),
        "controller_data": websocket_manager.controller_data,
        "database": "connected",  # TODO: Add actual DB status check
        "api_endpoints": {
            "parking": "/api/v1/parking",
            "system": "/api/v1/system", 
            "websocket": "/ws"
        }
    }

@app.get("/api/websocket/status")
async def get_websocket_status():
    """Get WebSocket status untuk debugging"""
    return {
        "channels": {
            name: {
                "connections": len(channel.connections),
                "name": channel.name
            }
            for name, channel in websocket_manager.channels.items()
        },
        "controllers": {
            gate_id: {
                "connected": gate_id in websocket_manager.controller_connections,
                "last_data": websocket_manager.controller_data.get(gate_id)
            }
            for gate_id in ["gate_in", "gate_out"]
        }
    }

# ========================================
# WEBSOCKET ENDPOINTS
# ========================================

@app.websocket("/ws/gate_in")
async def websocket_endpoint_gate_in(websocket: WebSocket):
    """WebSocket untuk frontend gate masuk"""
    channel = websocket_manager.get_channel("gate_in")
    await channel.connect(websocket)
    
    try:
        # Send initial status
        if "gate_in" in websocket_manager.controller_data:
            await channel.send_to_websocket(websocket, {
                "type": "system_status",
                "payload": websocket_manager.controller_data["gate_in"]["data"],
                "gate_id": "gate_in"
            })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await websocket_manager.handle_frontend_message("gate_in", websocket, message)
    except WebSocketDisconnect:
        channel.disconnect(websocket)
        logger.info("Frontend gate_in disconnected")
    except Exception as e:
        logger.error(f"Error in gate_in WebSocket: {e}")
        channel.disconnect(websocket)

@app.websocket("/ws/gate_out")
async def websocket_endpoint_gate_out(websocket: WebSocket):
    """WebSocket untuk frontend gate keluar"""
    channel = websocket_manager.get_channel("gate_out")
    await channel.connect(websocket)
    
    try:
        # Send initial status
        if "gate_out" in websocket_manager.controller_data:
            await channel.send_to_websocket(websocket, {
                "type": "system_status",
                "payload": websocket_manager.controller_data["gate_out"]["data"],
                "gate_id": "gate_out"
            })
            
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await websocket_manager.handle_frontend_message("gate_out", websocket, message)
    except WebSocketDisconnect:
        channel.disconnect(websocket)
        logger.info("Frontend gate_out disconnected")
    except Exception as e:
        logger.error(f"Error in gate_out WebSocket: {e}")
        channel.disconnect(websocket)

@app.websocket("/ws/gate_all")
async def websocket_endpoint_gate_all(websocket: WebSocket):
    """WebSocket untuk monitoring semua gate (admin/dashboard)"""
    channel = websocket_manager.get_channel("gate_all")
    await channel.connect(websocket)
    
    try:
        # Send initial status untuk semua gate
        await channel.send_to_websocket(websocket, {
            "type": "all_status",
            "payload": websocket_manager.controller_data
        })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await websocket_manager.handle_frontend_message("gate_all", websocket, message)
    except WebSocketDisconnect:
        channel.disconnect(websocket)
        logger.info("Frontend gate_all disconnected")
    except Exception as e:
        logger.error(f"Error in gate_all WebSocket: {e}")
        channel.disconnect(websocket)

@app.websocket("/ws/admin")
async def websocket_endpoint_admin(websocket: WebSocket):
    """WebSocket untuk admin (alias untuk gate_all)"""
    # Redirect ke gate_all functionality
    channel = websocket_manager.get_channel("gate_all")
    await channel.connect(websocket)
    
    try:
        # Send comprehensive admin status
        await channel.send_to_websocket(websocket, {
            "type": "admin_status",
            "payload": {
                "controllers": websocket_manager.controller_data,
                "system": {
                    "server_time": datetime.now().isoformat(),
                    "active_connections": {
                        name: len(ch.connections) 
                        for name, ch in websocket_manager.channels.items()
                    }
                }
            }
        })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await websocket_manager.handle_frontend_message("admin", websocket, message)
    except WebSocketDisconnect:
        channel.disconnect(websocket)
        logger.info("Admin WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in admin WebSocket: {e}")
        channel.disconnect(websocket)

# ========================================
# CONTROLLER WEBSOCKET ENDPOINTS
# ========================================

@app.websocket("/ws/controller/gate_in")
async def websocket_controller_gate_in(websocket: WebSocket):
    """WebSocket untuk controller gate masuk"""
    await websocket_manager.handle_controller_connection(websocket, "gate_in")

@app.websocket("/ws/controller/gate_out")
async def websocket_controller_gate_out(websocket: WebSocket):
    """WebSocket untuk controller gate keluar"""
    await websocket_manager.handle_controller_connection(websocket, "gate_out")

# ========================================
# STARTUP/SHUTDOWN EVENTS
# ========================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 Starting Manless Parking Hybrid Server...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
    
    # Initialize WebSocket manager
    logger.info("✅ WebSocket channels initialized")
    
    # Start background tasks if needed
    # asyncio.create_task(some_background_task())
    
    logger.info("✅ Hybrid Server started successfully")
    logger.info("   📡 HTTP API: http://localhost:8000/api/v1")
    logger.info("   🔌 WebSocket: ws://localhost:8000/ws")
    logger.info("   📚 Docs: http://localhost:8000/api/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🔄 Shutting down Hybrid Server...")
    
    # Close all WebSocket connections
    for channel in websocket_manager.channels.values():
        for websocket in list(channel.connections):
            try:
                await websocket.close()
            except:
                pass
    
    # Close controller connections
    for websocket in list(websocket_manager.controller_connections.values()):
        try:
            await websocket.close()
        except:
            pass
    
    logger.info("✅ Hybrid Server shutdown complete")

# ========================================
# ADDITIONAL API ENDPOINTS
# ========================================

class GateControlRequest(BaseModel):
    action: str  # "open" or "close"
    duration: Optional[int] = 10

@app.post("/api/v1/gate/{gate_id}/control")
async def control_gate_api(gate_id: str, request: GateControlRequest):
    """HTTP API untuk kontrol gate (alternatif WebSocket)"""
    if gate_id not in ["gate_in", "gate_out"]:
        raise HTTPException(status_code=400, detail="Invalid gate_id")
    
    # Send command via WebSocket to controller
    success = await websocket_manager.send_to_controller(gate_id, {
        "type": "gate_control",
        "payload": {
            "action": request.action,
            "duration": request.duration
        }
    })
    
    return {
        "success": success,
        "gate_id": gate_id,
        "action": request.action,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/gate/{gate_id}/status")
async def get_gate_status(gate_id: str):
    """Get status gate spesifik"""
    if gate_id not in ["gate_in", "gate_out"]:
        raise HTTPException(status_code=400, detail="Invalid gate_id")
    
    if gate_id in websocket_manager.controller_data:
        return {
            "gate_id": gate_id,
            "data": websocket_manager.controller_data[gate_id],
            "connected": gate_id in websocket_manager.controller_connections
        }
    else:
        return {
            "gate_id": gate_id,
            "data": None,
            "connected": False,
            "message": "Controller not connected"
        }

# ========================================
# STATIC FILES (untuk serve frontend jika diperlukan)
# ========================================

# Uncomment jika ingin serve static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main_hybrid:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 