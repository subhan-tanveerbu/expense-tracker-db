"""
MySQL backend. Requires a running MySQL server (see README for setup).
Uses mysql-connector-python with parameterized (%s) queries throughout.
"""

import mysql.connector
from mysql.connector import Error as MySQLError
from db.base import ExpenseDB


class MySQLExpenseDB(ExpenseDB):

    def __init__(self, host, user, password, database, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = None

    def connect(self):
        try:
            # Connect without a database first so we can CREATE DATABASE IF NOT EXISTS
            bootstrap = mysql.connector.connect(
                host=self.host, user=self.user, password=self.password, port=self.port
            )
            cur = bootstrap.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            bootstrap.commit()
            cur.close()
            bootstrap.close()

            self.conn = mysql.connector.connect(
                host=self.host, user=self.user, password=self.password,
                database=self.database, port=self.port,
            )
            return self.conn
        except MySQLError as e:
            raise ConnectionError(f"Could not connect to MySQL: {e}")

    def setup(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                category VARCHAR(100) NOT NULL,
                description VARCHAR(255),
                amount DECIMAL(10, 2) NOT NULL
            )
        """)
        self.conn.commit()
        cur.close()

    def add_expense(self, date, category, description, amount):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO expenses (date, category, description, amount) "
                "VALUES (%s, %s, %s, %s)",
                (date, category, description, amount),
            )
            self.conn.commit()
            new_id = cur.lastrowid
            cur.close()
            return new_id
        except MySQLError as e:
            raise RuntimeError(f"Insert failed: {e}")

    def _dict_cursor(self):
        return self.conn.cursor(dictionary=True)

    def view_expenses(self):
        cur = self._dict_cursor()
        cur.execute("SELECT * FROM expenses ORDER BY date")
        rows = cur.fetchall()
        cur.close()
        return rows

    def search_by_category(self, category):
        cur = self._dict_cursor()
        cur.execute(
            "SELECT * FROM expenses WHERE category = %s ORDER BY date",
            (category,),
        )
        rows = cur.fetchall()
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
        rows = cur.fetchall()
        cur.close()
        return rows

    def highest_expense(self):
        cur = self._dict_cursor()
        cur.execute("SELECT * FROM expenses ORDER BY amount DESC LIMIT 1")
        row = cur.fetchone()
        cur.close()
        return row

    def filter_by_date_range(self, start_date, end_date):
        cur = self._dict_cursor()
        cur.execute(
            "SELECT * FROM expenses WHERE date BETWEEN %s AND %s ORDER BY date",
            (start_date, end_date),
        )
        rows = cur.fetchall()
        cur.close()
        return rows

    def monthly_spending_by_category(self, year, month):
        cur = self.conn.cursor(dictionary=True)

        cur.execute("""
            SELECT category,
                   COUNT(*) AS count,
                   SUM(amount) AS total,
                   AVG(amount) AS average
            FROM expenses
            WHERE YEAR(date) = %s AND MONTH(date) = %s
            GROUP BY category
            ORDER BY total DESC
        """, (year, month))

        rows = cur.fetchall()
        cur.close()
        return rows
    
    def close(self):
        if self.conn:
            self.conn.close()
