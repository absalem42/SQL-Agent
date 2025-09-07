#!/usr/bin/env python3
"""
Debug script to examine the actual database schema and data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from db import get_db

def examine_database():
    """Examine the database structure and sample data"""
    
    print("🔍 Database Schema Analysis")
    print("=" * 50)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        key_tables = ['customers', 'orders', 'leads', 'invoices', 'products']
        
        for table_name in key_tables:
            if (table_name,) in tables:
                print(f"\n📋 Table: {table_name}")
                print("-" * 30)
                
                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                print("Columns:")
                for col in columns:
                    print(f"  • {col[1]} ({col[2]}) {'- PRIMARY KEY' if col[5] else ''}")
                
                # Get sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                
                if rows:
                    print(f"\nSample data (first 3 rows):")
                    col_names = [desc[0] for desc in cursor.description]
                    
                    for i, row in enumerate(rows, 1):
                        print(f"\nRow {i}:")
                        for j, value in enumerate(row):
                            print(f"  {col_names[j]}: {value}")
                else:
                    print("No data found")
            else:
                print(f"\n❌ Table '{table_name}' not found")
        
        # Test some specific queries
        print(f"\n🧪 Testing Key Queries")
        print("=" * 30)
        
        # Test customers query
        try:
            cursor.execute("SELECT COUNT(*) as count FROM customers")
            count = cursor.fetchone()[0]
            print(f"✅ Customers count: {count}")
        except Exception as e:
            print(f"❌ Customers query failed: {e}")
        
        # Test orders query with different column possibilities
        order_amount_columns = ['total_amount', 'amount', 'total', 'order_total', 'price']
        for col in order_amount_columns:
            try:
                cursor.execute(f"SELECT {col} FROM orders LIMIT 1")
                print(f"✅ Orders has column: {col}")
                break
            except Exception:
                print(f"❌ Orders missing column: {col}")
        
        # Test leads columns
        lead_value_columns = ['estimated_value', 'value', 'amount', 'deal_value']
        for col in lead_value_columns:
            try:
                cursor.execute(f"SELECT {col} FROM leads LIMIT 1")
                print(f"✅ Leads has column: {col}")
                break
            except Exception:
                print(f"❌ Leads missing column: {col}")

if __name__ == "__main__":
    examine_database()
