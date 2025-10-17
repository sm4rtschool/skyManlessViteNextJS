"""
Konfigurasi Kamera untuk Manless Parking System
File ini berisi URL kamera yang sudah ditest dan siap digunakan
"""

# Konfigurasi IP Camera Hikvision (backup)
HIKVISION_IP = "192.168.200.64"
HIKVISION_USERNAME = "admin"
HIKVISION_PASSWORD = "R4hasiabanget"

# Konfigurasi IP Camera Dahua untuk Gate IN
DAHUA_IP = "10.5.50.129"
DAHUA_USERNAME = "admin"  # Default Dahua username
DAHUA_PASSWORD = "SKYUPH@2025"  # Dahua password yang sudah dikonfigurasi

# URL RTSP Dahua yang umum digunakan
DAHUA_CAMERA_URLS = {
    # Main stream (resolusi tinggi)
    "rtsp_main": f"rtsp://{DAHUA_USERNAME}:{DAHUA_PASSWORD}@{DAHUA_IP}:554/cam/realmonitor?channel=1&subtype=0",
    
    # Sub stream (resolusi rendah, lebih stabil)
    "rtsp_sub": f"rtsp://{DAHUA_USERNAME}:{DAHUA_PASSWORD}@{DAHUA_IP}:554/cam/realmonitor?channel=1&subtype=1",
    
    # Alternative format 1
    "rtsp_alt1": f"rtsp://{DAHUA_USERNAME}:{DAHUA_PASSWORD}@{DAHUA_IP}:554/live/ch1",
    
    # Alternative format 2
    "rtsp_alt2": f"rtsp://{DAHUA_USERNAME}:{DAHUA_PASSWORD}@{DAHUA_IP}:554/h264/ch1/main/av_stream",
    
    # HTTP Stream
    "http_stream": f"http://{DAHUA_USERNAME}:{DAHUA_PASSWORD}@{DAHUA_IP}/video.cgi",
    
    # HTTP Snapshot
    "http_snapshot": f"http://{DAHUA_USERNAME}:{DAHUA_PASSWORD}@{DAHUA_IP}/cgi-bin/snapshot.cgi"
}

# URL RTSP Hikvision (backup)
HIKVISION_CAMERA_URLS = {
    # Channel Sub (640x360) - Direkomendasikan untuk streaming yang stabil
    "rtsp_sub": f"rtsp://{HIKVISION_USERNAME}:{HIKVISION_PASSWORD}@{HIKVISION_IP}:554/Streaming/Channels/102/",
    
    # Channel Utama (1920x1080) - Resolusi tinggi tapi butuh bandwidth lebih
    "rtsp_main": f"rtsp://{HIKVISION_USERNAME}:{HIKVISION_PASSWORD}@{HIKVISION_IP}:554/Streaming/Channels/101/",
    
    # Format H.264 Alternative (1920x1080)
    "rtsp_h264": f"rtsp://{HIKVISION_USERNAME}:{HIKVISION_PASSWORD}@{HIKVISION_IP}:554/h264/ch1/main/av_stream",
    
    # Format CGI Alternative (1920x1080)
    "rtsp_cgi": f"rtsp://{HIKVISION_USERNAME}:{HIKVISION_PASSWORD}@{HIKVISION_IP}:554/cam/realmonitor?channel=1&subtype=0",
    
    # HTTP Snapshot URL
    "http_snapshot": f"http://{HIKVISION_USERNAME}:{HIKVISION_PASSWORD}@{HIKVISION_IP}/ISAPI/Streaming/channels/101/picture"
}

# Konfigurasi per Gate
GATE_CAMERAS = {
    "gate_in": {
        "primary": DAHUA_CAMERA_URLS["rtsp_sub"],  # Dahua sub stream untuk stabilitas
        "backup": [
            DAHUA_CAMERA_URLS["rtsp_main"],
            DAHUA_CAMERA_URLS["rtsp_alt1"],
            DAHUA_CAMERA_URLS["rtsp_alt2"],
            HIKVISION_CAMERA_URLS["rtsp_sub"]  # Hikvision sebagai fallback
        ],
        "snapshot": DAHUA_CAMERA_URLS["http_snapshot"]
    },
    "gate_out": {
        "primary": HIKVISION_CAMERA_URLS["rtsp_sub"],  # Hikvision untuk gate out
        "backup": [
            HIKVISION_CAMERA_URLS["rtsp_main"],
            HIKVISION_CAMERA_URLS["rtsp_h264"]
        ],
        "snapshot": HIKVISION_CAMERA_URLS["http_snapshot"]
    }
}

