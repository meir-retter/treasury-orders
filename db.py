import dataclasses
import sqlite3

from data_model import Order
from typing import List, Tuple

DB_NAME = "treasury_rates.db"


def init_db() -> None:
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS orders (
                term TEXT,
                cents INTEGER,
                yield_basis_points INTEGER,
                timestamp TEXT
            )"""
        )


def read_orders() -> List[Order]:
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        res = cur.execute(
            "SELECT term, cents, yield_basis_points, timestamp FROM orders ORDER BY timestamp DESC"
        )
        return [Order(*db_row) for db_row in res.fetchall()]


def insert_order(conn: sqlite3.Connection, order: Order) -> None:
    cur = conn.cursor()
    insert_query = "INSERT INTO orders VALUES (?, ?, ?, ?)"
    cur.execute(insert_query, dataclasses.astuple(order))
    conn.commit()
