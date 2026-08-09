"""
PostgreSQL backend. Requires a running PostgreSQL server (see README).
Uses psycopg2 with parameterized (%s) queries throughout.
"""

import psycopg2
import psycopg2.extras
from db.base import ExpenseDB


class PostgresExpenseDB(ExpenseDB):

    def __init__(self, host, user, password, database, port=5432):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = None

    def connect(self):
        try:
            # Connect to the default 'postgres' db first to create ours if missing
            bootstrap = psycopg2.connect(
                host=self.host, user=self.user, password=self.password,
                port=self.port, dbname="postgres",
            )
            bootstrap.autocommit = True
            cur = bootstrap.cursor()
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database,))
            if not cur.fetchone():
                cur.execute(f'CREATE DATABASE "{self.database}"')
            cur.close()
            bootstrap.close()

            self.conn = psycopg2.connect(
                host=self.host, user=self.user, password=self.password,
                port=self.port, dbname=self.database,
            )
            return self.conn
        except psycopg2.Error as e:
            raise ConnectionError(f"Could not connect to PostgreSQL: {e}")

    def setup(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                category VARCHAR(100) NOT NULL,
                description VARCHAR(255),
                amount NUMERIC(10, 2) NOT NULL
            )
        """)
        self.conn.commit()
        cur.close()

    def add_expense(self, date, category, description, amount):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO expenses (date, category, description, amount) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                (date, category, description, amount),
            )
            new_id = cur.fetchone()[0]
            self.conn.commit()
            cur.close()
            return new_id
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Insert failed: {e}")

    def _dict_cursor(self):
        return self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def view_expenses(self):
        cur = self._dict_cursor()
        cur.execute("SELECT * FROM expenses ORDER BY date")
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        return rows

    def search_by_category(self, category):
        cur = self._dict_cursor()
        cur.execute(
            "SELECT * FROM expenses WHERE category = %s ORDER BY date",
            (category,),
        )
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        return rows

    def update_expense(self, expense_id, date=None, category=None,
                        description=None, amount=None):
        fields, values = [], []
        if date is not None:
            fields.append("date = %s"); values.append(date)
        if category is not None:
            fields.append("category = %s"); values.append(category)
        if description is not None:
            fields.append("description = %s"); values.append(description)
        if amount is not None:
            fields.append("amount = %s"); values.append(amount)
        if not fields:
            return 0
        values.append(expense_id)
        cur = self.conn.cursor()
        cur.execute(f"UPDATE expenses SET {', '.join(fields)} WHERE id = %s", values)
        self.conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected

    def delete_expense(self, expense_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        self.conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected

    def summary_by_category(self):
        cur = self._dict_cursor()
        cur.execute("""
            SELECT category, COUNT(*) AS count, SUM(amount) AS total,
                   AVG(amount) AS average
            FROM expenses GROUP BY category ORDER BY total DESC
        """)
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        return rows

    def highest_expense(self):
        cur = self._dict_cursor()
        cur.execute("SELECT * FROM expenses ORDER BY amount DESC LIMIT 1")
        row = cur.fetchone()
        cur.close()
        return dict(row) if row else None

    def filter_by_date_range(self, start_date, end_date):
        cur = self._dict_cursor()
        cur.execute(
            "SELECT * FROM expenses WHERE date BETWEEN %s AND %s ORDER BY date",
            (start_date, end_date),
        )
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        return rows

    def close(self):
        if self.conn:
            self.conn.close()
