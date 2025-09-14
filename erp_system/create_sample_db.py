"""
Create a sample SQLite database (erp_sample.db) for graders/reviewers.

Behavior:
- If databases/erp.db exists, copy it to databases/erp_sample.db (fast path).
- Otherwise, create a minimal schema and insert seed rows for core ERP tables.

Usage:
  python create_sample_db.py

The Makefile calls this in `make setup-local` automatically.
"""

from pathlib import Path
import os
import shutil
import sqlite3

ROOT = Path(__file__).parent
DB_DIR = ROOT / "databases"
SRC_DB = DB_DIR / "erp.db"
DEST_DB = DB_DIR / "erp_sample.db"


def copy_if_exists():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    if SRC_DB.exists():
        shutil.copy2(SRC_DB, DEST_DB)
        print(f"✅ Copied existing database to {DEST_DB}")
        return True
    return False


def create_minimal_schema_and_seed():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DEST_DB))
    cur = conn.cursor()

    # Core tables (minimal set)
    cur.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            total REAL NOT NULL,
            status TEXT,
            created_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            total REAL NOT NULL,
            status TEXT,
            issued_at TEXT,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );

        CREATE TABLE IF NOT EXISTS invoice_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            method TEXT,
            paid_at TEXT,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
        );

        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            contact_email TEXT,
            message TEXT,
            score REAL,
            status TEXT,
            created_at TEXT
        );
        """
    )

    # Seed data
    cur.executemany(
        "INSERT INTO customers (name, email, created_at) VALUES (?,?,?)",
        [
            ("Acme Corp", "contact@acme.example", "2024-01-10 10:00:00"),
            ("Globex LLC", "sales@globex.example", "2024-02-15 12:30:00"),
            ("Initech", "info@initech.example", "2024-03-01 09:15:00"),
        ],
    )

    cur.executemany(
        "INSERT INTO products (name, price) VALUES (?,?)",
        [
            ("Widget Pro", 199.99),
            ("Service A", 499.00),
            ("Tool Max", 249.50),
        ],
    )

    cur.executemany(
        "INSERT INTO orders (customer_id, total, status, created_at) VALUES (?,?,?,?)",
        [
            (1, 948.49, "paid", "2024-04-05 14:00:00"),
            (2, 249.50, "pending", "2024-04-10 13:20:00"),
        ],
    )

    cur.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?,?,?,?)",
        [
            (1, 1, 2, 199.99),
            (1, 2, 1, 499.00),
            (2, 3, 1, 249.50),
        ],
    )

    cur.executemany(
        "INSERT INTO invoices (order_id, total, status, issued_at) VALUES (?,?,?,?)",
        [
            (1, 948.49, "issued", "2024-04-06 09:00:00"),
            (2, 249.50, "issued", "2024-04-11 10:00:00"),
        ],
    )

    cur.executemany(
        "INSERT INTO invoice_lines (invoice_id, product_id, quantity, price) VALUES (?,?,?,?)",
        [
            (1, 1, 2, 199.99),
            (1, 2, 1, 499.00),
            (2, 3, 1, 249.50),
        ],
    )

    cur.executemany(
        "INSERT INTO payments (invoice_id, amount, method, paid_at) VALUES (?,?,?,?)",
        [
            (1, 948.49, "card", "2024-04-06 12:00:00"),
        ],
    )

    cur.executemany(
        "INSERT INTO leads (customer_name, contact_email, message, score, status, created_at) VALUES (?,?,?,?,?,?)",
        [
            ("Wayne Enterprises", "bruce@wayne.example", "Interested in bulk order", 0.9, "new", "2024-04-02 08:30:00"),
            ("Stark Industries", "tony@stark.example", "Request for quote", 0.8, "contacted", "2024-04-03 11:45:00"),
        ],
    )

    conn.commit()
    conn.close()
    print(f"✅ Created minimal sample database at {DEST_DB}")


if __name__ == "__main__":
    if not copy_if_exists():
        create_minimal_schema_and_seed()
