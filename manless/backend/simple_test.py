import requests
import json

def test_controller():
    try:
        print("Testing controller...")
        response = requests.get("http://localhost:8001/api/status")
        print(f"Controller Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Controller Response:")
            print(json.dumps(data, indent=2))
            return data
        else:
            print(f"Controller Error: {response.text}")
            return None
    except Exception as e:
        print(f"Controller Connection Error: {e}")
        return None

def test_backend():
    try:
        print("\nTesting backend...")
        response = requests.get("http://localhost:8000/api/v1/system/status")
        print(f"Backend Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Backend Response:")
            print(json.dumps(data, indent=2))
            return data
        else:
            print(f"Backend Error: {response.text}")
            return None
    except Exception as e:
        print(f"Backend Connection Error: {e}")
        return None

if __name__ == "__main__":
    controller_data = test_controller()
    backend_data = test_backend()
    
    print("\n" + "="*50)
    print("ANALYSIS")
    print("="*50)
    
    if controller_data:
        hardware = controller_data.get("hardware", {})
        arduino = hardware.get("arduino", {})
        print(f"Controller Arduino Status: {arduino.get('connected', 'N/A')}")
    
    if backend_data:
        print(f"Backend Arduino Status: {backend_data.get('arduino', 'N/A')}")
        print(f"Backend Controller Connected: {backend_data.get('controller_connected', 'N/A')}") 