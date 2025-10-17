#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk menginsert sample data ke database MySQL/MariaDB
Sistem Manless Parking
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime
import sys
import os

# Set console encoding untuk Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Konfigurasi database
DB_CONFIG = {
    'host': '127.0.0.1',
    'database': 'skyparking',
    'user': 'root',
    'password': '',  # Sesuaikan dengan password MySQL Anda
    'port': 3306
}

def create_connection():
    """Membuat koneksi ke database MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✅ Berhasil terhubung ke database MySQL")
            return connection
    except Error as e:
        print(f"❌ Error saat menghubungkan ke database: {e}")
        return None

def execute_sql_file(connection, sql_file_path):
    """Eksekusi file SQL"""
    try:
        cursor = connection.cursor()
        
        # Baca file SQL
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split berdasarkan statement (;)
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        success_count = 0
        for statement in sql_statements:
            if statement.startswith('--') or not statement:
                continue
                
            try:
                cursor.execute(statement)
                success_count += 1
            except Error as e:
                print(f"⚠️  Error pada statement: {e}")
                continue
        
        connection.commit()
        print(f"✅ Berhasil mengeksekusi {success_count} statement SQL")
        
    except Error as e:
        print(f"❌ Error saat mengeksekusi SQL: {e}")
        connection.rollback()
    except FileNotFoundError:
        print(f"❌ File SQL tidak ditemukan: {sql_file_path}")
    finally:
        if cursor:
            cursor.close()

def insert_sample_data(connection):
    """Insert sample data langsung melalui Python"""
    try:
        cursor = connection.cursor()
        
        # Data sample untuk cards
        cards_data = [
            ('CARD001', 'employee', 'Ahmad Wijaya', 1, '2024-01-15 08:00:00', '2024-12-23 09:30:00'),
            ('CARD002', 'visitor', 'Siti Nurhaliza', 1, '2024-01-20 10:15:00', '2024-12-22 14:45:00'),
            ('CARD003', 'employee', 'Budi Santoso', 1, '2024-02-01 07:30:00', '2024-12-23 08:15:00'),
            ('CARD004', 'monthly', 'Dewi Lestari', 1, '2024-02-10 11:00:00', '2024-12-21 16:20:00'),
            ('CARD005', 'visitor', 'Rahman Ali', 1, '2024-03-05 13:45:00', '2024-12-20 12:10:00'),
            ('CARD006', 'employee', 'Linda Sari', 0, '2024-01-25 09:20:00', '2024-11-15 17:30:00'),
            ('CARD007', 'vip', 'Hendra Kusuma', 1, '2024-03-15 14:00:00', '2024-12-23 10:45:00'),
            ('CARD008', 'monthly', 'Rina Permata', 1, '2024-04-01 08:30:00', '2024-12-22 15:50:00')
        ]
        
        # Insert cards
        cards_query = """
        INSERT INTO cards (card_id, card_type, owner_name, is_active, registered_at, last_used) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(cards_query, cards_data)
        print("✅ Sample data cards berhasil diinsert")
        
        # Data sample untuk vehicles
        vehicles_data = [
            ('B1234ABC', 'Ahmad Wijaya', 'car', 'CARD001', '2024-01-15 08:00:00', 1),
            ('B5678DEF', 'Siti Nurhaliza', 'motorcycle', 'CARD002', '2024-01-20 10:15:00', 1),
            ('B9012GHI', 'Budi Santoso', 'car', 'CARD003', '2024-02-01 07:30:00', 1),
            ('B3456JKL', 'Dewi Lestari', 'car', 'CARD004', '2024-02-10 11:00:00', 1),
            ('B7890MNO', 'Rahman Ali', 'motorcycle', 'CARD005', '2024-03-05 13:45:00', 1),
            ('B2468PQR', 'Linda Sari', 'car', 'CARD006', '2024-01-25 09:20:00', 0),
            ('B1357STU', 'Hendra Kusuma', 'car', 'CARD007', '2024-03-15 14:00:00', 1),
            ('B8024VWX', 'Rina Permata', 'motorcycle', 'CARD008', '2024-04-01 08:30:00', 1),
            ('B4680YZA', 'Teguh Prakoso', 'car', None, '2024-05-10 09:15:00', 1),
            ('B9753BCD', 'Maya Indah', 'motorcycle', None, '2024-06-20 11:30:00', 1)
        ]
        
        vehicles_query = """
        INSERT INTO vehicles (license_plate, owner_name, vehicle_type, card_id, registered_at, is_active) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(vehicles_query, vehicles_data)
        print("✅ Sample data vehicles berhasil diinsert")
        
        # Data sample untuk parking_slots
        parking_slots_data = [
            ('A001', 'car', 1, 1, '2024-12-23 08:15:00'),
            ('A002', 'car', 0, None, None),
            ('A003', 'car', 1, 3, '2024-12-23 09:30:00'),
            ('A004', 'car', 0, None, None),
            ('A005', 'car', 1, 4, '2024-12-23 07:45:00'),
            ('B001', 'motorcycle', 1, 2, '2024-12-23 08:45:00'),
            ('B002', 'motorcycle', 0, None, None),
            ('B003', 'motorcycle', 1, 5, '2024-12-23 10:15:00'),
            ('B004', 'motorcycle', 0, None, None),
            ('B005', 'motorcycle', 0, None, None),
            ('VIP001', 'vip', 1, 7, '2024-12-23 09:00:00'),
            ('VIP002', 'vip', 0, None, None),
            ('DISABLE001', 'disabled', 0, None, None),
            ('DISABLE002', 'disabled', 0, None, None)
        ]
        
        parking_slots_query = """
        INSERT INTO parking_slots (slot_number, slot_type, is_occupied, current_vehicle_id, occupied_since) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(parking_slots_query, parking_slots_data)
        print("✅ Sample data parking_slots berhasil diinsert")
        
        connection.commit()
        print("🎉 Semua sample data berhasil diinsert ke database!")
        
    except Error as e:
        print(f"❌ Error saat insert sample data: {e}")
        connection.rollback()
    finally:
        if cursor:
            cursor.close()

