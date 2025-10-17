"""
Card Reader Controller untuk Manless Parking System
Simulasi card reader untuk development dan testing
"""

import asyncio
import logging
import random
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class CardReaderController:
    def __init__(self):
        self.is_connected = False
        self.is_reading = False
        self.last_card_read = None
        self.card_read_history = []
        self.pending_events = []
        
        # Simulated valid cards for testing
        self.valid_cards = {
            "CARD001": {"owner": "John Doe", "type": "RFID", "active": True},
            "CARD002": {"owner": "Jane Smith", "type": "RFID", "active": True},
            "CARD003": {"owner": "Bob Wilson", "type": "Magnetic", "active": True},
            "CARD004": {"owner": "Alice Brown", "type": "RFID", "active": False},
            "CARD005": {"owner": "Charlie Davis", "type": "RFID", "active": True},
        }
        
    async def initialize(self) -> bool:
        """Initialize card reader connection"""
        try:
            logger.info("Initializing card reader...")
            
            # Simulate card reader initialization
            await asyncio.sleep(1)
            
            # In a real implementation, this would connect to actual hardware
            # For now, we'll simulate successful connection
            self.is_connected = True
            
            logger.info("Card reader initialized successfully (simulation mode)")
            
            # Start background card detection simulation
            asyncio.create_task(self._simulate_card_detection())
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing card reader: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup card reader resources"""
        try:
            self.is_connected = False
            self.is_reading = False
            logger.info("Card reader cleanup completed")
        except Exception as e:
            logger.error(f"Error during card reader cleanup: {e}")
    
    def is_connected_status(self) -> bool:
        """Check if card reader is connected"""
        return self.is_connected
    
    async def start_reading(self):
        """Start card reading mode"""
        if not self.is_connected:
            logger.error("Card reader not connected")
            return False
        
        self.is_reading = True
        logger.info("Card reader started reading")
        return True
    
    async def stop_reading(self):
        """Stop card reading mode"""
        self.is_reading = False
        logger.info("Card reader stopped reading")
        return True
    
    async def read_card(self, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """Read a card (blocking with timeout)"""
        if not self.is_connected:
            logger.error("Card reader not connected")
            return None
        
        try:
            logger.info(f"Waiting for card (timeout: {timeout}s)...")
            
            # Simulate card reading delay
            await asyncio.sleep(random.uniform(1, 3))
            
            # Simulate random card detection
            if random.random() < 0.7:  # 70% chance of card detection
                card_id = random.choice(list(self.valid_cards.keys()))
                return await self._process_card(card_id)
            else:
                logger.info("No card detected within timeout")
                return None
                
        except Exception as e:
            logger.error(f"Error reading card: {e}")
            return None
    
    async def validate_card(self, card_id: str) -> Dict[str, Any]:
        """Validate a card ID"""
        try:
            if card_id in self.valid_cards:
                card_info = self.valid_cards[card_id]
                
                if card_info["active"]:
                    result = {
                        "valid": True,
                        "card_id": card_id,
                        "owner": card_info["owner"],
                        "card_type": card_info["type"],
                        "message": "Card valid - Access granted",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Log card access
                    await self._log_card_access(card_id, "ACCESS_GRANTED")
                    
                else:
                    result = {
                        "valid": False,
                        "card_id": card_id,
                        "owner": card_info["owner"],
                        "card_type": card_info["type"],
                        "message": "Card inactive - Access denied",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Log card access attempt
                    await self._log_card_access(card_id, "ACCESS_DENIED_INACTIVE")
            else:
                result = {
                    "valid": False,
                    "card_id": card_id,
                    "owner": "Unknown",
                    "card_type": "Unknown",
                    "message": "Card not registered - Access denied",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Log unknown card attempt
                await self._log_card_access(card_id, "ACCESS_DENIED_UNKNOWN")
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating card: {e}")
            return {
                "valid": False,
                "card_id": card_id,
                "message": f"Validation error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _process_card(self, card_id: str) -> Dict[str, Any]:
        """Process detected card"""
        try:
            self.last_card_read = {
                "card_id": card_id,
                "timestamp": datetime.utcnow(),
                "raw_data": self._generate_raw_card_data(card_id)
            }
            
            # Add to history
            self.card_read_history.append(self.last_card_read.copy())
            
            # Keep only last 100 reads
            if len(self.card_read_history) > 100:
                self.card_read_history = self.card_read_history[-100:]
            
            logger.info(f"Card detected: {card_id}")
            
            # Validate card
            validation_result = await self.validate_card(card_id)
            
            return {
                **validation_result,
                "raw_data": self.last_card_read["raw_data"]
            }
            
        except Exception as e:
            logger.error(f"Error processing card: {e}")
            return None
    
    def _generate_raw_card_data(self, card_id: str) -> str:
        """Generate simulated raw card data"""
        # Simulate raw card data (hexadecimal format)
        hash_object = hashlib.md5(card_id.encode())
        raw_data = hash_object.hexdigest()[:16].upper()
        return raw_data
    
    async def _log_card_access(self, card_id: str, event_type: str):
        """Log card access event"""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "card_id": card_id,
                "details": f"Card {card_id} - {event_type}"
            }
            
            # Add to pending events queue
            self.pending_events.append(log_entry)
            
            logger.info(f"Card access logged: {event_type} for {card_id}")
            
        except Exception as e:
            logger.error(f"Error logging card access: {e}")
    
    async def _simulate_card_detection(self):
        """Background task to simulate random card detection"""
        logger.info("Card detection simulation started")
        
        while self.is_connected:
            try:
                if self.is_reading:
                    # Random card detection (5% chance every second)
                    if random.random() < 0.05:
                        card_id = random.choice(list(self.valid_cards.keys()))
                        logger.info(f"Simulated card detection: {card_id}")
                        
                        # Process the card
                        result = await self._process_card(card_id)
                        
                        # Add to pending events
                        if result:
                            self.pending_events.append({
                                "type": "card_detected",
                                "payload": result
                            })
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in card detection simulation: {e}")
                await asyncio.sleep(5)
        
        logger.info("Card detection simulation stopped")
    
    async def get_pending_events(self) -> List[Dict[str, Any]]:
        """Get and clear pending events"""
        events = self.pending_events.copy()
        self.pending_events.clear()
        return events
    
    async def get_status(self) -> Dict[str, Any]:
        """Get card reader status"""
        return {
            "connected": self.is_connected,
            "reading": self.is_reading,
            "last_card_read": self.last_card_read,
            "cards_read_today": len(self.card_read_history),
            "pending_events": len(self.pending_events),
            "valid_cards_count": len(self.valid_cards),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_card_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get card reading history"""
        return self.card_read_history[-limit:]
    
    async def add_card(self, card_id: str, owner: str, card_type: str = "RFID") -> bool:
        """Add a new valid card"""
        try:
            if card_id in self.valid_cards:
                logger.warning(f"Card {card_id} already exists")
                return False
            
            self.valid_cards[card_id] = {
                "owner": owner,
                "type": card_type,
                "active": True
            }
            
            logger.info(f"Card {card_id} added for {owner}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding card: {e}")
            return False
    
    async def remove_card(self, card_id: str) -> bool:
        """Remove a card (deactivate)"""
        try:
            if card_id not in self.valid_cards:
                logger.warning(f"Card {card_id} not found")
                return False
            
            self.valid_cards[card_id]["active"] = False
            logger.info(f"Card {card_id} deactivated")
            return True
            
        except Exception as e:
            logger.error(f"Error removing card: {e}")
            return False
    
    async def activate_card(self, card_id: str) -> bool:
        """Activate a card"""
        try:
            if card_id not in self.valid_cards:
                logger.warning(f"Card {card_id} not found")
                return False
            
            self.valid_cards[card_id]["active"] = True
            logger.info(f"Card {card_id} activated")
            return True
            
        except Exception as e:
            logger.error(f"Error activating card: {e}")
            return False
    
    async def get_card_info(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific card"""
        if card_id in self.valid_cards:
            return {
                "card_id": card_id,
                **self.valid_cards[card_id]
            }
        return None

# Usage example dan testing
async def test_card_reader():
    """Test card reader functionality"""
    card_reader = CardReaderController()
    
    # Initialize
    if await card_reader.initialize():
        print("Card reader initialized successfully")
        
        # Start reading
        await card_reader.start_reading()
        
        # Test card validation
        for card_id in ["CARD001", "CARD004", "INVALID_CARD"]:
            result = await card_reader.validate_card(card_id)
            print(f"Card {card_id}: {result}")
        
        # Test card reading (simulated)
        card_data = await card_reader.read_card(timeout=5)
        if card_data:
            print(f"Card read: {card_data}")
        
        # Get status
        status = await card_reader.get_status()
        print(f"Card reader status: {status}")
        
        await card_reader.cleanup()
    else:
        print("Failed to initialize card reader")

if __name__ == "__main__":
    asyncio.run(test_card_reader())
