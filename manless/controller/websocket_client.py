"""
WebSocket Client untuk Controller
Mengirim data hardware ke backend WebSocket server
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Optional, Dict, Any

# Setup logging
logger = logging.getLogger(__name__)

class WebSocketClient:
    """WebSocket client untuk controller"""
    
    def __init__(self, gate_id: str, backend_host: str = "localhost", backend_port: int = 8000):
        self.gate_id = gate_id
        self.backend_url = f"ws://{backend_host}:{backend_port}/ws/controller/{gate_id}"
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        self.should_reconnect = True
        self.reconnect_delay = 5
        self.max_reconnect_attempts = 10
        self.reconnect_attempts = 0
        
        # Message queue untuk pesan yang akan dikirim
        self.message_queue = asyncio.Queue()
        
        # Callback untuk menerima pesan dari backend
        self.message_callback = None
        
    async def connect(self):
        """Koneksi ke backend WebSocket server"""
        while self.should_reconnect and self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                logger.info(f"Connecting to backend WebSocket: {self.backend_url}")
                self.websocket = await websockets.connect(self.backend_url)
                self.connected = True
                self.reconnect_attempts = 0
                logger.info(f"✅ Controller {self.gate_id} connected to backend")
                
                # Start message sender dan receiver tasks
                await asyncio.gather(
                    self.message_sender(),
                    self.message_receiver(),
                    return_exceptions=True
                )
                
            except Exception as e:
                logger.error(f"❌ Connection failed: {e}")
                self.connected = False
                self.reconnect_attempts += 1
                
                if self.should_reconnect and self.reconnect_attempts < self.max_reconnect_attempts:
                    logger.info(f"Reconnecting in {self.reconnect_delay} seconds... (attempt {self.reconnect_attempts})")
                    await asyncio.sleep(self.reconnect_delay)
                else:
                    logger.error("Max reconnection attempts reached")
                    break
    
    async def disconnect(self):
        """Disconnect dari backend"""
        self.should_reconnect = False
        self.connected = False
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            
        logger.info(f"Controller {self.gate_id} disconnected from backend")
    
    async def send_message(self, message_type: str, payload: Dict[str, Any]):
        """Kirim pesan ke backend"""
        message = {
            "type": message_type,
            "payload": payload,
            "gate_id": self.gate_id,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.message_queue.put(message)
        logger.debug(f"Queued message: {message_type}")
    
    async def message_sender(self):
        """Task untuk mengirim pesan dari queue"""
        while self.connected:
            try:
                # Ambil pesan dari queue dengan timeout
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                if self.websocket and not self.websocket.closed:
                    await self.websocket.send(json.dumps(message))
                    logger.debug(f"Sent message: {message['type']}")
                
            except asyncio.TimeoutError:
                # Timeout normal, lanjutkan loop
                continue
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                self.connected = False
                break
    
    async def message_receiver(self):
        """Task untuk menerima pesan dari backend"""
        while self.connected:
            try:
                if self.websocket and not self.websocket.closed:
                    message_str = await self.websocket.recv()
                    message = json.loads(message_str)
                    
                    logger.debug(f"Received message: {message.get('type')}")
                    
                    # Panggil callback jika ada
                    if self.message_callback:
                        await self.message_callback(message)
                        
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Backend connection closed")
                self.connected = False
                break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                self.connected = False
                break
    
    def set_message_callback(self, callback):
        """Set callback untuk menangani pesan dari backend"""
        self.message_callback = callback
    
    async def send_hardware_status(self, hardware_data: Dict[str, Any]):
        """Kirim status hardware ke backend"""
        await self.send_message("hardware_status", hardware_data)
    
    async def send_parking_event(self, event_type: str, event_data: Dict[str, Any]):
        """Kirim event parkir ke backend"""
        await self.send_message("parking_event", {
            "event_type": event_type,
            "data": event_data
        })
    
    async def send_system_status(self, status_data: Dict[str, Any]):
        """Kirim status sistem ke backend"""
        await self.send_message("system_status", status_data)
    
    async def send_camera_frame(self, frame_data: str):
        """Kirim frame kamera ke backend"""
        await self.send_message("camera_frame", {
            "frame": frame_data,
            "timestamp": datetime.now().isoformat()
        })
    
    async def send_card_detected(self, card_id: str, additional_data: Dict[str, Any] = None):
        """Kirim event kartu terdeteksi"""
        payload = {
            "card_id": card_id,
            "timestamp": datetime.now().isoformat()
        }
        if additional_data:
            payload.update(additional_data)
            
        await self.send_message("card_detected", payload)
    
    async def send_gate_status(self, status: str, additional_data: Dict[str, Any] = None):
        """Kirim status gate"""
        payload = {
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        if additional_data:
            payload.update(additional_data)
            
        await self.send_message("gate_status", payload)
    
    async def send_error(self, error_message: str, error_data: Dict[str, Any] = None):
        """Kirim error ke backend"""
        payload = {
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }
        if error_data:
            payload.update(error_data)
            
        await self.send_message("error", payload)
    
    def is_connected(self) -> bool:
        """Check apakah terhubung ke backend"""
        return self.connected and self.websocket and not self.websocket.closed


class ControllerWebSocketManager:
    """Manager untuk WebSocket client controller"""
    
    def __init__(self, gate_id: str):
        self.gate_id = gate_id
        self.client = WebSocketClient(gate_id)
        self.running = False
        
        # Set callback untuk menangani pesan dari backend
        self.client.set_message_callback(self.handle_backend_message)
        
        # Storage untuk callback handlers
        self.message_handlers = {}
    
    async def start(self):
        """Start WebSocket client"""
        if self.running:
            logger.warning("WebSocket client already running")
            return
            
        self.running = True
        logger.info(f"Starting WebSocket client for {self.gate_id}")
        
        # Start connection in background task
        asyncio.create_task(self.client.connect())
    
    async def stop(self):
        """Stop WebSocket client"""
        self.running = False
        await self.client.disconnect()
        logger.info(f"WebSocket client for {self.gate_id} stopped")
    
    async def handle_backend_message(self, message: Dict[str, Any]):
        """Handle pesan dari backend"""
        message_type = message.get("type")
        payload = message.get("payload", {})
        
        logger.info(f"Received from backend: {message_type}")
        
        # Panggil handler yang sesuai
        if message_type in self.message_handlers:
            handler = self.message_handlers[message_type]
            try:
                await handler(payload)
            except Exception as e:
                logger.error(f"Error handling message {message_type}: {e}")
        else:
            logger.warning(f"No handler for message type: {message_type}")
    
    def register_handler(self, message_type: str, handler):
        """Register handler untuk message type tertentu"""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for {message_type}")
    
    async def send_hardware_status(self, hardware_data: Dict[str, Any]):
        """Send hardware status ke backend"""
        await self.client.send_hardware_status(hardware_data)
    
    async def send_parking_event(self, event_type: str, event_data: Dict[str, Any]):
        """Send parking event ke backend"""
        await self.client.send_parking_event(event_type, event_data)
    
    async def send_system_status(self, status_data: Dict[str, Any]):
        """Send system status ke backend"""
        await self.client.send_system_status(status_data)
    
    def is_connected(self) -> bool:
        """Check koneksi status"""
        return self.client.is_connected() 