import sqlite3

DB_NAME = "treasury_rates.db"

def get_orders_from_db():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS orders (
                term TEXT,
                amount REAL,
                yield_value REAL,
                timestamp TEXT
            )"""
        )
        res = cur.execute(
            "SELECT term, amount, yield_value, timestamp FROM orders ORDER BY timestamp DESC"
        )
        return res.fetchall()


def insert_order(conn, term, amount, yld, timestamp):
    cur = conn.cursor()
    insert_query = "INSERT INTO orders VALUES (?, ?, ?, ?)"
    cur.execute(insert_query, (term, amount, yld, timestamp))
    conn.commit()
