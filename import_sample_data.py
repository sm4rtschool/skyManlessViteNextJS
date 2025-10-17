#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk import sample data ke database SkyParking
Menggunakan file sample_data.sql
"""

import pymysql
import sys

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

def import_sample_data():
    """Import sample data dari file SQL"""
    print("=" * 60)
    print("📦 IMPORT SAMPLE DATA SKYPARKING")
    print("=" * 60)
    print()
    
    try:
        # Baca file SQL
        print("📖 Membaca file sample_data.sql...")
        with open('sample_data.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split SQL statements (sederhana)
        sql_statements = []
        current_statement = []
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # Skip komentar dan baris kosong
            if not line or line.startswith('--'):
                continue
            
            current_statement.append(line)
            
            # Jika baris diakhiri dengan semicolon, statement selesai
            if line.endswith(';'):
                statement = ' '.join(current_statement)
                sql_statements.append(statement)
                current_statement = []
        
        print(f"✅ Ditemukan {len(sql_statements)} SQL statements")
        
        # Koneksi ke database
        print(f"\n🔧 Menghubungkan ke database '{DB_NAME}'...")
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ Berhasil terhubung ke database")
        
        # Execute statements
        print("\n📝 Mengimport sample data...")
        with connection.cursor() as cursor:
            success_count = 0
            error_count = 0
            
            for i, statement in enumerate(sql_statements, 1):
                # Skip SELECT statements (query verification)
                if statement.upper().strip().startswith('SELECT'):
                    continue
                
                try:
                    cursor.execute(statement)
                    success_count += 1
                    
                    # Tampilkan progress setiap 5 statement
                    if i % 5 == 0:
                        print(f"   ✓ Progress: {i}/{len(sql_statements)} statements")
                        
                except Exception as e:
                    error_count += 1
                    # Ignore duplicate entry errors
                    if "Duplicate entry" not in str(e):
                        print(f"   ⚠️  Warning on statement {i}: {str(e)[:100]}")
        
        connection.commit()
        print(f"\n✅ Import selesai!")
        print(f"   • {success_count} statements berhasil")
        print(f"   • {error_count} statements di-skip (sudah ada)")
        
        # Verifikasi data
        print("\n🔍 Verifikasi data yang diimport:")
        with connection.cursor() as cursor:
            tables = ['cards', 'vehicles', 'parking_slots', 'payments', 'parking_log', 'system_alerts']
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    result = cursor.fetchone()
                    print(f"   ✓ {table}: {result['count']} records")
                except:
                    pass
        
        connection.close()
        
        print("\n" + "=" * 60)
        print("✅ SAMPLE DATA BERHASIL DIIMPORT!")
        print("=" * 60)
        print("\n💡 Silakan restart backend untuk melihat perubahan")
        print()
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: File 'sample_data.sql' tidak ditemukan!")
        print("   Pastikan file ada di directory yang sama dengan script ini")
        return False
    except pymysql.err.OperationalError as e:
        print(f"❌ Error koneksi database: {e}")
        print("\n💡 Pastikan:")
        print("   1. MySQL server sudah berjalan")
        print("   2. Database 'skyparking' sudah dibuat (jalankan setup_database.py)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = import_sample_data()
    sys.exit(0 if success else 1)

