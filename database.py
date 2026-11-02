 
import sqlite3
import pandas as pd

DB_NAME = "expenses.db"


def get_connection():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)


def create_table():
    """Create the transactions table if it does not exist."""

    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT
            )
        """)


def add_transaction(transaction_type, amount, category, date, description):
    """Save a new income or expense transaction."""

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO transactions
            (transaction_type, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            transaction_type,
            amount,
            category,
            date,
            description
        ))


def get_transactions():
    """Retrieve all transactions from the database."""

    with get_connection() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM transactions ORDER BY date DESC, id DESC",
            conn
        )

    return df


def delete_transaction(transaction_id):
    """Delete a transaction using its ID."""

    with get_connection() as conn:
        conn.execute(
            "DELETE FROM transactions WHERE id = ?",
            (int(transaction_id),)
        )