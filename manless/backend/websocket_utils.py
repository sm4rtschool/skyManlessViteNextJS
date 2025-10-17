"""
WebSocket Utilities untuk mengatasi JSON serialization errors
"""

import json
from datetime import datetime, date
from typing import Any, Dict
from fastapi import WebSocket

def safe_json_dumps(data: Any) -> str:
    """Safely serialize data to JSON string, handling datetime objects"""
    def json_serializer(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    return json.dumps(data, default=json_serializer, ensure_ascii=False)

async def safe_websocket_send_json(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Safely send JSON data via WebSocket, handling datetime serialization"""
    try:
        # Convert any datetime objects to ISO format strings
        safe_data = convert_datetime_to_string(data)
        await websocket.send_json(safe_data)
    except Exception as e:
        # Fallback: send as text
        try:
            json_str = safe_json_dumps(data)
            await websocket.send_text(json_str)
        except Exception as fallback_error:
            # Last resort: send error message
            error_msg = {
                "type": "error",
                "message": f"JSON serialization error: {str(e)}",
                "fallback_error": str(fallback_error)
            }
            await websocket.send_json(error_msg)

def convert_datetime_to_string(obj: Any) -> Any:
    """Recursively convert datetime objects to ISO format strings"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_datetime_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime_to_string(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_datetime_to_string(item) for item in obj)
    else:
        return obj

def safe_error_response(message: str, error_type: str = "error") -> Dict[str, Any]:
    """Create a safe error response with timestamp"""
    return {
        "type": error_type,
        "message": message,
        "timestamp": datetime.now().isoformat()
    } 