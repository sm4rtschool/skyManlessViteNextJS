#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk setup database SkyParking
Membuat database dan semua tabel yang diperlukan
"""

import pymysql
import sys
import os

# Set console encoding untuk Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Konfigurasi database
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "skyparking"

def create_database():
    """Buat database skyparking"""
    print("🔧 Menghubungkan ke MySQL server...")
    
    try:
        # Koneksi ke MySQL server (tanpa database)
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ Berhasil terhubung ke MySQL server")
        
        with connection.cursor() as cursor:
            # Buat database
            print(f"🔧 Membuat database '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Database '{DB_NAME}' berhasil dibuat")
            
        connection.close()
        return True
        
    except pymysql.err.OperationalError as e:
        print(f"❌ Error koneksi ke MySQL: {e}")
        print("\n💡 Pastikan:")
        print("   1. MySQL server sudah berjalan")
        print("   2. Username dan password benar")
        print("   3. Port 3306 tidak diblokir")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_tables():
    """Buat semua tabel yang diperlukan"""
    print(f"\n🔧 Membuat tabel di database '{DB_NAME}'...")
    
    try:
        # Koneksi ke database skyparking
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Tabel parking_log
            print("   📋 Membuat tabel 'parking_log'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `parking_log` (
                  `id` INT NOT NULL AUTO_INCREMENT,
                  `timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  `event_type` VARCHAR(50) NOT NULL,
                  `details` TEXT NULL,
                  `card_id` VARCHAR(100) NULL,
                  PRIMARY KEY (`id`),
                  INDEX `idx_timestamp` (`timestamp`),
                  INDEX `idx_event_type` (`event_type`),
                  INDEX `idx_card_id` (`card_id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabel vehicles
            print("   🚗 Membuat tabel 'vehicles'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `vehicles` (
                  `id` INT NOT NULL AUTO_INCREMENT,
                  `license_plate` VARCHAR(20) NOT NULL,
                  `owner_name` VARCHAR(100) NOT NULL,
                  `vehicle_type` VARCHAR(50) NOT NULL,
                  `card_id` VARCHAR(100) NULL,
                  `registered_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
                  PRIMARY KEY (`id`),
                  UNIQUE INDEX `idx_license_plate` (`license_plate`),
                  INDEX `idx_card_id` (`card_id`),
                  INDEX `idx_is_active` (`is_active`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabel cards
            print("   💳 Membuat tabel 'cards'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `cards` (
                  `id` INT NOT NULL AUTO_INCREMENT,
                  `card_id` VARCHAR(100) NOT NULL,
                  `card_type` VARCHAR(50) NOT NULL,
                  `owner_name` VARCHAR(100) NOT NULL,
                  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
                  `registered_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  `last_used` DATETIME NULL,
                  PRIMARY KEY (`id`),
                  UNIQUE INDEX `idx_card_id` (`card_id`),
                  INDEX `idx_is_active` (`is_active`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabel system_config
            print("   ⚙️  Membuat tabel 'system_config'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `system_config` (
                  `id` INT NOT NULL AUTO_INCREMENT,
                  `config_key` VARCHAR(100) NOT NULL,
                  `config_value` TEXT NOT NULL,
                  `description` TEXT NULL,
                  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                  PRIMARY KEY (`id`),
                  UNIQUE INDEX `idx_config_key` (`config_key`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabel parking_slots
            print("   🅿️  Membuat tabel 'parking_slots'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `parking_slots` (
                  `id` INT NOT NULL AUTO_INCREMENT,
                  `slot_number` VARCHAR(10) NOT NULL,
                  `slot_type` VARCHAR(20) NOT NULL,
                  `is_occupied` BOOLEAN NOT NULL DEFAULT FALSE,
                  `current_vehicle_id` INT NULL,
                  `occupied_since` DATETIME NULL,
                  PRIMARY KEY (`id`),
                  UNIQUE INDEX `idx_slot_number` (`slot_number`),
                  INDEX `idx_is_occupied` (`is_occupied`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabel payments
            print("   💰 Membuat tabel 'payments'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `payments` (
                  `id` INT NOT NULL AUTO_INCREMENT,
                  `vehicle_id` INT NOT NULL,
                  `card_id` VARCHAR(100) NULL,
                  `amount` FLOAT NOT NULL,
                  `payment_method` VARCHAR(50) NOT NULL,
                  `payment_status` VARCHAR(20) NOT NULL DEFAULT 'pending',
                  `entry_time` DATETIME NOT NULL,
                  `exit_time` DATETIME NULL,
                  `duration_hours` FLOAT NULL,
                  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY (`id`),
                  INDEX `idx_vehicle_id` (`vehicle_id`),
                  INDEX `idx_card_id` (`card_id`),
                  INDEX `idx_payment_status` (`payment_status`),
                  INDEX `idx_created_at` (`created_at`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabel system_alerts
            print("   🚨 Membuat tabel 'system_alerts'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `system_alerts` (
                  `id` INT NOT NULL AUTO_INCREMENT,
                  `alert_type` VARCHAR(50) NOT NULL,
                  `severity` VARCHAR(20) NOT NULL,
                  `message` TEXT NOT NULL,
                  `is_resolved` BOOLEAN NOT NULL DEFAULT FALSE,
                  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  `resolved_at` DATETIME NULL,
                  PRIMARY KEY (`id`),
                  INDEX `idx_alert_type` (`alert_type`),
                  INDEX `idx_severity` (`severity`),
                  INDEX `idx_is_resolved` (`is_resolved`),
                  INDEX `idx_created_at` (`created_at`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
        connection.commit()
        print("✅ Semua tabel berhasil dibuat")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error membuat tabel: {e}")
        return False

def insert_initial_config():
    """Insert konfigurasi awal sistem"""
    print("\n🔧 Menambahkan konfigurasi awal sistem...")
    
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Cek apakah sudah ada config
            cursor.execute("SELECT COUNT(*) as count FROM system_config")
            result = cursor.fetchone()
            
            if result['count'] == 0:
                print("   📝 Menambahkan data konfigurasi...")
                
                configs = [
                    ('gate_auto_close_delay', '5', 'Auto close gate delay in seconds'),
                    ('camera_resolution', '1920x1080', 'Camera resolution setting'),
                    ('parking_rate_per_hour', '2000', 'Parking rate per hour in IDR'),
                    ('max_parking_capacity', '100', 'Maximum parking capacity'),
                    ('card_reader_timeout', '10', 'Card reader timeout in seconds'),
                    ('system_timezone', 'Asia/Jakarta', 'System timezone'),
                    ('backup_enabled', 'true', 'Enable automatic database backup'),
                    ('notification_email', 'admin@manlessparking.com', 'System notification email'),
                    ('gate_open_duration', '10', 'Gate open duration in seconds'),
                    ('log_retention_days', '90', 'Log retention period in days')
                ]
                
                for config in configs:
                    cursor.execute(
                        "INSERT INTO system_config (config_key, config_value, description) VALUES (%s, %s, %s)",
                        config
                    )
                
                connection.commit()
                print(f"✅ {len(configs)} konfigurasi awal berhasil ditambahkan")
            else:
                print(f"ℹ️  Konfigurasi sudah ada ({result['count']} entries)")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error menambahkan konfigurasi: {e}")
        return False

def verify_database():
    """Verifikasi database dan tabel"""
    print("\n🔍 Verifikasi database...")
    
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"\n📊 Database '{DB_NAME}' berisi {len(tables)} tabel:")
            for table in tables:
                table_name = list(table.values())[0]
                cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
                count = cursor.fetchone()['count']
                print(f"   ✓ {table_name}: {count} records")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifikasi: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 SETUP DATABASE SKYPARKING")
    print("=" * 60)
    
    # Step 1: Create database
    if not create_database():
        sys.exit(1)
    
    # Step 2: Create tables
    if not create_tables():
        sys.exit(1)
    
    # Step 3: Insert initial config
    if not insert_initial_config():
        sys.exit(1)
    
    # Step 4: Verify
    if not verify_database():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ SETUP DATABASE SELESAI!")
    print("=" * 60)
    print(f"\n📌 Database: {DB_NAME}")
    print(f"📌 Host: {DB_HOST}:{DB_PORT}")
    print(f"📌 User: {DB_USER}")
    print("\n💡 Selanjutnya, Anda bisa:")
    print(f"   1. Import sample data: python insert_sample_data.py")
    print(f"   2. Restart backend: tekan Ctrl+C di backend dan jalankan ulang")
    print(f"   3. Akses frontend: http://localhost:5173")
    print()

if __name__ == "__main__":
    main()

