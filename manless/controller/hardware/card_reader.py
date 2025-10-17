"""
Card Reader Controller untuk Controller Application
Menangani pembacaan kartu RFID/NFC untuk sistem parkir manless
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict
import serial
import time

logger = logging.getLogger(__name__)

class CardReaderController:
    """Controller untuk menangani pembacaan kartu"""
    
    def __init__(self, port: str, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        self.last_card_read = None
        self.card_timeout = 5  # seconds
        
    async def initialize(self):
        """Initialize card reader connection"""
        try:
            # Try to connect to serial port
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            
            # Test connection
            if self.serial_connection.is_open:
                self.is_connected = True
                logger.info(f"Card reader connected to {self.port}")
                return True
            else:
                logger.error(f"Failed to open card reader port: {self.port}")
                return False
                
        except serial.SerialException as e:
            logger.error(f"Serial connection error: {e}")
            # Fallback to simulation mode
            self.is_connected = False
            logger.info("Card reader running in simulation mode")
            return True
        except Exception as e:
            logger.error(f"Error initializing card reader: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup card reader resources"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info("Card reader connection closed")
    
    async def read_card(self, timeout: int = 10) -> Optional[Dict]:
        """Read card data with timeout"""
        if self.is_connected and self.serial_connection:
            return await self._read_card_hardware(timeout)
        else:
            return await self._read_card_simulation(timeout)
    
    async def _read_card_hardware(self, timeout: int) -> Optional[Dict]:
        """Read card from actual hardware"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if self.serial_connection.in_waiting > 0:
                    # Read data from card reader
                    data = self.serial_connection.readline().decode('utf-8').strip()
                    
                    if data:
                        # Parse card data (format depends on your card reader)
                        card_data = self._parse_card_data(data)
                        if card_data:
                            self.last_card_read = {
                                **card_data,
                                "timestamp": datetime.now().isoformat(),
                                "read_method": "hardware"
                            }
                            logger.info(f"Card read: {card_data['card_id']}")
                            return self.last_card_read
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
            
            logger.info("Card read timeout")
            return None
            
        except Exception as e:
            logger.error(f"Error reading card from hardware: {e}")
            return None
    
    async def _read_card_simulation(self, timeout: int) -> Optional[Dict]:
        """Simulate card reading for testing"""
        # Wait for a short time to simulate card reading
        await asyncio.sleep(1)
        
        # Simulate different card types
        import random
        card_types = ["employee", "visitor", "monthly", "vip"]
        card_id = f"CARD{random.randint(1000, 9999)}"
        
        card_data = {
            "card_id": card_id,
            "card_type": random.choice(card_types),
            "timestamp": datetime.now().isoformat(),
            "read_method": "simulation"
        }
        
        self.last_card_read = card_data
        logger.info(f"Simulated card read: {card_id}")
        return card_data
    
    def _parse_card_data(self, raw_data: str) -> Optional[Dict]:
        """Parse raw card data from hardware"""
        try:
            # This will depend on your card reader format
            # Example formats:
            # - Simple: "1234567890"
            # - With type: "CARD:1234567890:EMPLOYEE"
            # - JSON: {"id": "1234567890", "type": "employee"}
            
            if raw_data.startswith("CARD:"):
                # Format: CARD:ID:TYPE
                parts = raw_data.split(":")
                if len(parts) >= 2:
                    card_id = parts[1]
                    card_type = parts[2] if len(parts) > 2 else "visitor"
                    
                    return {
                        "card_id": card_id,
                        "card_type": card_type.lower()
                    }
            
            elif raw_data.startswith("{"):
                # JSON format
                import json
                data = json.loads(raw_data)
                return {
                    "card_id": data.get("id", data.get("card_id")),
                    "card_type": data.get("type", data.get("card_type", "visitor"))
                }
            
            else:
                # Simple format - just card ID
                return {
                    "card_id": raw_data,
                    "card_type": "visitor"  # Default type
                }
                
        except Exception as e:
            logger.error(f"Error parsing card data: {e}")
            return None
    
    async def get_status(self) -> Dict:
        """Get card reader status"""
        return {
            "name": "Card Reader",
            "connected": self.is_connected,
            "port": self.port,
            "baudrate": self.baudrate,
            "last_read": self.last_card_read,
            "status": "connected" if self.is_connected else "simulation"
        }
    
    async def test_connection(self) -> bool:
        """Test card reader connection"""
        if not self.is_connected or not self.serial_connection:
            return False
            
        try:
            # Send test command (depends on your card reader)
            self.serial_connection.write(b"TEST\n")
            await asyncio.sleep(0.5)
            
            # Check for response
            if self.serial_connection.in_waiting > 0:
                response = self.serial_connection.readline().decode('utf-8').strip()
                logger.info(f"Card reader test response: {response}")
                return True
            else:
                logger.warning("No response from card reader")
                return False
                
        except Exception as e:
            logger.error(f"Card reader test failed: {e}")
            return False
    
    async def beep(self, duration: float = 0.1):
        """Make card reader beep (if supported)"""
        if self.is_connected and self.serial_connection:
            try:
                # Send beep command (depends on your card reader)
                self.serial_connection.write(b"BEEP\n")
                logger.info("Card reader beep")
            except Exception as e:
                logger.error(f"Card reader beep failed: {e}")
        else:
            logger.info("Simulated card reader beep")
    
    async def set_led(self, color: str, state: bool = True):
        """Control card reader LED (if supported)"""
        if self.is_connected and self.serial_connection:
            try:
                # Send LED command (depends on your card reader)
                command = f"LED:{color.upper()}:{'ON' if state else 'OFF'}\n"
                self.serial_connection.write(command.encode())
                logger.info(f"Card reader LED {color} {'on' if state else 'off'}")
            except Exception as e:
                logger.error(f"Card reader LED control failed: {e}")
        else:
            logger.info(f"Simulated card reader LED {color} {'on' if state else 'off'}")
    
    async def wait_for_card(self, timeout: int = 30) -> Optional[Dict]:
        """Wait for card to be presented"""
        logger.info(f"Waiting for card (timeout: {timeout}s)")
        
        # Visual feedback
        await self.set_led("blue", True)  # Indicate ready to read
        
        try:
            card_data = await self.read_card(timeout)
            
            if card_data:
                # Success feedback
                await self.beep(0.1)
                await self.set_led("green", True)
                await asyncio.sleep(1)
                await self.set_led("green", False)
                
                return card_data
            else:
                # Timeout feedback
                await self.set_led("red", True)
                await asyncio.sleep(0.5)
                await self.set_led("red", False)
                
                return None
                
        finally:
            await self.set_led("blue", False)  # Turn off ready indicator
    
    def get_last_card(self) -> Optional[Dict]:
        """Get last card that was read"""
        return self.last_card_read
    
    async def clear_buffer(self):
        """Clear card reader buffer"""
        if self.is_connected and self.serial_connection:
            try:
                self.serial_connection.reset_input_buffer()
                logger.info("Card reader buffer cleared")
            except Exception as e:
                logger.error(f"Failed to clear card reader buffer: {e}")
    
    async def set_timeout(self, timeout: int):
        """Set card read timeout"""
        self.card_timeout = timeout
        logger.info(f"Card reader timeout set to {timeout}s") 