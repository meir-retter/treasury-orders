import dataclasses
import sqlite3
from utils import Order
from typing import List

DB_NAME = "treasury_rates.db"


def read_db_orders() -> List[Order]:
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
        res = cur.execute(
            "SELECT term, cents, yield_basis_points, timestamp FROM orders ORDER BY timestamp DESC"
        )
        return [Order(*row) for row in res.fetchall()]


def insert_order(conn, order) -> None:
    cur = conn.cursor()
    insert_query = "INSERT INTO orders VALUES (?, ?, ?, ?)"
    cur.execute(insert_query, dataclasses.astuple(order))
    conn.commit()
