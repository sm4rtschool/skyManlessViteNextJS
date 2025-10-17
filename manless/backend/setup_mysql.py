"""
Setup MySQL Database untuk SkyParking
Script untuk membuat database dan tabel yang diperlukan
"""

import pymysql
import logging
from app.database.database import engine, init_database, test_connection
from app.database.model import Base

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Membuat database skyparking jika belum ada"""
    try:
        # Koneksi ke MySQL server tanpa database
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Buat database jika belum ada
            cursor.execute("CREATE DATABASE IF NOT EXISTS skyparking CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info("Database 'skyparking' berhasil dibuat atau sudah ada")
            
            # Tampilkan database yang ada
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            logger.info("Database yang tersedia:")
            for db in databases:
                logger.info(f"  - {db[0]}")
        
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"Error membuat database: {e}")
        return False

def setup_tables():
    """Membuat tabel-tabel yang diperlukan"""
    try:
        logger.info("Membuat tabel-tabel database...")
        
        # Test koneksi dulu
        if not test_connection():
            logger.error("Koneksi database gagal!")
            return False
        
        # Inisialisasi database dan buat tabel
        init_database()
        logger.info("Tabel-tabel berhasil dibuat!")
        return True
        
    except Exception as e:
        logger.error(f"Error membuat tabel: {e}")
        return False

def check_mysql_connection():
    """Mengecek koneksi MySQL"""
    try:
        # Test koneksi langsung ke MySQL
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            logger.info(f"MySQL Version: {version[0]}")
        
        connection.close()
        logger.info("Koneksi MySQL berhasil!")
        return True
        
    except Exception as e:
        logger.error(f"Koneksi MySQL gagal: {e}")
        logger.error("Pastikan MySQL server berjalan dan konfigurasi sudah benar")
        return False

def main():
    """Main setup function"""
    logger.info("=== Setup Database SkyParking ===")
    
    # 1. Cek koneksi MySQL
    logger.info("1. Mengecek koneksi MySQL...")
    if not check_mysql_connection():
        return
    
    # 2. Buat database
    logger.info("2. Membuat database...")
    if not create_database():
        return
    
    # 3. Buat tabel
    logger.info("3. Membuat tabel...")
    if not setup_tables():
        return
    
    logger.info("=== Setup database selesai! ===")
    logger.info("Database SkyParking siap digunakan!")

if __name__ == "__main__":
    main() 