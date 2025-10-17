"""
Custom JSON Encoder untuk menangani datetime objects
Mengatasi error "Object of type datetime is not JSON serializable"
"""

import json
from datetime import datetime, date
from typing import Any

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder yang bisa handle datetime objects"""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return super().default(obj)

def json_serialize(data: Any) -> str:
    """Serialize data ke JSON dengan custom encoder"""
    return json.dumps(data, cls=DateTimeEncoder, ensure_ascii=False, indent=2)

def safe_json_response(data: Any) -> Any:
    """Convert data ke format yang safe untuk JSON response"""
    def convert_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: convert_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_datetime(item) for item in obj]
        else:
            return obj
    
    return convert_datetime(data) 