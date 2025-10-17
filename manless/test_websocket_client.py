#!/usr/bin/env python3
"""
WebSocket Client Test - Manless Parking System
Test WebSocket connection dan message handling
"""

import asyncio
import websockets
import json
from datetime import datetime

class WebSocketTestClient:
    def __init__(self, uri="ws://localhost:8000/ws"):
        self.uri = uri
        self.websocket = None
        self.connected = False
        
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            print(f"🔗 Connecting to {self.uri}...")
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            print("✅ Connected successfully!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def send_message(self, message_type, payload=None):
        """Send message to server"""
        if not self.connected or not self.websocket:
            print("⚠️ Not connected to server")
            return False
            
        message = {
            "type": message_type,
            "payload": payload or {}
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            print(f"📤 Sent: {message_type}")
            return True
        except Exception as e:
            print(f"❌ Send failed: {e}")
            return False
    
    async def listen_for_messages(self, duration=10):
        """Listen for incoming messages"""
        if not self.connected or not self.websocket:
            print("⚠️ Not connected to server")
            return
            
        print(f"👂 Listening for messages for {duration} seconds...")
        
        try:
            end_time = asyncio.get_event_loop().time() + duration
            
            while asyncio.get_event_loop().time() < end_time:
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(), 
                        timeout=1.0
                    )
                    
                    data = json.loads(message)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"📨 [{timestamp}] Received: {data.get('type', 'unknown')} - {data.get('payload', {})}")
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Listen error: {e}")
    
    async def ping_test(self):
        """Test ping/pong"""
        print("🏓 Testing ping/pong...")
        success = await self.send_message("ping", {"timestamp": datetime.now().isoformat()})
        if success:
            # Wait for pong response
            await asyncio.sleep(1)
    
    async def request_system_status(self):
        """Request system status"""
        print("📊 Requesting system status...")
        await self.send_message("request_system_status", {})
    
    async def request_parking_capacity(self):
        """Request parking capacity"""
        print("🅿️ Requesting parking capacity...")
        await self.send_message("request_parking_capacity", {})
    
    async def simulate_card_scan(self, gate="gate_in", card_id="TEST_CARD_001"):
        """Simulate card scan"""
        print(f"💳 Simulating card scan: {card_id} at {gate}")
        await self.send_message("card_scan", {
            "gate": gate,
            "card_id": card_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def close(self):
        """Close connection"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print("🔌 Connection closed")

async def run_comprehensive_test():
    """Run comprehensive WebSocket test"""
    print("=" * 60)
    print("  WEBSOCKET CLIENT TEST - MANLESS PARKING SYSTEM")
    print("=" * 60)
    
    client = WebSocketTestClient()
    
    # Test connection
    if not await client.connect():
        print("❌ Cannot connect to WebSocket server")
        print("Make sure the backend is running: cd manless/backend && python main.py")
        return
    
    # Test basic communication
    await client.ping_test()
    await asyncio.sleep(1)
    
    # Request system information
    await client.request_system_status()
    await asyncio.sleep(1)
    
    await client.request_parking_capacity()
    await asyncio.sleep(1)
    
    # Simulate some events
    await client.simulate_card_scan("gate_in", "CARD_12345")
    await asyncio.sleep(1)
    
    await client.simulate_card_scan("gate_out", "CARD_67890")
    await asyncio.sleep(1)
    
    # Listen for responses
    await client.listen_for_messages(duration=5)
    
    # Close connection
    await client.close()
    
    print("\n✅ WebSocket test completed!")

async def run_simple_connection_test():
    """Simple connection test"""
    print("🔗 Simple WebSocket Connection Test")
    
    try:
        async with websockets.connect("ws://localhost:8000/ws", timeout=5) as websocket:
            print("✅ Connection successful!")
            
            # Send ping
            await websocket.send(json.dumps({"type": "ping", "payload": {}}))
            print("📤 Ping sent")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)
                print(f"📨 Response: {data}")
                print("✅ WebSocket communication working!")
            except asyncio.TimeoutError:
                print("⏰ No response received (timeout)")
                
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "simple":
        asyncio.run(run_simple_connection_test())
    else:
        asyncio.run(run_comprehensive_test()) 