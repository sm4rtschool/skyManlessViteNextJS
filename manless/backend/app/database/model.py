"""
Database Models untuk Manless Parking System
SQLAlchemy models untuk parking_log, vehicles, cards, dan system_config
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class ParkingLog(Base):
    """Model untuk parking log - mencatat semua event sistem"""
    __tablename__ = "parking_log"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    details = Column(Text, nullable=True)
    card_id = Column(String(100), nullable=True, index=True)

class Vehicle(Base):
    """Model untuk data kendaraan terdaftar"""
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    license_plate = Column(String(20), unique=True, nullable=False, index=True)
    owner_name = Column(String(100), nullable=False)
    vehicle_type = Column(String(50), nullable=False)  # car, motorcycle, truck, etc.
    card_id = Column(String(100), nullable=True, index=True)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

class Card(Base):
    """Model untuk data kartu akses"""
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    card_id = Column(String(100), unique=True, nullable=False, index=True)
    card_type = Column(String(50), nullable=False)  # RFID, magnetic, etc.
    owner_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used = Column(DateTime, nullable=True)

class SystemConfig(Base):
    """Model untuk konfigurasi sistem"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# Additional models untuk future features

class ParkingSlot(Base):
    """Model untuk slot parkir (future feature)"""
    __tablename__ = "parking_slots"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slot_number = Column(String(10), unique=True, nullable=False, index=True)
    slot_type = Column(String(20), nullable=False)  # car, motorcycle, disabled
    is_occupied = Column(Boolean, default=False, nullable=False)
    current_vehicle_id = Column(Integer, nullable=True)
    occupied_since = Column(DateTime, nullable=True)

class Payment(Base):
    """Model untuk pembayaran parkir (future feature)"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vehicle_id = Column(Integer, nullable=False, index=True)
    card_id = Column(String(100), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # cash, card, digital
    payment_status = Column(String(20), default="pending", nullable=False)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=True)
    duration_hours = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class SystemAlert(Base):
    """Model untuk alert sistem (future feature)"""
    __tablename__ = "system_alerts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

# Helper function untuk initial data
def create_initial_data():
    """Create initial system configuration data"""
    return [
        SystemConfig(
            config_key="gate_auto_close_delay",
            config_value="5",
            description="Auto close gate delay in seconds"
        ),
        SystemConfig(
            config_key="camera_resolution",
            config_value="1920x1080",
            description="Camera resolution setting"
        ),
        SystemConfig(
            config_key="parking_rate_per_hour",
            config_value="2000",
            description="Parking rate per hour in IDR"
        ),
        SystemConfig(
            config_key="max_parking_capacity",
            config_value="100",
            description="Maximum parking capacity"
        ),
        SystemConfig(
            config_key="card_reader_timeout",
            config_value="10",
            description="Card reader timeout in seconds"
        ),
        SystemConfig(
            config_key="system_timezone",
            config_value="Asia/Jakarta",
            description="System timezone"
        ),
        SystemConfig(
            config_key="backup_enabled",
            config_value="true",
            description="Enable automatic database backup"
        ),
        SystemConfig(
            config_key="notification_email",
            config_value="admin@manlessparking.com",
            description="System notification email"
        ),
        SystemConfig(
            config_key="gate_open_duration",
            config_value="10",
            description="Gate open duration in seconds"
        ),
        SystemConfig(
            config_key="log_retention_days",
            config_value="90",
            description="Log retention period in days"
        )
    ]
