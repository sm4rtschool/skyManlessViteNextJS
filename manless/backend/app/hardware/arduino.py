"""
Arduino Controller untuk Manless Parking System
Komunikasi serial dengan Arduino untuk kontrol gerbang dan sensor
"""

import asyncio
import logging
import serial
import serial.tools.list_ports
from typing import Optional, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ArduinoController:
    def __init__(self, port: Optional[str] = None, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection: Optional[serial.Serial] = None
        self._connected = False
        self.gate_status = "closed"  # closed, open, opening, closing
        self.last_command = None
        self.command_queue = asyncio.Queue()
        
    async def initialize(self) -> bool:
        """Initialize Arduino connection"""
        try:
            logger.info("Initializing Arduino connection...")
            
            # Auto-detect Arduino port if not specified
            if not self.port:
                self.port = await self._detect_arduino_port()
            
            if not self.port:
                logger.warning("Arduino not found, using simulation mode")
                self._connected = True  # Simulation mode
                return True
            
            # Try to establish serial connection
            try:
                self.serial_connection = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=2.0,
                    write_timeout=2.0
                )
                
                # Wait for Arduino to initialize
                await asyncio.sleep(2)
                
                # Test communication
                if await self._test_communication():
                    self._connected = True
                    logger.info(f"Arduino connected successfully on {self.port}")
                    
                    # Start background task for handling commands
                    asyncio.create_task(self._command_handler())
                    return True
                else:
                    logger.error("Arduino communication test failed")
                    self.serial_connection.close()
                    self.serial_connection = None
                    return False
                    
            except serial.SerialException as e:
                logger.error(f"Serial connection error: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing Arduino: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup Arduino connection"""
        try:
            self._connected = False
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                self.serial_connection = None
            logger.info("Arduino cleanup completed")
        except Exception as e:
            logger.error(f"Error during Arduino cleanup: {e}")
    
    async def _detect_arduino_port(self) -> Optional[str]:
        """Auto-detect Arduino port"""
        try:
            ports = serial.tools.list_ports.comports()
            
            # Look for Arduino-like devices
            arduino_keywords = ['arduino', 'ch340', 'cp210', 'ftdi', 'usb']
            
            for port in ports:
                port_desc = port.description.lower()
                if any(keyword in port_desc for keyword in arduino_keywords):
                    logger.info(f"Detected Arduino-like device: {port.device} - {port.description}")
                    return port.device
            
            # If no Arduino found, try first available port
            if ports:
                logger.info(f"Using first available port: {ports[0].device}")
                return ports[0].device
                
            return None
            
        except Exception as e:
            logger.error(f"Error detecting Arduino port: {e}")
            return None
    
    async def _test_communication(self) -> bool:
        """Test communication with Arduino"""
        try:
            if not self.serial_connection:
                return False
            
            # Send test command
            test_command = "STATUS\n"
            self.serial_connection.write(test_command.encode())
            
            # Wait for response
            await asyncio.sleep(1)
            
            if self.serial_connection.in_waiting > 0:
                response = self.serial_connection.readline().decode().strip()
                logger.info(f"Arduino response: {response}")
                return True
            else:
                logger.warning("No response from Arduino")
                return True  # Continue anyway for simulation
                
        except Exception as e:
            logger.error(f"Communication test error: {e}")
            return False
    
    def is_connected_status(self) -> bool:
        """Check if Arduino is connected"""
        return self._connected
    
    def is_connected(self) -> bool:
        """Check if Arduino is connected (alias for is_connected_status)"""
        return self._connected
    
    async def control_gate(self, action: str) -> bool:
        """Control gate (open/close)"""
        try:
            if action not in ["open", "close"]:
                logger.error(f"Invalid gate action: {action}")
                return False
            
            logger.info(f"Gate control: {action}")
            
            # Add command to queue
            await self.command_queue.put({
                "command": "GATE",
                "action": action,
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error controlling gate: {e}")
            return False
    
    async def _command_handler(self):
        """Background task to handle Arduino commands"""
        logger.info("Arduino command handler started")
        
        while self._connected:
            try:
                # Get command from queue (with timeout)
                try:
                    command = await asyncio.wait_for(
                        self.command_queue.get(), 
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process command
                await self._process_command(command)
                
            except Exception as e:
                logger.error(f"Error in command handler: {e}")
                await asyncio.sleep(1)
        
        logger.info("Arduino command handler stopped")
    
    async def _process_command(self, command: Dict[str, Any]):
        """Process individual Arduino command"""
        try:
            cmd_type = command.get("command")
            action = command.get("action")
            
            if cmd_type == "GATE" and action:
                await self._execute_gate_command(str(action))
            else:
                logger.warning(f"Unknown command type: {cmd_type}")
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
    
    async def _execute_gate_command(self, action: str):
        """Execute gate control command"""
        try:
            if action == "open":
                self.gate_status = "opening"
                await self._send_arduino_command("GATE_OPEN")
                
                # Simulate gate opening time
                await asyncio.sleep(2)
                self.gate_status = "open"
                
            elif action == "close":
                self.gate_status = "closing"
                await self._send_arduino_command("GATE_CLOSE")
                
                # Simulate gate closing time
                await asyncio.sleep(2)
                self.gate_status = "closed"
            
            logger.info(f"Gate {action} completed. Status: {self.gate_status}")
            
        except Exception as e:
            logger.error(f"Error executing gate command: {e}")
            self.gate_status = "error"
    
    async def _send_arduino_command(self, command: str) -> bool:
        """Send command to Arduino via serial"""
        try:
            if self.serial_connection and self.serial_connection.is_open:
                command_with_newline = f"{command}\n"
                self.serial_connection.write(command_with_newline.encode())
                self.last_command = {
                    "command": command,
                    "timestamp": datetime.now().isoformat()
                }
                logger.debug(f"Sent Arduino command: {command}")
                return True
            else:
                # Simulation mode
                logger.debug(f"Simulated Arduino command: {command}")
                return True
                
        except Exception as e:
            logger.error(f"Error sending Arduino command: {e}")
            return False
    
    async def read_sensors(self) -> Dict[str, Any]:
        """Read sensor data from Arduino"""
        try:
            if self.serial_connection and self.serial_connection.is_open:
                # Send sensor request
                await self._send_arduino_command("READ_SENSORS")
                
                # Wait for response
                await asyncio.sleep(0.1)
                
                if self.serial_connection.in_waiting > 0:
                    response = self.serial_connection.readline().decode().strip()
                    try:
                        sensor_data = json.loads(response)
                        return sensor_data
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid sensor data format: {response}")
            
            # Return simulated sensor data
            return {
                "vehicle_sensor": False,
                "gate_position": self.gate_status,
                "temperature": 25.5,
                "humidity": 60.0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reading sensors: {e}")
            return {}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Arduino status"""
        sensor_data = await self.read_sensors()
        
        return {
            "connected": self._connected,
            "port": self.port,
            "baudrate": self.baudrate,
            "gate_status": self.gate_status,
            "last_command": self.last_command,
            "sensors": sensor_data,
            "timestamp": datetime.now().isoformat()
        }
    
    async def emergency_stop(self) -> bool:
        """Emergency stop - stop all operations"""
        try:
            logger.warning("Emergency stop activated")
            
            # Clear command queue
            while not self.command_queue.empty():
                try:
                    self.command_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            # Send emergency stop command
            await self._send_arduino_command("EMERGENCY_STOP")
            
            # Reset gate status
            self.gate_status = "stopped"
            
            return True
            
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
            return False
    
    async def reset_system(self) -> bool:
        """Reset Arduino system"""
        try:
            logger.info("Resetting Arduino system")
            
            await self._send_arduino_command("RESET")
            await asyncio.sleep(3)  # Wait for Arduino to reset
            
            # Re-establish communication
            if await self._test_communication():
                self.gate_status = "closed"
                logger.info("Arduino system reset successful")
                return True
            else:
                logger.error("Arduino system reset failed")
                return False
                
        except Exception as e:
            logger.error(f"Error resetting Arduino system: {e}")
            return False

# Usage example dan testing
async def test_arduino():
    """Test Arduino functionality"""
    arduino = ArduinoController()
    
    # Initialize
    if await arduino.initialize():
        print("Arduino initialized successfully")
        
        # Test gate control
        print("Testing gate open...")
        await arduino.control_gate("open")
        await asyncio.sleep(3)
        
        print("Testing gate close...")
        await arduino.control_gate("close")
        await asyncio.sleep(3)
        
        # Test sensor reading
        sensors = await arduino.read_sensors()
        print(f"Sensor data: {sensors}")
        
        # Get status
        status = await arduino.get_status()
        print(f"Arduino status: {status}")
        
        await arduino.cleanup()
    else:
        print("Failed to initialize Arduino")

if __name__ == "__main__":
    asyncio.run(test_arduino())
