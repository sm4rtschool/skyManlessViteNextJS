#!/usr/bin/env python3
"""
CONTROLLER APPLICATION - WEBSOCKET CLIENT VERSION
=================================================
Controller yang bertindak sebagai WebSocket client ke backend
Menangani hardware dan mengirim data realtime ke backend
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Import hardware controllers
from hardware.camera import CameraController
from hardware.card_reader import CardReaderController  
from hardware.arduino import ArduinoController
from hardware_detector import hardware_detector
from websocket_client import ControllerWebSocketManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ControllerApplication:
    """Aplikasi controller dengan WebSocket client"""
    
    def __init__(self, gate_id: str = "gate_in"):
        self.gate_id = gate_id
        
        # WebSocket manager
        self.ws_manager = ControllerWebSocketManager(gate_id)
        
        # Hardware controllers
        self.camera_controller = CameraController("0")
        self.card_reader_controller = CardReaderController()
        self.arduino_controller = ArduinoController()
        
        # Status tracking
        self.last_hardware_status = {}
        self.status_update_interval = 5  # seconds
        
        # Flag untuk menghentikan aplikasi
        self.running = False
        
    async def initialize(self):
        """Initialize semua komponen"""
        logger.info(f"🚀 Initializing Controller for {self.gate_id}")
        
        # Initialize hardware controllers
        await self.camera_controller.initialize()
        await self.card_reader_controller.initialize()
        await self.arduino_controller.initialize()
        
        # Setup hardware detector callback
        def hardware_status_callback(status):
            asyncio.create_task(self.send_hardware_status(status))
        
        hardware_detector.set_status_callback(hardware_status_callback)
        hardware_detector.start_detection()
        
        # Register WebSocket message handlers
        self.setup_websocket_handlers()
        
        # Start WebSocket client
        await self.ws_manager.start()
        
        logger.info("✅ Controller initialized successfully")
    
    def setup_websocket_handlers(self):
        """Setup handlers untuk pesan dari backend"""
        
        async def handle_gate_control(payload: Dict[str, Any]):
            """Handle perintah kontrol gate dari backend"""
            action = payload.get("action")
            duration = payload.get("duration", 10)
            
            logger.info(f"Gate control received: {action}")
            
            try:
                if action == "open":
                    result = await self.arduino_controller.open_gate(duration)
                elif action == "close":
                    result = await self.arduino_controller.close_gate()
                else:
                    logger.error(f"Unknown gate action: {action}")
                    return
                
                # Send result back to backend
                await self.ws_manager.send_parking_event("gate_control_result", {
                    "action": action,
                    "success": result.get("success", False),
                    "response": result
                })
                
            except Exception as e:
                logger.error(f"Error controlling gate: {e}")
                await self.ws_manager.client.send_error(f"Gate control error: {str(e)}")
        
        async def handle_camera_control(payload: Dict[str, Any]):
            """Handle perintah kontrol kamera dari backend"""
            command = payload.get("command")
            
            logger.info(f"Camera control received: {command}")
            
            try:
                if command == "capture":
                    frame = await self.camera_controller.capture_image()
                    await self.ws_manager.send_parking_event("image_captured", {
                        "frame": frame,
                        "timestamp": datetime.now().isoformat()
                    })
                elif command == "start_stream":
                    await self.camera_controller.start_stream()
                elif command == "stop_stream":
                    await self.camera_controller.stop_stream()
                
            except Exception as e:
                logger.error(f"Error controlling camera: {e}")
                await self.ws_manager.client.send_error(f"Camera control error: {str(e)}")
        
        async def handle_system_request(payload: Dict[str, Any]):
            """Handle request status sistem"""
            logger.info("System status request received")
            await self.send_system_status()
        
        # Register handlers
        self.ws_manager.register_handler("gate_control", handle_gate_control)
        self.ws_manager.register_handler("camera_control", handle_camera_control)
        self.ws_manager.register_handler("request_status", handle_system_request)
    
    async def send_hardware_status(self, status: Dict[str, Any]):
        """Kirim status hardware ke backend"""
        try:
            # Get additional hardware status
            camera_status = await self.camera_controller.get_status()
            card_reader_status = await self.card_reader_controller.get_status()
            arduino_status = await self.arduino_controller.get_status()
            
            hardware_data = {
                "camera": camera_status,
                "card_reader": card_reader_status,
                "arduino": arduino_status,
                "hardware_detector": status,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.ws_manager.send_hardware_status(hardware_data)
            self.last_hardware_status = hardware_data
            
        except Exception as e:
            logger.error(f"Error sending hardware status: {e}")
    
    async def send_system_status(self):
        """Kirim status sistem lengkap ke backend"""
        try:
            system_data = {
                "gate_id": self.gate_id,
                "controller_status": "running",
                "websocket_connected": self.ws_manager.is_connected(),
                "hardware": self.last_hardware_status,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.ws_manager.send_system_status(system_data)
            
        except Exception as e:
            logger.error(f"Error sending system status: {e}")
    
    async def start_card_reader_monitoring(self):
        """Start monitoring card reader"""
        logger.info("Starting card reader monitoring")
        
        while self.running:
            try:
                # Check for card
                card_data = await self.card_reader_controller.read_card()
                
                if card_data and card_data.get("card_id"):
                    logger.info(f"Card detected: {card_data['card_id']}")
                    
                    # Send card detection to backend
                    await self.ws_manager.client.send_card_detected(
                        card_data["card_id"],
                        card_data
                    )
                    
                    # Trigger parking entry/exit logic based on gate
                    if self.gate_id == "gate_in":
                        await self.handle_parking_entry(card_data)
                    elif self.gate_id == "gate_out":
                        await self.handle_parking_exit(card_data)
                
            except Exception as e:
                logger.error(f"Card reader monitoring error: {e}")
            
            await asyncio.sleep(1)  # Check every second
    
    async def handle_parking_entry(self, card_data: Dict[str, Any]):
        """Handle parking entry"""
        try:
            # Capture image
            frame = await self.camera_controller.capture_image()
            
            # Send parking entry event
            await self.ws_manager.send_parking_event("parking_entry", {
                "card_id": card_data["card_id"],
                "timestamp": datetime.now().isoformat(),
                "image": frame,
                "gate_id": self.gate_id
            })
            
            # Open gate
            await self.arduino_controller.open_gate(10)
            
        except Exception as e:
            logger.error(f"Error handling parking entry: {e}")
            await self.ws_manager.client.send_error(f"Parking entry error: {str(e)}")
    
    async def handle_parking_exit(self, card_data: Dict[str, Any]):
        """Handle parking exit"""
        try:
            # Capture image
            frame = await self.camera_controller.capture_image()
            
            # Send parking exit event
            await self.ws_manager.send_parking_event("parking_exit", {
                "card_id": card_data["card_id"],
                "timestamp": datetime.now().isoformat(),
                "image": frame,
                "gate_id": self.gate_id
            })
            
            # Open gate
            await self.arduino_controller.open_gate(10)
            
        except Exception as e:
            logger.error(f"Error handling parking exit: {e}")
            await self.ws_manager.client.send_error(f"Parking exit error: {str(e)}")
    
    async def periodic_status_update(self):
        """Kirim status update secara berkala"""
        logger.info("Starting periodic status updates")
        
        while self.running:
            try:
                await self.send_system_status()
                await asyncio.sleep(self.status_update_interval)
            except Exception as e:
                logger.error(f"Error in periodic status update: {e}")
                await asyncio.sleep(self.status_update_interval)
    
    async def run(self):
        """Run aplikasi controller"""
        self.running = True
        
        try:
            # Initialize semua komponen
            await self.initialize()
            
            # Start background tasks
            tasks = [
                asyncio.create_task(self.start_card_reader_monitoring()),
                asyncio.create_task(self.periodic_status_update()),
            ]
            
            logger.info(f"✅ Controller {self.gate_id} is running...")
            
            # Wait for all tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Controller error: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown aplikasi"""
        logger.info("🔄 Shutting down controller...")
        
        self.running = False
        
        # Stop hardware detection
        hardware_detector.stop_detection()
        
        # Stop WebSocket client
        await self.ws_manager.stop()
        
        # Cleanup hardware controllers
        await self.camera_controller.cleanup()
        await self.card_reader_controller.cleanup()
        await self.arduino_controller.cleanup()
        
        logger.info("✅ Controller shutdown complete")


async def main():
    """Main function"""
    # Get gate ID from command line or environment
    gate_id = "gate_in"  # default
    
    if len(sys.argv) > 1:
        gate_id = sys.argv[1]
    elif "GATE_ID" in os.environ:
        gate_id = os.environ["GATE_ID"]
    
    logger.info(f"Starting controller for {gate_id}")
    
    # Create and run controller
    controller = ControllerApplication(gate_id)
    await controller.run()


if __name__ == "__main__":
    asyncio.run(main()) 