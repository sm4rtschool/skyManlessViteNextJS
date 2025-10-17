#!/usr/bin/env python3
"""
Test Ping/Pong WebSocket - Manless Parking System
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_ping_pong():
    """Test ping/pong functionality"""
    print("🏓 Testing WebSocket Ping/Pong...")
    
    try:
        async with websockets.connect("ws://localhost:8000/ws", timeout=5) as websocket:
            print("✅ WebSocket connected!")
            
            # First, receive the initial system_status message
            print("📨 Waiting for initial system_status...")
            initial_response = await asyncio.wait_for(websocket.recv(), timeout=5)
            initial_data = json.loads(initial_response)
            print(f"📨 Initial message: {initial_data.get('type')}")
            
            # Now send ping message
            ping_message = {
                "type": "ping",
                "payload": {
                    "timestamp": datetime.now().isoformat(),
                    "client": "test_client"
                }
            }
            
            await websocket.send(json.dumps(ping_message))
            print(f"📤 Ping sent: {ping_message['type']}")
            
            # Wait for pong response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)
                
                if data.get('type') == 'pong':
                    print(f"📨 Pong received: {data}")
                    
                    # Calculate latency
                    original_time = data.get('payload', {}).get('original_timestamp')
                    if original_time:
                        try:
                            sent_time = datetime.fromisoformat(original_time.replace('Z', '+00:00'))
                            recv_time = datetime.now()
                            latency = (recv_time - sent_time).total_seconds() * 1000
                            print(f"⚡ Latency: {latency:.2f}ms")
                        except:
                            print("⚡ Latency calculation failed")
                    
                    print("✅ Ping/Pong test successful!")
                    return True
                else:
                    print(f"⚠️ Expected pong, got: {data.get('type')}")
                    print(f"Data: {data}")
                    return False
                    
            except asyncio.TimeoutError:
                print("⏰ No pong response received (timeout)")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_multiple_messages():
    """Test multiple ping/pong exchanges"""
    print("\n🔄 Testing multiple ping/pong exchanges...")
    
    try:
        async with websockets.connect("ws://localhost:8000/ws", timeout=5) as websocket:
            # Consume initial message
            await websocket.recv()
            
            success_count = 0
            total_tests = 3
            
            for i in range(total_tests):
                ping_message = {
                    "type": "ping",
                    "payload": {
                        "timestamp": datetime.now().isoformat(),
                        "sequence": i + 1
                    }
                }
                
                await websocket.send(json.dumps(ping_message))
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3)
                    data = json.loads(response)
                    
                    if data.get('type') == 'pong':
                        success_count += 1
                        print(f"✅ Ping {i+1}/{total_tests} successful")
                    else:
                        print(f"❌ Ping {i+1}/{total_tests} failed - got {data.get('type')}")
                        
                except asyncio.TimeoutError:
                    print(f"⏰ Ping {i+1}/{total_tests} timeout")
                    
                await asyncio.sleep(0.5)  # Small delay between pings
            
            print(f"📊 Results: {success_count}/{total_tests} successful")
            return success_count == total_tests
            
    except Exception as e:
        print(f"❌ Multiple ping test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("  WEBSOCKET PING/PONG TEST SUITE")
    print("=" * 60)
    
    # Test 1: Basic ping/pong
    result1 = await test_ping_pong()
    
    # Test 2: Multiple ping/pong
    result2 = await test_multiple_messages()
    
    print("\n" + "=" * 60)
    print("  TEST RESULTS")
    print("=" * 60)
    print(f"Basic Ping/Pong:     {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Multiple Ping/Pong:  {'✅ PASS' if result2 else '❌ FAIL'}")
    print(f"Overall:             {'✅ ALL TESTS PASSED' if result1 and result2 else '❌ SOME TESTS FAILED'}")

if __name__ == "__main__":
    asyncio.run(main()) 