# URL Default (Gate IN menggunakan Dahua)
DEFAULT_CAMERA_URL = GATE_CAMERAS["gate_in"]["primary"]

# Backward compatibility
CAMERA_URLS = HIKVISION_CAMERA_URLS

def get_camera_url_for_gate(gate_id, quality="sub"):
    """
    Mendapatkan URL kamera berdasarkan gate dan kualitas
    
    Args:
        gate_id: "gate_in" atau "gate_out"
        quality: "primary" untuk URL utama, "backup" untuk daftar backup
        
    Returns:
        str atau list: URL kamera
    """
    if gate_id not in GATE_CAMERAS:
        return DEFAULT_CAMERA_URL
    
    gate_config = GATE_CAMERAS[gate_id]
    
    if quality == "backup":
        return gate_config.get("backup", [])
    else:
        return gate_config.get("primary", DEFAULT_CAMERA_URL)

def get_snapshot_url_for_gate(gate_id):
    """Mendapatkan URL snapshot untuk gate tertentu"""
    if gate_id not in GATE_CAMERAS:
        return DAHUA_CAMERA_URLS["http_snapshot"]
    
    return GATE_CAMERAS[gate_id].get("snapshot", DAHUA_CAMERA_URLS["http_snapshot"])

def get_camera_url(quality="sub"):
    """
    Mendapatkan URL kamera berdasarkan kualitas yang diinginkan (backward compatibility)
    Default menggunakan gate_in (Dahua)
    """
    return get_camera_url_for_gate("gate_in", "primary")

def get_snapshot_url():
    """Mendapatkan URL untuk HTTP snapshot (backward compatibility)"""
    return get_snapshot_url_for_gate("gate_in")

def get_all_urls():
    """Mendapatkan semua URL yang tersedia"""
    return {
        "dahua": DAHUA_CAMERA_URLS,
        "hikvision": HIKVISION_CAMERA_URLS,
        "gates": GATE_CAMERAS
    }

def test_camera_connection(gate_id="gate_in"):
    """Test koneksi ke kamera menggunakan OpenCV"""
    import cv2
    
    camera_url = get_camera_url_for_gate(gate_id)
    camera_ip = DAHUA_IP if gate_id == "gate_in" else HIKVISION_IP
    
    print(f"Testing connection to {gate_id} camera at {camera_ip}...")
    print(f"URL: {camera_url}")
    
    # Test URL utama
    cap = cv2.VideoCapture(camera_url)
    
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        
        if ret and frame is not None:
            print(f"✅ {gate_id} camera connection successful!")
            return True
        else:
            print(f"❌ {gate_id} camera connected but cannot capture frame")
            return False
    else:
        print(f"❌ Cannot connect to {gate_id} camera")
        
        # Try backup URLs
        backup_urls = get_camera_url_for_gate(gate_id, "backup")
        for i, backup_url in enumerate(backup_urls):
            print(f"Trying backup URL {i+1}: {backup_url}")
            cap = cv2.VideoCapture(backup_url)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret and frame is not None:
                    print(f"✅ {gate_id} camera backup connection successful!")
                    return True
        
        return False

if __name__ == "__main__":
    print("=== Konfigurasi Kamera Manless Parking System ===")
    print()
    print("🚪 Gate IN (Dahua Camera):")
    print(f"IP: {DAHUA_IP}")
    print(f"Username: {DAHUA_USERNAME}")
    print(f"Primary URL: {GATE_CAMERAS['gate_in']['primary']}")
    print()
    print("🚪 Gate OUT (Hikvision Camera):")
    print(f"IP: {HIKVISION_IP}")
    print(f"Username: {HIKVISION_USERNAME}")
    print(f"Primary URL: {GATE_CAMERAS['gate_out']['primary']}")
    print()
    
    # Test koneksi gate in
    print("Testing Gate IN camera...")
    test_camera_connection("gate_in")
    print()
    
    # Test koneksi gate out
    print("Testing Gate OUT camera...")
    test_camera_connection("gate_out") 