import sqlite3


def get_orders_from_db():
    conn = sqlite3.connect("treasury_rates.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS orders(term, amount, yield, timestamp)")
    res = cur.execute(
        "SELECT term, amount, yield, timestamp FROM orders ORDER BY timestamp DESC"
    )
    rows = res.fetchall()
    conn.close()
    return rows


def insert_order(conn, term, amount, yld, timestamp):
    cur = conn.cursor()
    insert_query = "INSERT INTO orders VALUES (?, ?, ?, ?)"
    cur.execute(insert_query, (term, amount, yld, timestamp))
    conn.commit()
