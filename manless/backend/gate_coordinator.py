#!/usr/bin/env python3
"""
Gate Coordinator - Central Hub untuk Multiple Gate Controllers
Sistem Parkir Manless

Arsitektur:
Frontend ←→ Backend (Central Hub) ←→ Gate Controllers
                                   ├── Gate IN (port 8001)
                                   └── Gate OUT (port 8002)
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, Optional, List
import json

logger = logging.getLogger(__name__)

class GateCoordinator:
    """Coordinator untuk mengelola multiple gate controllers"""
    
    def __init__(self):
        self.gate_controllers = {
            "gate_in": {
                "url": "http://localhost:8001",
                "type": "entry",
                "status": "unknown",
                "last_ping": None
            },
            "gate_out": {
                "url": "http://localhost:8002", 
                "type": "exit",
                "status": "unknown",
                "last_ping": None
            }
        }
        
        self.active_sessions = {}  # Track kendaraan yang sedang parkir
        self.session = None
        
    async def initialize(self):
        """Initialize gate coordinator"""
        self.session = aiohttp.ClientSession()
        
        # Health check semua gate controllers
        await self.health_check_all_gates()
        
        logger.info("Gate Coordinator initialized")
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        logger.info("Gate Coordinator cleaned up")
    
    async def health_check_all_gates(self):
        """Check status semua gate controllers"""
        for gate_id, gate_info in self.gate_controllers.items():
            try:
                status = await self.ping_gate(gate_id)
                self.gate_controllers[gate_id]["status"] = "online" if status else "offline"
                self.gate_controllers[gate_id]["last_ping"] = datetime.now().isoformat()
                
                logger.info(f"Gate {gate_id}: {self.gate_controllers[gate_id]['status']}")
                
            except Exception as e:
                logger.error(f"Health check failed for {gate_id}: {e}")
                self.gate_controllers[gate_id]["status"] = "offline"
    
    async def ping_gate(self, gate_id: str) -> bool:
        """Ping specific gate controller"""
        try:
            gate_url = self.gate_controllers[gate_id]["url"]
            
            async with self.session.get(
                f"{gate_url}/api/status",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.warning(f"Ping failed for {gate_id}: {e}")
            return False
    
    async def send_to_gate(self, gate_id: str, endpoint: str, data: dict) -> dict:
        """Send request to specific gate controller"""
        if gate_id not in self.gate_controllers:
            return {"error": f"Unknown gate: {gate_id}"}
            
        gate_url = self.gate_controllers[gate_id]["url"]
        
        try:
            async with self.session.post(
                f"{gate_url}{endpoint}",
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    self.gate_controllers[gate_id]["status"] = "online"
                    return result
                else:
                    logger.error(f"Gate {gate_id} returned status {response.status}")
                    return {"error": f"Gate {gate_id} error: {response.status}"}
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout sending to gate {gate_id}")
            self.gate_controllers[gate_id]["status"] = "timeout"
            return {"error": f"Gate {gate_id} timeout"}
            
        except Exception as e:
            logger.error(f"Error sending to gate {gate_id}: {e}")
            self.gate_controllers[gate_id]["status"] = "error"
            return {"error": f"Gate {gate_id} error: {str(e)}"}
    
    async def process_parking_entry(self, payload: dict) -> dict:
        """Process parking entry via Gate IN"""
        card_id = payload.get("card_id")
        
        if not card_id:
            return {"error": "Card ID is required"}
        
        # Check if card is already in active session
        if card_id in self.active_sessions:
            return {
                "error": "Card already has active parking session",
                "session": self.active_sessions[card_id]
            }
        
        # Send to Gate IN controller
        result = await self.send_to_gate("gate_in", "/api/parking/entry", payload)
        
        if result.get("status") == "approved":
            # Create active session
            self.active_sessions[card_id] = {
                "card_id": card_id,
                "entry_time": datetime.now().isoformat(),
                "entry_gate": "gate_in",
                "license_plate": payload.get("license_plate"),
                "status": "parked"
            }
            
            logger.info(f"Parking entry approved for {card_id}")
            
            # Add session info to result
            result["session"] = self.active_sessions[card_id]
            result["gate"] = "gate_in"
            
        return result
    
    async def process_parking_exit(self, payload: dict) -> dict:
        """Process parking exit via Gate OUT"""
        card_id = payload.get("card_id")
        
        if not card_id:
            return {"error": "Card ID is required"}
        
        # Check if card has active session
        if card_id not in self.active_sessions:
            return {
                "error": "No active parking session found for this card",
                "card_id": card_id
            }
        
        session = self.active_sessions[card_id]
        
        # Add session info to payload
        payload["session"] = session
        
        # Send to Gate OUT controller
        result = await self.send_to_gate("gate_out", "/api/parking/exit", payload)
        
        if result.get("status") == "approved":
            # Update session with exit info
            session.update({
                "exit_time": datetime.now().isoformat(),
                "exit_gate": "gate_out",
                "payment_amount": result.get("payment_amount", 0),
                "payment_method": payload.get("payment_method", "card"),
                "status": "completed"
            })
            
            # Remove from active sessions
            completed_session = self.active_sessions.pop(card_id)
            
            logger.info(f"Parking exit approved for {card_id}")
            
            # Add session info to result
            result["session"] = completed_session
            result["gate"] = "gate_out"
            
        return result
    
    async def manual_gate_control(self, gate_id: str, action: str, duration: int = 10) -> dict:
        """Manual gate control for specific gate"""
        payload = {
            "action": action,
            "duration": duration
        }
        
        result = await self.send_to_gate(gate_id, "/api/gate/control", payload)
        result["gate"] = gate_id
        
        return result
    
    async def get_camera_stream_url(self, gate_id: str) -> str:
        """Get camera stream URL for specific gate"""
        if gate_id in self.gate_controllers:
            return f"{self.gate_controllers[gate_id]['url']}/api/camera/stream"
        return None
    
    async def capture_image(self, gate_id: str) -> dict:
        """Capture image from specific gate camera"""
        result = await self.send_to_gate(gate_id, "/api/camera/control", {
            "command": "capture_image"
        })
        result["gate"] = gate_id
        
        return result
    
    async def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        status = {
            "coordinator": {
                "status": "online",
                "timestamp": datetime.now().isoformat(),
                "active_sessions": len(self.active_sessions)
            },
            "gates": {},
            "active_sessions": self.active_sessions
        }
        
        # Get status dari semua gate
        for gate_id, gate_info in self.gate_controllers.items():
            try:
                gate_status = await self.send_to_gate(gate_id, "/api/status", {})
                status["gates"][gate_id] = {
                    **gate_info,
                    "controller_status": gate_status
                }
            except Exception as e:
                status["gates"][gate_id] = {
                    **gate_info,
                    "error": str(e)
                }
        
        return status
    
    async def get_parking_capacity(self) -> dict:
        """Get parking capacity info"""
        total_capacity = 100  # Dari config
        occupied = len(self.active_sessions)
        available = total_capacity - occupied
        
        return {
            "total_capacity": total_capacity,
            "occupied": occupied,
            "available": available,
            "occupancy_rate": (occupied / total_capacity) * 100
        }
    
    async def force_exit_session(self, card_id: str, reason: str = "manual") -> dict:
        """Force exit parking session (emergency/manual)"""
        if card_id not in self.active_sessions:
            return {"error": "No active session found"}
        
        session = self.active_sessions.pop(card_id)
        session.update({
            "exit_time": datetime.now().isoformat(),
            "exit_gate": "manual",
            "status": "force_exited",
            "reason": reason
        })
        
        logger.warning(f"Force exit session for {card_id}: {reason}")
        
        return {
            "status": "force_exited",
            "session": session,
            "reason": reason
        }
    
    async def get_gate_logs(self, gate_id: str = None, limit: int = 50) -> list:
        """Get logs from specific gate or all gates"""
        logs = []
        
        if gate_id:
            # Get logs from specific gate
            result = await self.send_to_gate(gate_id, f"/api/logs?limit={limit}", {})
            if "logs" in result:
                for log in result["logs"]:
                    log["gate"] = gate_id
                logs.extend(result["logs"])
        else:
            # Get logs from all gates
            for gid in self.gate_controllers.keys():
                result = await self.send_to_gate(gid, f"/api/logs?limit={limit}", {})
                if "logs" in result:
                    for log in result["logs"]:
                        log["gate"] = gid
                    logs.extend(result["logs"])
        
        # Sort by timestamp
        logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return logs[:limit]

# Global instance
gate_coordinator = GateCoordinator() 