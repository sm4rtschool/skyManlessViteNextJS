#!/usr/bin/env python3
"""
Test script untuk camera Dahua
"""

import requests
import cv2
import numpy as np
from urllib.parse import urlparse
import base64

def test_dahua_snapshot():
    """Test HTTP snapshot dari camera Dahua"""
    url = "http://10.5.50.129/cgi-bin/snapshot.cgi"
    username = "admin"
    password = "SKYUPH@2025"
    
    print(f"Testing Dahua camera snapshot...")
    print(f"URL: {url}")
    print(f"Username: {username}")
    
    try:
        # Method 1: Basic auth
        response = requests.get(url, auth=(username, password), timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            print("✅ HTTP snapshot berhasil!")
            
            # Save image untuk test
            with open("test_dahua_snapshot.jpg", "wb") as f:
                f.write(response.content)
            print("✅ Image disimpan sebagai test_dahua_snapshot.jpg")
            
            return True
        else:
            print(f"❌ HTTP snapshot gagal: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing HTTP snapshot: {e}")
        return False

def test_dahua_rtsp():
    """Test RTSP stream dari camera Dahua"""
    rtsp_url = "rtsp://admin:SKYUPH@2025@10.5.50.129:554/cam/realmonitor?channel=1&subtype=1"
    
    print(f"\nTesting Dahua RTSP stream...")
    print(f"RTSP URL: {rtsp_url}")
    
    try:
        cap = cv2.VideoCapture(rtsp_url)
        
        if cap.isOpened():
            print("✅ RTSP connection berhasil!")
            
            # Try to read a frame
            ret, frame = cap.read()
            if ret and frame is not None:
                print("✅ Frame berhasil dibaca!")
                print(f"Frame shape: {frame.shape}")
                
                # Save frame
                cv2.imwrite("test_dahua_frame.jpg", frame)
                print("✅ Frame disimpan sebagai test_dahua_frame.jpg")
                
                cap.release()
                return True
            else:
                print("❌ Gagal membaca frame")
                cap.release()
                return False
        else:
            print("❌ Gagal membuka RTSP stream")
            return False
            
    except Exception as e:
        print(f"❌ Error testing RTSP: {e}")
        return False

def test_alternative_urls():
    """Test alternative URLs untuk camera Dahua"""
    urls = [
        "rtsp://admin:SKYUPH@2025@10.5.50.129:554/cam/realmonitor?channel=1&subtype=0",
        "rtsp://admin:SKYUPH@2025@10.5.50.129:554/live/ch1",
        "rtsp://admin:SKYUPH@2025@10.5.50.129:554/h264/ch1/main/av_stream",
        "http://admin:SKYUPH@2025@10.5.50.129/video.cgi"
    ]
    
    print(f"\nTesting alternative URLs...")
    
    for i, url in enumerate(urls):
        print(f"\nURL {i+1}: {url}")
        
        if url.startswith("rtsp://"):
            try:
                cap = cv2.VideoCapture(url)
                if cap.isOpened():
                    ret, frame = cap.read()
                    cap.release()
                    if ret and frame is not None:
                        print(f"✅ URL {i+1} berhasil!")
                        cv2.imwrite(f"test_alt_{i+1}.jpg", frame)
                        return url
                    else:
                        print(f"❌ URL {i+1} gagal membaca frame")
                else:
                    print(f"❌ URL {i+1} gagal connect")
            except Exception as e:
                print(f"❌ URL {i+1} error: {e}")
        else:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ URL {i+1} berhasil!")
                    return url
                else:
                    print(f"❌ URL {i+1} status: {response.status_code}")
            except Exception as e:
                print(f"❌ URL {i+1} error: {e}")
    
    return None

if __name__ == "__main__":
    print("=== Test Camera Dahua ===")
    
    # Test HTTP snapshot
    snapshot_success = test_dahua_snapshot()
    
    # Test RTSP stream
    rtsp_success = test_dahua_rtsp()
    
    # Test alternative URLs
    best_url = test_alternative_urls()
    
    print(f"\n=== Hasil Test ===")
    print(f"HTTP Snapshot: {'✅' if snapshot_success else '❌'}")
    print(f"RTSP Stream: {'✅' if rtsp_success else '❌'}")
    print(f"Best Alternative URL: {best_url if best_url else '❌ Tidak ada yang berhasil'}")
    
    if snapshot_success or rtsp_success or best_url:
        print("\n✅ Camera Dahua berfungsi!")
    else:
        print("\n❌ Camera Dahua tidak berfungsi!") 