"""************************************"""
"""    Code By Vinzuda Manthan S.      """
"""************************************"""

import sqlite3
from datetime import datetime

class Database:
    """Handles all database interactions for the banking system."""
    
    def __init__(self, db_name="bank.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """Returns a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes tables if they do not exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                dob TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                address TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                account_number TEXT UNIQUE NOT NULL,
                ifsc_code TEXT NOT NULL,
                account_type TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0.0,
                is_active INTEGER DEFAULT 1,
                is_frozen INTEGER DEFAULT 0,
                failed_attempts INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Transactions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                balance_after REAL NOT NULL,
                related_account TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_number) REFERENCES users (account_number)
            )
        ''')

        conn.commit()
        conn.close()

# Shared instance
db = Database()
