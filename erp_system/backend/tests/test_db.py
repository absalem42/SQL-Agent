# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db, DB_PATH

def test_existing_database():
    print(f"🔍 Looking for database at: {DB_PATH}")
    print(f"📁 Database exists: {os.path.exists(DB_PATH)}")
    
    try:
        with get_db() as conn:
            # Check what tables exist
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("📊 Existing tables:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Check data in each table
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  {table_name}: {count} records")
                
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        print(f"💡 Try creating the database first or check if the path exists")
        return False

if __name__ == "__main__":
    test_existing_database()