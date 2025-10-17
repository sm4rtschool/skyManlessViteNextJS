#!/usr/bin/env python3
"""
Check Real-time WebSocket Status - Manless Parking System
"""

import asyncio
import websockets
import json
from datetime import datetime

async def monitor_websocket():
    """Monitor WebSocket connection status"""
    print("🔍 Monitoring WebSocket Connection Status...")
    print("=" * 50)
    
    try:
        # Connect to WebSocket
        async with websockets.connect("ws://localhost:8000/ws", timeout=5) as websocket:
            print(f"✅ Connected at {datetime.now().strftime('%H:%M:%S')}")
            
            # Monitor connection
            connection_count = 0
            message_count = 0
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_count += 1
                    
                    print(f"📨 [{datetime.now().strftime('%H:%M:%S')}] "
                          f"Message #{message_count}: {data.get('type', 'unknown')}")
                    
                    # Show connection status every 10 messages
                    if message_count % 10 == 0:
                        print(f"📊 Status: {message_count} messages received, connection stable")
                    
                    # Break after 20 messages for demo
                    if message_count >= 20:
                        print("\n✅ Connection test completed successfully!")
                        print(f"📊 Total messages received: {message_count}")
                        print("🔗 WebSocket connection is STABLE and WORKING")
                        break
                        
                except json.JSONDecodeError:
                    print(f"⚠️ Received non-JSON message: {message[:100]}...")
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    
    except websockets.exceptions.ConnectionClosed:
        print("❌ WebSocket connection closed unexpectedly")
        return False
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False
    
    return True

async def test_connection_stability():
    """Test multiple quick connections"""
    print("\n🔄 Testing Connection Stability...")
    print("=" * 50)
    
    success_count = 0
    total_tests = 5
    
    for i in range(total_tests):
        try:
            async with websockets.connect("ws://localhost:8000/ws", timeout=3) as websocket:
                # Receive initial message
                initial_msg = await asyncio.wait_for(websocket.recv(), timeout=2)
                data = json.loads(initial_msg)
                
                if data.get('type') == 'system_status':
                    success_count += 1
                    print(f"✅ Test {i+1}/{total_tests}: Connection successful")
                else:
                    print(f"⚠️ Test {i+1}/{total_tests}: Unexpected initial message")
                    
        except Exception as e:
            print(f"❌ Test {i+1}/{total_tests}: Failed - {e}")
            
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    print(f"\n📊 Connection Stability Results:")
    print(f"✅ Successful connections: {success_count}/{total_tests}")
    print(f"📈 Success rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 WebSocket connection is FULLY STABLE!")
    elif success_count >= total_tests * 0.8:
        print("✅ WebSocket connection is mostly stable")
    else:
        print("⚠️ WebSocket connection has stability issues")
    
    return success_count >= total_tests * 0.8

async def main():
    """Run all WebSocket status checks"""
    print("🚀 WEBSOCKET STATUS CHECKER")
    print("=" * 60)
    
    # Test 1: Monitor real-time connection
    monitor_result = await monitor_websocket()
    
    # Test 2: Check connection stability
    stability_result = await test_connection_stability()
    
    print("\n" + "=" * 60)
    print("📋 FINAL RESULTS")
    print("=" * 60)
    print(f"Real-time monitoring:    {'✅ PASS' if monitor_result else '❌ FAIL'}")
    print(f"Connection stability:    {'✅ PASS' if stability_result else '❌ FAIL'}")
    
    overall_status = monitor_result and stability_result
    print(f"Overall WebSocket Status: {'🎉 EXCELLENT' if overall_status else '⚠️ NEEDS ATTENTION'}")
    
    if overall_status:
        print("\n💡 Recommendation: WebSocket is working perfectly!")
        print("   Frontend status should show CONNECTED")
    else:
        print("\n💡 Recommendation: Check backend service and network connection")

if __name__ == "__main__":
    asyncio.run(main()) 