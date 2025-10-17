"""
WebSocket Server untuk Manless Parking System
Backend hanya untuk komunikasi data dan relay informasi antara controller dan frontend
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketChannel:
    """Kelas untuk mengelola channel WebSocket berbeda"""
    def __init__(self, name: str):
        self.name = name
        self.connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        """Tambahkan koneksi ke channel"""
        await websocket.accept()
        self.connections.add(websocket)
        logger.info(f"WebSocket connected to channel '{self.name}'. Total: {len(self.connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Hapus koneksi dari channel"""
        self.connections.discard(websocket)
        logger.info(f"WebSocket disconnected from channel '{self.name}'. Total: {len(self.connections)}")
        
    async def broadcast(self, message: dict):
        """Broadcast pesan ke semua koneksi di channel"""
        if not self.connections:
            return
            
        disconnected = []
        message_str = json.dumps(message)
        
        for websocket in self.connections:
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to {self.name}: {e}")
                disconnected.append(websocket)
        
        # Hapus koneksi yang terputus
        for websocket in disconnected:
            self.disconnect(websocket)
            
    async def send_to_websocket(self, websocket: WebSocket, message: dict):
        """Kirim pesan ke WebSocket spesifik"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message to {self.name}: {e}")
            self.disconnect(websocket)

class WebSocketManager:
    """Manager untuk mengelola semua channel WebSocket"""
    
    def __init__(self):
        # Channel untuk berbagai gate
        self.channels: Dict[str, WebSocketChannel] = {
            "gate_in": WebSocketChannel("gate_in"),
            "gate_out": WebSocketChannel("gate_out"), 
            "gate_all": WebSocketChannel("gate_all"),
            "admin": WebSocketChannel("admin")
        }
        
        # Penyimpanan data terbaru dari setiap controller
        self.controller_data: Dict[str, dict] = {}
        
        # Track controller connections
        self.controller_connections: Dict[str, WebSocket] = {}
        
    def get_channel(self, channel_name: str) -> WebSocketChannel:
        """Dapatkan channel berdasarkan nama"""
        return self.channels.get(channel_name)
        
    async def handle_controller_connection(self, websocket: WebSocket, gate_id: str):
        """Handle koneksi dari controller"""
        await websocket.accept()
        self.controller_connections[gate_id] = websocket
        logger.info(f"Controller {gate_id} connected")
        
        try:
            while True:
                data = await websocket.receive_text()
                await self.process_controller_message(gate_id, json.loads(data))
        except WebSocketDisconnect:
            logger.info(f"Controller {gate_id} disconnected")
            self.controller_connections.pop(gate_id, None)
        except Exception as e:
            logger.error(f"Error handling controller {gate_id}: {e}")
            self.controller_connections.pop(gate_id, None)
    
    async def process_controller_message(self, gate_id: str, message: dict):
        """Proses pesan dari controller dan relay ke frontend"""
        message_type = message.get("type")
        payload = message.get("payload", {})
        
        # Simpan data terbaru dari controller
        self.controller_data[gate_id] = {
            "last_update": datetime.now().isoformat(),
            "data": payload
        }
        
        # Tentukan channel mana yang akan menerima pesan
        target_channels = ["gate_all"]  # Semua pesan masuk ke gate_all
        
        if gate_id == "gate_in":
            target_channels.append("gate_in")
        elif gate_id == "gate_out":
            target_channels.append("gate_out")
            
        # Jika pesan penting, kirim juga ke admin
        if message_type in ["emergency", "error", "system_status"]:
            target_channels.append("admin")
        
        # Buat pesan yang akan dikirim ke frontend
        relay_message = {
            "type": message_type,
            "payload": payload,
            "gate_id": gate_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Kirim ke channel yang sesuai
        for channel_name in target_channels:
            channel = self.get_channel(channel_name)
            if channel:
                await channel.broadcast(relay_message)
                
        logger.info(f"Relayed message from {gate_id} to channels: {target_channels}")
    
    async def send_to_controller(self, gate_id: str, message: dict):
        """Kirim pesan ke controller spesifik"""
        if gate_id in self.controller_connections:
            websocket = self.controller_connections[gate_id]
            try:
                await websocket.send_text(json.dumps(message))
                logger.info(f"Sent message to controller {gate_id}")
                return True
            except Exception as e:
                logger.error(f"Error sending to controller {gate_id}: {e}")
                self.controller_connections.pop(gate_id, None)
                return False
        else:
            logger.warning(f"Controller {gate_id} not connected")
            return False
    
    async def handle_frontend_message(self, channel_name: str, websocket: WebSocket, message: dict):
        """Handle pesan dari frontend"""
        message_type = message.get("type")
        payload = message.get("payload", {})
        
        logger.info(f"Frontend message on {channel_name}: {message_type}")
        
        if message_type == "gate_control":
            # Forward gate control ke controller yang sesuai
            gate_id = payload.get("gate_id", channel_name.replace("gate_", "gate_"))
            if gate_id == "gate_gate_in":
                gate_id = "gate_in"
            elif gate_id == "gate_gate_out":
                gate_id = "gate_out"
                
            success = await self.send_to_controller(gate_id, {
                "type": "gate_control",
                "payload": payload
            })
            
            # Kirim response ke frontend
            await self.get_channel(channel_name).send_to_websocket(websocket, {
                "type": "gate_control_response",
                "payload": {
                    "success": success,
                    "gate_id": gate_id,
                    "action": payload.get("action")
                }
            })
            
        elif message_type == "request_status":
            # Kirim status terbaru yang tersimpan
            gate_id = payload.get("gate_id")
            if gate_id and gate_id in self.controller_data:
                await self.get_channel(channel_name).send_to_websocket(websocket, {
                    "type": "system_status",
                    "payload": self.controller_data[gate_id]["data"],
                    "gate_id": gate_id
                })
            else:
                # Kirim status semua controller
                await self.get_channel(channel_name).send_to_websocket(websocket, {
                    "type": "all_status",
                    "payload": self.controller_data
                })

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

# WebSocket endpoints functions
async def websocket_gate_in(websocket: WebSocket):
    """WebSocket endpoint untuk gate_in"""
    channel = websocket_manager.get_channel("gate_in")
    await channel.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await websocket_manager.handle_frontend_message("gate_in", websocket, message)
    except WebSocketDisconnect:
        channel.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error in gate_in WebSocket: {e}")
        channel.disconnect(websocket)

async def websocket_gate_out(websocket: WebSocket):
    """WebSocket endpoint untuk gate_out"""
    channel = websocket_manager.get_channel("gate_out")
    await channel.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await websocket_manager.handle_frontend_message("gate_out", websocket, message)
    except WebSocketDisconnect:
        channel.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error in gate_out WebSocket: {e}")
        channel.disconnect(websocket)

async def websocket_gate_all(websocket: WebSocket):
    """WebSocket endpoint untuk monitoring semua gate"""
    channel = websocket_manager.get_channel("gate_all")
    await channel.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await websocket_manager.handle_frontend_message("gate_all", websocket, message)
    except WebSocketDisconnect:
        channel.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error in gate_all WebSocket: {e}")
        channel.disconnect(websocket)

async def websocket_admin(websocket: WebSocket):
    """WebSocket endpoint untuk admin/monitoring"""
    channel = websocket_manager.get_channel("admin")
    await channel.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await websocket_manager.handle_frontend_message("admin", websocket, message)
    except WebSocketDisconnect:
        channel.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error in admin WebSocket: {e}")
        channel.disconnect(websocket)

async def websocket_controller(websocket: WebSocket, gate_id: str):
    """WebSocket endpoint untuk controller"""
    await websocket_manager.handle_controller_connection(websocket, gate_id) 