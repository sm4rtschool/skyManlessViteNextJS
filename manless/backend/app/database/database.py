"""
Database Connection dan Session Management
SQLAlchemy setup untuk Manless Parking System
"""

import os
import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

# Database configuration
# Konfigurasi MySQL untuk SkyParking
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/skyparking")

# Fallback ke SQLite jika MySQL tidak tersedia (untuk development)
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./parking_system.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration (fallback)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
else:
    # MySQL configuration untuk SkyParking
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
        connect_args={
            "charset": "utf8mb4",
            "use_unicode": True,
            "autocommit": False
        },
        echo=False  # Set to True untuk SQL debugging
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """
    Database dependency untuk FastAPI
    Yields database session dan ensures proper cleanup
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """
    Initialize database - create tables dan initial data
    """
    try:
        logger.info("Initializing database...")
        
        # Import models to ensure they are registered
        from .model import Base, create_initial_data, SystemConfig
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Check if initial data exists
        db = SessionLocal()
        try:
            existing_config = db.query(SystemConfig).first()
            if not existing_config:
                logger.info("Creating initial system configuration...")
                
                # Add initial configuration data
                initial_configs = create_initial_data()
                for config in initial_configs:
                    db.add(config)
                
                db.commit()
                logger.info("Initial system configuration created")
            else:
                logger.info("System configuration already exists")
                
        except Exception as e:
            logger.error(f"Error creating initial data: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def get_db_info():
    """Get database information untuk debugging"""
    return {
        "url": DATABASE_URL,
        "driver": engine.driver,
        "dialect": engine.dialect.name,
        "pool_size": engine.pool.size() if hasattr(engine.pool, 'size') else None,
        "checked_out": engine.pool.checkedout() if hasattr(engine.pool, 'checkedout') else None
    }

def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

# Database utilities
class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def backup_database(backup_path: str = None):
        """Backup database - supports MySQL and SQLite"""
        try:
            from datetime import datetime
            
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backup_skyparking_{timestamp}.sql"
            
            if DATABASE_URL.startswith("sqlite"):
                # SQLite backup
                import shutil
                db_path = DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
                shutil.copy2(db_path, backup_path.replace('.sql', '.db'))
                logger.info(f"SQLite database backed up to: {backup_path.replace('.sql', '.db')}")
                return True
            elif DATABASE_URL.startswith("mysql"):
                # MySQL backup using mysqldump
                import subprocess
                cmd = [
                    "mysqldump",
                    "--host=localhost",
                    "--port=3306", 
                    "--user=root",
                    "--password=",
                    "--single-transaction",
                    "--routines",
                    "--triggers",
                    "skyparking"
                ]
                
                with open(backup_path, 'w') as f:
                    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                    
                if result.returncode == 0:
                    logger.info(f"MySQL database backed up to: {backup_path}")
                    return True
                else:
                    logger.error(f"MySQL backup failed: {result.stderr}")
                    return False
            else:
                logger.warning("Backup not supported for this database type")
                return False
                
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    @staticmethod
    def restore_database(backup_path: str):
        """Restore database from backup (SQLite only)"""
        if not DATABASE_URL.startswith("sqlite"):
            logger.warning("Restore only supported for SQLite databases")
            return False
            
        try:
            import shutil
            
            # Extract database file path from URL
            db_path = DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
            
            # Close all connections
            engine.dispose()
            
            # Restore backup
            shutil.copy2(backup_path, db_path)
            logger.info(f"Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return False
    
    @staticmethod
    def vacuum_database():
        """Vacuum database untuk optimize storage (SQLite only)"""
        if not DATABASE_URL.startswith("sqlite"):
            logger.warning("Vacuum only supported for SQLite databases")
            return False
            
        try:
            db = SessionLocal()
            db.execute("VACUUM")
            db.close()
            logger.info("Database vacuum completed")
            return True
            
        except Exception as e:
            logger.error(f"Database vacuum failed: {e}")
            return False
    
    @staticmethod
    def get_table_info():
        """Get information about database tables"""
        try:
            from .model import Base
            
            tables_info = []
            for table_name, table in Base.metadata.tables.items():
                column_info = []
                for column in table.columns:
                    column_info.append({
                        "name": column.name,
                        "type": str(column.type),
                        "nullable": column.nullable,
                        "primary_key": column.primary_key,
                        "unique": column.unique
                    })
                
                tables_info.append({
                    "name": table_name,
                    "columns": column_info
                })
            
            return tables_info
            
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return []
    
    @staticmethod
    def cleanup_old_logs(days: int = 90):
        """Cleanup old log entries"""
        try:
            from datetime import datetime, timedelta
            from .model import ParkingLog
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            db = SessionLocal()
            deleted_count = db.query(ParkingLog).filter(
                ParkingLog.timestamp < cutoff_date
            ).delete()
            
            db.commit()
            db.close()
            
            logger.info(f"Cleaned up {deleted_count} old log entries")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")
            return 0

# Initialize database on module import
if __name__ != "__main__":
    try:
        init_database()
    except Exception as e:
        logger.error(f"Failed to initialize database on import: {e}")

# Example usage dan testing
if __name__ == "__main__":
    # Test database functionality
    print("Testing database connection...")
    
    if test_connection():
        print("✓ Database connection successful")
        
        # Initialize database
        init_database()
        print("✓ Database initialized")
        
        # Get database info
        info = get_db_info()
        print(f"✓ Database info: {info}")
        
        # Test session
        db = SessionLocal()
        result = db.execute("SELECT COUNT(*) FROM parking_log").scalar()
        print(f"✓ Parking logs count: {result}")
        db.close()
        
    else:
        print("✗ Database connection failed")