#!/usr/bin/env python3
"""
Sample Database Creator for ERP System
Creates erp_sample.db with test data for demonstration
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

def create_sample_database():
    """Create a sample ERP database with test data"""
    
    # Remove existing sample DB
    sample_db_path = Path("databases/erp_sample.db")
    sample_db_path.parent.mkdir(exist_ok=True)
    if sample_db_path.exists():
        sample_db_path.unlink()
    
    conn = sqlite3.connect(sample_db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        contact_email TEXT NOT NULL,
        phone TEXT,
        status TEXT NOT NULL DEFAULT 'new',
        score DECIMAL(3,1) DEFAULT 0.0,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        invoice_number TEXT UNIQUE NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        due_date DATE NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    )
    """)
    
    # Sample data
    customers_data = [
        ("Acme Corp", "contact@acme.com", "+1-555-0101", "123 Business St, NY"),
        ("Tech Solutions Ltd", "info@techsolutions.com", "+1-555-0102", "456 Tech Ave, CA"),
        ("Global Industries", "sales@global.com", "+1-555-0103", "789 Global Blvd, TX"),
        ("Startup Inc", "hello@startup.com", "+1-555-0104", "321 Innovation Dr, WA"),
        ("Enterprise Systems", "contact@enterprise.com", "+1-555-0105", "654 Corporate Way, FL")
    ]
    
    products = [
        ("Software License", 299.99),
        ("Consulting Services", 150.00),
        ("Hardware Setup", 599.99),
        ("Training Package", 199.99),
        ("Support Contract", 99.99),
        ("Custom Development", 2500.00)
    ]
    
    # Insert customers
    cursor.executemany("""
    INSERT INTO customers (name, email, phone, address) 
    VALUES (?, ?, ?, ?)
    """, customers_data)
    
    # Insert orders and order items
    for customer_id in range(1, 6):
        num_orders = random.randint(1, 3)
        for _ in range(num_orders):
            # Create order
            order_total = 0
            order_date = datetime.now() - timedelta(days=random.randint(1, 90))
            status = random.choice(['pending', 'completed', 'shipped', 'cancelled'])
            
            cursor.execute("""
            INSERT INTO orders (customer_id, total_amount, status, order_date)
            VALUES (?, ?, ?, ?)
            """, (customer_id, 0, status, order_date))
            
            order_id = cursor.lastrowid
            
            # Add order items
            num_items = random.randint(1, 4)
            for _ in range(num_items):
                product_name, unit_price = random.choice(products)
                quantity = random.randint(1, 5)
                item_total = unit_price * quantity
                order_total += item_total
                
                cursor.execute("""
                INSERT INTO order_items (order_id, product_name, quantity, unit_price)
                VALUES (?, ?, ?, ?)
                """, (order_id, product_name, quantity, unit_price))
            
            # Update order total
            cursor.execute("""
            UPDATE orders SET total_amount = ? WHERE id = ?
            """, (order_total, order_id))
    
    # Insert leads
    leads_data = [
        ("Future Tech Co", "leads@futuretech.com", "+1-555-0201", "qualified", 8.5, "website"),
        ("Small Business LLC", "owner@smallbiz.com", "+1-555-0202", "new", 6.2, "referral"),
        ("Big Corporation", "procurement@bigcorp.com", "+1-555-0203", "contacted", 9.1, "trade show"),
        ("Local Services", "info@localservices.com", "+1-555-0204", "lost", 3.4, "cold call"),
        ("Growth Startup", "ceo@growthstartup.com", "+1-555-0205", "new", 7.8, "linkedin")
    ]
    
    cursor.executemany("""
    INSERT INTO leads (company_name, contact_email, phone, status, score, source)
    VALUES (?, ?, ?, ?, ?, ?)
    """, leads_data)
    
    # Insert invoices
    cursor.execute("SELECT id FROM orders WHERE status = 'completed'")
    completed_orders = cursor.fetchall()
    
    for order_id, in completed_orders:
        cursor.execute("SELECT total_amount FROM orders WHERE id = ?", (order_id,))
        amount = cursor.fetchone()[0]
        
        invoice_number = f"INV-{order_id:04d}"
        due_date = datetime.now() + timedelta(days=30)
        status = random.choice(['pending', 'paid', 'overdue'])
        
        cursor.execute("""
        INSERT INTO invoices (order_id, invoice_number, amount, due_date, status)
        VALUES (?, ?, ?, ?, ?)
        """, (order_id, invoice_number, amount, due_date.date(), status))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Sample database created: {sample_db_path}")
    print("📊 Sample data includes:")
    print("   • 5 customers with contact information")
    print("   • 8-15 orders with various statuses")
    print("   • 15-45 order items with different products")
    print("   • 5 leads with different stages")
    print("   • Invoices for completed orders")

if __name__ == "__main__":
    create_sample_database()
