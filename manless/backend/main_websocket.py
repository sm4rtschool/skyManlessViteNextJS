"""
Backend WebSocket Server untuk Manless Parking System
Hanya untuk komunikasi data dan relay informasi
"""

import asyncio
import logging
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from websocket_server import (
    websocket_gate_in,
    websocket_gate_out, 
    websocket_gate_all,
    websocket_admin,
    websocket_controller,
    websocket_manager
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Manless Parking WebSocket Server",
    description="WebSocket server untuk komunikasi data sistem parkir",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Manless Parking WebSocket Server",
        "version": "2.0.0",
        "endpoints": {
            "gate_in": "/ws/gate_in",
            "gate_out": "/ws/gate_out", 
            "gate_all": "/ws/gate_all",
            "admin": "/ws/admin",
            "controller_gate_in": "/ws/controller/gate_in",
            "controller_gate_out": "/ws/controller/gate_out"
        }
    }

@app.get("/status")
async def get_status():
    """Status server dan koneksi"""
    return {
        "server": "running",
        "channels": {
            name: len(channel.connections) 
            for name, channel in websocket_manager.channels.items()
        },
        "controllers": list(websocket_manager.controller_connections.keys()),
        "controller_data": websocket_manager.controller_data
    }

# WebSocket endpoints untuk frontend
@app.websocket("/ws/gate_in")
async def websocket_endpoint_gate_in(websocket: WebSocket):
    """WebSocket untuk frontend gate masuk"""
    await websocket_gate_in(websocket)

@app.websocket("/ws/gate_out")
async def websocket_endpoint_gate_out(websocket: WebSocket):
    """WebSocket untuk frontend gate keluar"""
    await websocket_gate_out(websocket)

@app.websocket("/ws/gate_all")
async def websocket_endpoint_gate_all(websocket: WebSocket):
    """WebSocket untuk monitoring semua gate"""
    await websocket_gate_all(websocket)

@app.websocket("/ws/admin")
async def websocket_endpoint_admin(websocket: WebSocket):
    """WebSocket untuk admin/monitoring"""
    await websocket_admin(websocket)

# WebSocket endpoints untuk controller
@app.websocket("/ws/controller/gate_in")
async def websocket_endpoint_controller_gate_in(websocket: WebSocket):
    """WebSocket untuk controller gate masuk"""
    await websocket_controller(websocket, "gate_in")

@app.websocket("/ws/controller/gate_out")
async def websocket_endpoint_controller_gate_out(websocket: WebSocket):
    """WebSocket untuk controller gate keluar"""
    await websocket_controller(websocket, "gate_out")

@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info("🚀 Starting Manless Parking WebSocket Server...")
    logger.info("✅ WebSocket Server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown tasks"""
    logger.info("🔄 Shutting down WebSocket Server...")
    # Tutup semua koneksi
    for channel in websocket_manager.channels.values():
        for websocket in list(channel.connections):
            try:
                await websocket.close()
            except:
                pass
    logger.info("✅ WebSocket Server shutdown complete")

if __name__ == "__main__":
    uvicorn.run(
        "main_websocket:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 