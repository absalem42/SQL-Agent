import sqlite3
import os
from contextlib import contextmanager

# Get the directory of this file
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the erp_system directory, then to databases
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(BACKEND_DIR), "databases", "erp.db"))

@contextmanager
def get_db():
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # returns dict-like rows
    try:
        yield conn
    finally:
        conn.close()