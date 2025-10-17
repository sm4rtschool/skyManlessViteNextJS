"""
Arduino Controller untuk Controller Application
Menangani kontrol gate dan hardware melalui Arduino untuk sistem parkir manless
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, List
import serial
import time
import json

logger = logging.getLogger(__name__)

class ArduinoController:
    """Controller untuk menangani Arduino. Koneksi dibuat per-perintah."""
    
    def __init__(self, port: str = "COM8", baudrate: int = 9600):
        # Port default disetel ke COM8, tetapi akan di-override oleh hardware detector
        self.port = port
        self.baudrate = baudrate
        self.gate_status = "closed" # Status default
        self.sensors_data = {}

    async def initialize(self):
        """Inisialisasi 'kosong'. Koneksi tidak dibuat di sini."""
        logger.info("ArduinoController initialized (connection on-demand).")
        # Tidak melakukan apa-apa, koneksi akan dibuat saat dibutuhkan.
        return True

    async def cleanup(self):
        """Cleanup 'kosong'. Tidak ada koneksi persisten untuk ditutup."""
        logger.info("ArduinoController cleanup.")
        # Tidak perlu melakukan apa-apa.

    async def _send_command(self, command: str, target_port: Optional[str] = None, wait_response: bool = True) -> Optional[str]:
        """
        Membuka koneksi, mengirim perintah, mendapatkan respons, dan menutup koneksi.
        Ini adalah satu-satunya tempat di mana koneksi serial ditangani.
        """
        port_to_use = target_port or self.port
        if not port_to_use:
            logger.error("Cannot send command: Arduino port is not specified.")
            return None
        
        logger.debug(f"Executing command '{command}' on port {port_to_use}")

        try:
            with serial.Serial(port_to_use, self.baudrate, timeout=2.0) as ser:
                await asyncio.sleep(1.5)  # Beri waktu untuk Arduino siap
                
                # Kirim perintah
                ser.write(f"{command}\n".encode('utf-8'))
                ser.flush()
                
                if not wait_response:
                    return "OK"
                
                # Baca respons
                response = ser.readline().decode('utf-8').strip()
                logger.debug(f"Response from {port_to_use}: '{response}'")
                return response

        except serial.SerialException as e:
            logger.error(f"Serial error on port {port_to_use} for command '{command}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error on port {port_to_use} for command '{command}': {e}")
            return None

    async def open_gate(self, duration: int = 10, target_port: Optional[str] = None) -> Dict:
        """Membuka gerbang parkir."""
        logger.info(f"Request to open gate on port {target_port or self.port}")
        response = await self._send_command("GATE_OPEN", target_port=target_port)
        
        if response and "OPENED" in response:
            self.gate_status = "open"
            asyncio.create_task(self._auto_close_gate(duration))
            return {"status": "success", "action": "open", "response": response}
        else:
            logger.error(f"Failed to open gate. Response: {response}")
            return {"status": "error", "message": "Failed to open gate", "response": response}

    async def close_gate(self, target_port: Optional[str] = None) -> Dict:
        """Menutup gerbang parkir."""
        logger.info(f"Request to close gate on port {target_port or self.port}")
        response = await self._send_command("GATE_CLOSE", target_port=target_port)
        
        if response and "CLOSED" in response:
            self.gate_status = "closed"
            return {"status": "success", "action": "close", "response": response}
        else:
            logger.error(f"Failed to close gate. Response: {response}")
            return {"status": "error", "message": "Failed to close gate", "response": response}
    
    async def _auto_close_gate(self, delay: int):
        """Automatically close gate after delay"""
        await asyncio.sleep(delay)
        
        if self.gate_status == "open":
            logger.info("Auto-closing gate")
            await self.close_gate()
    
    async def get_gate_status(self) -> Dict:
        """Get current gate status"""
        response = await self._send_command("STATUS")
        
        if response:
            # Parse status response
            # Expected format: "GATE:OPEN,SENSORS:OK"
            parts = response.split(',')
            for part in parts:
                if part.startswith("GATE:"):
                    status = part.split(':')[1].lower()
                    self.gate_status = status
        
        return {
            "status": self.gate_status,
            "timestamp": datetime.now().isoformat()
        }
    
    async def control_led(self, color: str, state: bool = True) -> Dict:
        """Control LED indicators"""
        command = f"LED_{color.upper()}_{'ON' if state else 'OFF'}"
        response = await self._send_command(command)
        
        return {
            "command": command,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    
    async def buzzer(self, duration: float = 0.5) -> Dict:
        """Activate buzzer"""
        command = f"BUZZER_{int(duration * 1000)}"  # Convert to milliseconds
        response = await self._send_command(command)
        
        return {
            "command": command,
            "response": response,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
    
    async def read_sensors(self) -> Dict:
        """Read sensor data from Arduino"""
        response = await self._send_command("SENSORS")
        
        if response:
            try:
                # Parse sensor data
                # Expected format: "TEMP:25.5,HUMIDITY:60.2,MOTION:0"
                sensors = {}
                parts = response.split(',')
                
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':')
                        try:
                            sensors[key.lower()] = float(value)
                        except ValueError:
                            sensors[key.lower()] = value
                
                self.sensors_data = sensors
                
            except Exception as e:
                logger.error(f"Error parsing sensor data: {e}")
        else:
            # Simulation data
            import random
            self.sensors_data = {
                "temperature": round(random.uniform(20, 35), 1),
                "humidity": round(random.uniform(40, 80), 1),
                "motion": random.choice([0, 1]),
                "light": round(random.uniform(0, 100), 1)
            }
        
        return {
            "sensors": self.sensors_data,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_status(self) -> Dict:
        """Get comprehensive Arduino status"""
        gate_status = await self.get_gate_status()
        sensor_data = await self.read_sensors()
        
        return {
            "name": "Arduino Controller",
            "connected": False, # Status ini sekarang kurang relevan
            "port": self.port,
            "baudrate": self.baudrate,
            "gate": gate_status,
            "sensors": sensor_data["sensors"],
            "status": "simulation" if not self.port else "on-demand"
        }
    
    async def emergency_stop(self) -> Dict:
        """Emergency stop - close gate immediately"""
        logger.warning("Emergency stop activated")
        
        response = await self._send_command("EMERGENCY_STOP")
        self.gate_status = "closed"
        
        # Turn on red LED
        await self.control_led("red", True)
        
        # Sound alarm
        await self.buzzer(2.0)
        
        return {
            "status": "emergency_stop_activated",
            "gate_status": "closed",
            "timestamp": datetime.now().isoformat(),
            "response": response
        }
    
    async def reset_system(self) -> Dict:
        """Reset Arduino system"""
        logger.info("Resetting Arduino system")
        
        response = await self._send_command("RESET")
        
        # Wait for reset
        await asyncio.sleep(2)
        
        # Reinitialize
        await self.initialize()
        
        return {
            "status": "system_reset",
            "timestamp": datetime.now().isoformat(),
            "response": response
        }
    
    async def set_gate_auto_close_delay(self, delay: int) -> Dict:
        """Set automatic gate close delay"""
        command = f"SET_AUTO_CLOSE_{delay}"
        response = await self._send_command(command)
        
        return {
            "auto_close_delay": delay,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_device_info(self) -> Dict:
        """Get Arduino device information"""
        response = await self._send_command("INFO")
        
        if response:
            try:
                # Parse device info
                # Expected format: "VERSION:1.0,MODEL:UNO,ID:ABC123"
                info = {}
                parts = response.split(',')
                
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        info[key.lower()] = value
                
                return info
                
            except Exception as e:
                logger.error(f"Error parsing device info: {e}")
        
        # Simulation info
        return {
            "version": "1.0-sim",
            "model": "Arduino UNO (Simulated)",
            "id": "SIM123",
            "firmware": "ParkingGate v1.0"
        }
    
    async def test_all_components(self) -> Dict:
        """Test all connected components"""
        results = {}
        
        # Test gate
        logger.info("Testing gate...")
        gate_test = await self.open_gate(2)
        await asyncio.sleep(3)
        gate_close = await self.close_gate()
        results["gate"] = gate_test["status"] == "success" and gate_close["status"] == "success"
        
        # Test LEDs
        logger.info("Testing LEDs...")
        led_results = []
        for color in ["red", "green", "blue"]:
            led_on = await self.control_led(color, True)
            await asyncio.sleep(0.5)
            led_off = await self.control_led(color, False)
            led_results.append(led_on["response"] and led_off["response"])
        results["leds"] = all(led_results)
        
        # Test buzzer
        logger.info("Testing buzzer...")
        buzzer_test = await self.buzzer(0.2)
        results["buzzer"] = buzzer_test["response"] is not None
        
        # Test sensors
        logger.info("Testing sensors...")
        sensor_test = await self.read_sensors()
        results["sensors"] = bool(sensor_test["sensors"])
        
        overall_status = all(results.values())
        
        return {
            "overall": overall_status,
            "components": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def test_connection(self, target_port: Optional[str] = None) -> bool:
        """Tes koneksi dengan mengirim PING dan menunggu PONG."""
        port_to_test = target_port or self.port
        logger.debug(f"Testing connection on port {port_to_test}...")
        response = await self._send_command("PING", target_port=port_to_test)
        return response == "PONG" 