def verify_data(connection):
    """Verifikasi data yang sudah diinsert"""
    try:
        cursor = connection.cursor()
        
        # Query untuk cek jumlah data di setiap tabel
        tables = ['cards', 'vehicles', 'parking_slots', 'payments', 'parking_log', 'system_alerts', 'system_config']
        
        print("\n📊 VERIFIKASI DATA:")
        print("-" * 40)
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table.ljust(15)}: {count} records")
        
        # Cek status parking slots
        print("\n🅿️  STATUS PARKING SLOTS:")
        print("-" * 40)
        cursor.execute("""
            SELECT 
                slot_type,
                COUNT(*) as total_slots,
                SUM(is_occupied) as occupied_slots,
                COUNT(*) - SUM(is_occupied) as available_slots
            FROM parking_slots 
            GROUP BY slot_type
        """)
        
        for row in cursor.fetchall():
            slot_type, total, occupied, available = row
            print(f"{slot_type.ljust(12)}: {total} total, {occupied} occupied, {available} available")
        
    except Error as e:
        print(f"❌ Error saat verifikasi data: {e}")
    finally:
        if cursor:
            cursor.close()

def main():
    """Fungsi utama"""
    print("🚀 MANLESS PARKING - SAMPLE DATA INSTALLER")
    print("=" * 50)
    
    # Buat koneksi ke database
    connection = create_connection()
    if not connection:
        sys.exit(1)
    
    try:
        # Pilihan metode insert
        print("\nPilih metode insert sample data:")
        print("1. Insert melalui file SQL (sample_data.sql)")
        print("2. Insert langsung melalui Python")
        
        choice = input("\nMasukkan pilihan (1/2): ").strip()
        
        if choice == '1':
            sql_file = 'sample_data.sql'
            if os.path.exists(sql_file):
                execute_sql_file(connection, sql_file)
            else:
                print(f"❌ File {sql_file} tidak ditemukan!")
                print("💡 Pastikan file sample_data.sql ada di direktori yang sama")
        
        elif choice == '2':
            # Hapus data existing terlebih dahulu
            confirm = input("\n⚠️  Hapus data existing terlebih dahulu? (y/n): ").strip().lower()
            if confirm == 'y':
                cursor = connection.cursor()
                tables = ['payments', 'parking_log', 'system_alerts', 'parking_slots', 'vehicles', 'cards']
                for table in tables:
                    cursor.execute(f"DELETE FROM {table}")
                    print(f"🗑️  Data tabel {table} dihapus")
                connection.commit()
                cursor.close()
            
            insert_sample_data(connection)
        
        else:
            print("❌ Pilihan tidak valid!")
            sys.exit(1)
        
        # Verifikasi data
        verify_data(connection)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Proses dibatalkan oleh user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\n🔌 Koneksi database ditutup")
    
    print("\n✨ Selesai! Database siap untuk integrasi sistem.")

if __name__ == "__main__":
    main() 