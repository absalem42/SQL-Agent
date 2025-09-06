import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.getenv("DB_PATH", "../databases/erp.db")

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # returns dict-like rows
    try:
        yield conn
    finally:
        conn.close()