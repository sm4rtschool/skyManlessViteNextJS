#!/usr/bin/env python3
"""
RTSP to WebRTC Stream Converter
Mengkonversi RTSP stream dari camera Dahua ke WebRTC yang bisa ditampilkan di browser
"""

import asyncio
import cv2
import numpy as np
import av
import fractions
import time
import logging
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRecorder, MediaRelay
from aiortc.contrib.signaling import TcpSocketSignaling, BYE
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Camera configuration
DAHUA_RTSP_URL = "rtsp://admin:SKYUPH@2025@10.5.50.129:554/cam/realmonitor?channel=1&subtype=1"

class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from RTSP to WebRTC
    """
    kind = "video"

    def __init__(self, track):
        super().__init__()
        self.track = track
        self.relay = MediaRelay()

    async def recv(self):
        frame = await self.track.recv()
        return frame

async def offer_handler(offer, pc):
    """Handle WebRTC offer and create answer"""
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return answer

async def run_rtsp_to_webrtc():
    """Main function to run RTSP to WebRTC conversion"""
    
    # Create peer connection
    pc = RTCPeerConnection()
    
    # Create media player from RTSP stream
    try:
        player = MediaPlayer(DAHUA_RTSP_URL)
        logger.info(f"✅ RTSP stream connected: {DAHUA_RTSP_URL}")
        
        # Add video track to peer connection
        if player.video:
            video = VideoTransformTrack(player.video)
            pc.addTrack(video)
            logger.info("✅ Video track added to WebRTC")
        
        # Add audio track if available
        if player.audio:
            pc.addTrack(player.audio)
            logger.info("✅ Audio track added to WebRTC")
            
    except Exception as e:
        logger.error(f"❌ Failed to connect to RTSP stream: {e}")
        return None
    
    return pc

async def create_webrtc_offer():
    """Create WebRTC offer for frontend"""
    pc = await run_rtsp_to_webrtc()
    if not pc:
        return None
    
    # Create offer
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    
    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }

# FastAPI integration
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def get_webrtc_page():
    """HTML page with WebRTC video player"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dahua Camera WebRTC Stream</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                background: #1a1a1a; 
                color: white; 
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
            }
            video { 
                width: 100%; 
                max-width: 640px; 
                border: 2px solid #333; 
                border-radius: 8px; 
            }
            .status { 
                margin: 10px 0; 
                padding: 10px; 
                border-radius: 4px; 
            }
            .connected { background: #2d5a2d; }
            .disconnected { background: #5a2d2d; }
            button { 
                padding: 10px 20px; 
                margin: 5px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
            }
            .start { background: #4CAF50; color: white; }
            .stop { background: #f44336; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📹 Dahua Camera WebRTC Stream</h1>
            <div id="status" class="status disconnected">Status: Disconnected</div>
            <video id="video" autoplay playsinline></video>
            <br>
            <button class="start" onclick="startStream()">Start Stream</button>
            <button class="stop" onclick="stopStream()">Stop Stream</button>
            <div id="info"></div>
        </div>

        <script>
            let pc = null;
            let ws = null;

            async function startStream() {
                try {
                    document.getElementById('status').textContent = 'Status: Connecting...';
                    document.getElementById('status').className = 'status disconnected';
                    
                    // Connect to WebSocket
                    ws = new WebSocket('ws://localhost:8001/ws');
                    
                    ws.onopen = async function() {
                        console.log('WebSocket connected');
                        
                        // Request WebRTC offer
                        ws.send(JSON.stringify({
                            type: 'request_offer'
                        }));
                    };
                    
                    ws.onmessage = async function(event) {
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'offer') {
                            await handleOffer(data);
                        } else if (data.type === 'ice_candidate') {
                            await handleIceCandidate(data);
                        }
                    };
                    
                    ws.onerror = function(error) {
                        console.error('WebSocket error:', error);
                        document.getElementById('status').textContent = 'Status: WebSocket Error';
                        document.getElementById('status').className = 'status disconnected';
                    };
                    
                } catch (error) {
                    console.error('Error starting stream:', error);
                    document.getElementById('status').textContent = 'Status: Error - ' + error.message;
                    document.getElementById('status').className = 'status disconnected';
                }
            }

            async function handleOffer(data) {
                try {
                    // Create RTCPeerConnection
                    pc = new RTCPeerConnection({
                        iceServers: [
                            { urls: 'stun:stun.l.google.com:19302' }
                        ]
                    });
                    
                    // Handle incoming tracks
                    pc.ontrack = function(event) {
                        const video = document.getElementById('video');
                        if (event.streams && event.streams[0]) {
                            video.srcObject = event.streams[0];
                        } else {
                            video.srcObject = new MediaStream([event.track]);
                        }
                    };
                    
                    // Handle ICE candidates
                    pc.onicecandidate = function(event) {
                        if (event.candidate) {
                            ws.send(JSON.stringify({
                                type: 'ice_candidate',
                                candidate: event.candidate
                            }));
                        }
                    };
                    
                    // Set remote description
                    await pc.setRemoteDescription(new RTCSessionDescription(data));
                    
                    // Create answer
                    const answer = await pc.createAnswer();
                    await pc.setLocalDescription(answer);
                    
                    // Send answer back
                    ws.send(JSON.stringify({
                        type: 'answer',
                        sdp: answer.sdp
                    }));
                    
                    document.getElementById('status').textContent = 'Status: Connected';
                    document.getElementById('status').className = 'status connected';
                    
                } catch (error) {
                    console.error('Error handling offer:', error);
                    document.getElementById('status').textContent = 'Status: Error - ' + error.message;
                    document.getElementById('status').className = 'status disconnected';
                }
            }

            async function handleIceCandidate(data) {
                if (pc) {
                    try {
                        await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
                    } catch (error) {
                        console.error('Error adding ICE candidate:', error);
                    }
                }
            }

            function stopStream() {
                if (pc) {
                    pc.close();
                    pc = null;
                }
                if (ws) {
                    ws.close();
                    ws = null;
                }
                document.getElementById('video').srcObject = null;
                document.getElementById('status').textContent = 'Status: Disconnected';
                document.getElementById('status').className = 'status disconnected';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 