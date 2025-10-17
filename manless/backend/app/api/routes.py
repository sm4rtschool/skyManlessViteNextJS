from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database.database import get_db
from app.database.model import ParkingLog, Vehicle, Card, SystemConfig
from datetime import datetime, timedelta
from typing import List, Dict, Any

router = APIRouter()

@router.get("/health", tags=["System"])
async def health_check():
    """
    Check if the API is running.
    """
    return {"status": "ok", "message": "API is running"}

@router.get("/system/stats", tags=["System"])
async def get_system_stats(db: Session = Depends(get_db)):
    """
    Get parking system statistics
    """
    try:
        # Hitung total kendaraan terdaftar
        total_vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).count()
        
        # Hitung entry hari ini
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_entries = db.query(ParkingLog).filter(
            ParkingLog.timestamp >= today_start,
            ParkingLog.event_type == "ENTRY"
        ).count()
        
        # Hitung occupancy saat ini (simulasi)
        current_occupancy = db.query(ParkingLog).filter(
            ParkingLog.event_type == "ENTRY"
        ).count() - db.query(ParkingLog).filter(
            ParkingLog.event_type == "EXIT"
        ).count()
        
        if current_occupancy < 0:
            current_occupancy = 0
            
        # Ambil kapasitas dari konfigurasi
        capacity_config = db.query(SystemConfig).filter(
            SystemConfig.config_key == "max_parking_capacity"
        ).first()
        capacity = int(capacity_config.config_value) if capacity_config else 100
        
        return {
            "totalVehicles": total_vehicles,
            "todayEntries": today_entries,
            "currentOccupancy": current_occupancy,
            "capacity": capacity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system stats: {str(e)}")

@router.get("/parking/logs", tags=["Parking"])
async def get_parking_logs(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """
    Get parking logs with pagination
    """
    try:
        logs = db.query(ParkingLog).order_by(desc(ParkingLog.timestamp)).offset(offset).limit(limit).all()
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "event_type": log.event_type,
                    "details": log.details,
                    "card_id": log.card_id
                }
                for log in logs
            ],
            "total": db.query(ParkingLog).count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting parking logs: {str(e)}")

@router.post("/parking/log", tags=["Parking"])
async def create_parking_log(event_type: str, details: str = None, card_id: str = None, db: Session = Depends(get_db)):
    """
    Create a new parking log entry
    """
    try:
        log = ParkingLog(
            event_type=event_type,
            details=details,
            card_id=card_id,
            timestamp=datetime.now()
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return {
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "event_type": log.event_type,
            "details": log.details,
            "card_id": log.card_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating parking log: {str(e)}")

@router.get("/system/config", tags=["System"])
async def get_system_config(db: Session = Depends(get_db)):
    """
    Get system configuration
    """
    try:
        configs = db.query(SystemConfig).all()
        return {
            config.config_key: {
                "value": config.config_value,
                "description": config.description,
                "updated_at": config.updated_at.isoformat()
            }
            for config in configs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system config: {str(e)}")

@router.get("/vehicles", tags=["Vehicles"])
async def get_vehicles(active_only: bool = True, db: Session = Depends(get_db)):
    """
    Get registered vehicles
    """
    try:
        query = db.query(Vehicle)
        if active_only:
            query = query.filter(Vehicle.is_active == True)
            
        vehicles = query.all()
        
        return [
            {
                "id": vehicle.id,
                "license_plate": vehicle.license_plate,
                "owner_name": vehicle.owner_name,
                "vehicle_type": vehicle.vehicle_type,
                "card_id": vehicle.card_id,
                "registered_at": vehicle.registered_at.isoformat(),
                "is_active": vehicle.is_active
            }
            for vehicle in vehicles
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting vehicles: {str(e)}")

@router.get("/cards", tags=["Cards"])
async def get_cards(active_only: bool = True, db: Session = Depends(get_db)):
    """
    Get registered cards
    """
    try:
        query = db.query(Card)
        if active_only:
            query = query.filter(Card.is_active == True)
            
        cards = query.all()
        
        return [
            {
                "id": card.id,
                "card_id": card.card_id,
                "card_type": card.card_type,
                "owner_name": card.owner_name,
                "is_active": card.is_active,
                "registered_at": card.registered_at.isoformat(),
                "last_used": card.last_used.isoformat() if card.last_used else None
            }
            for card in cards
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cards: {str(e)}")

# Camera endpoints akan dipindahkan ke main.py untuk menghindari circular import 