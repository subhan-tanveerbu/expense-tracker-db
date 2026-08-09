"""
SQLite backend. No server required -- stores data in a local .db file.
Great for local development and as the first backend to get working.
"""

import sqlite3
from db.base import ExpenseDB


class SQLiteExpenseDB(ExpenseDB):

    def __init__(self, db_path="expenses_sqlite.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return self.conn
        except sqlite3.Error as e:
            raise ConnectionError(f"Could not connect to SQLite: {e}")

    def setup(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL
            )
        """)
        self.conn.commit()

    def add_expense(self, date, category, description, amount):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO expenses (date, category, description, amount) "
                "VALUES (?, ?, ?, ?)",
                (date, category, description, amount),
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Insert failed: {e}")

    def view_expenses(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM expenses ORDER BY date")
        return [dict(row) for row in cur.fetchall()]

    def search_by_category(self, category):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM expenses WHERE category = ? ORDER BY date",
            (category,),
        )
        return [dict(row) for row in cur.fetchall()]

    def update_expense(self, expense_id, date=None, category=None,
                        description=None, amount=None):
        fields, values = [], []
        if date is not None:
            fields.append("date = ?"); values.append(date)
        if category is not None:
            fields.append("category = ?"); values.append(category)
        if description is not None:
            fields.append("description = ?"); values.append(description)
        if amount is not None:
            fields.append("amount = ?"); values.append(amount)
        if not fields:
            return 0
        values.append(expense_id)
        cur = self.conn.cursor()
        cur.execute(f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?", values)
        self.conn.commit()
        return cur.rowcount

    def delete_expense(self, expense_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        return cur.rowcount

    def summary_by_category(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT category, COUNT(*) AS count, SUM(amount) AS total,
                   AVG(amount) AS average
            FROM expenses GROUP BY category ORDER BY total DESC
        """)
        return [dict(row) for row in cur.fetchall()]

    def highest_expense(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM expenses ORDER BY amount DESC LIMIT 1")
        row = cur.fetchone()
        return dict(row) if row else None

    def filter_by_date_range(self, start_date, end_date):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM expenses WHERE date BETWEEN ? AND ? ORDER BY date",
            (start_date, end_date),
        )
        return [dict(row) for row in cur.fetchall()]

    def close(self):
        if self.conn:
            self.conn.close()
