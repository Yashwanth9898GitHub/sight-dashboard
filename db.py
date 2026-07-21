"""SQLite data layer for the Sight Order Dashboard."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "orders.db"

STATUS_ORDERED = "Ordered"
STATUS_DELIVERED = "Delivered"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mobile_number TEXT NOT NULL,
                age INTEGER NOT NULL,
                sight TEXT NOT NULL,
                entry_date TEXT NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Ordered',
                delivered_date TEXT
            )
            """
        )


def add_order(name, mobile_number, age, sight, entry_date, price):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO orders (name, mobile_number, age, sight, entry_date, price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, mobile_number, age, sight, entry_date, price, STATUS_ORDERED),
        )


def get_orders(status):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM orders WHERE status = ? ORDER BY entry_date DESC, id DESC",
            (status,),
        ).fetchall()
        return [dict(row) for row in rows]


def mark_delivered(order_id, delivered_date):
    with get_connection() as conn:
        conn.execute(
            "UPDATE orders SET status = ?, delivered_date = ? WHERE id = ?",
            (STATUS_DELIVERED, delivered_date, order_id),
        )


def delete_order(order_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
