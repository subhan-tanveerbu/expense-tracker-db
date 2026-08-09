"""
Extra Challenge: compare the same expense data across SQLite, MySQL,
PostgreSQL, and MongoDB.

Connects to whichever backends are reachable, prints a record count
and total spend from each, and reports if a backend is unreachable
instead of crashing the whole script.

Run directly: python extra_challenges/compare_databases.py
(run this AFTER you've added some expenses through main.py in each
backend, so there's actually something to compare)
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from db.sqlite_db import SQLiteExpenseDB
from db.mysql_db import MySQLExpenseDB
from db.postgres_db import PostgresExpenseDB
from db.mongo_db import MongoExpenseDB


def summarize(name, db):
    try:
        db.connect()
        db.setup()
        rows = db.view_expenses()
        total = sum(float(r["amount"]) for r in rows)
        print(f"{name:<12} | records: {len(rows):<5} | total spend: {total}")
        db.close()
    except Exception as e:
        print(f"{name:<12} | UNREACHABLE ({e})")


if __name__ == "__main__":
    print("Comparing expense data across all four backends:\n")
    summarize("SQLite", SQLiteExpenseDB(**config.SQLITE_CONFIG))
    summarize("MySQL", MySQLExpenseDB(**config.MYSQL_CONFIG))
    summarize("PostgreSQL", PostgresExpenseDB(**config.POSTGRES_CONFIG))
    summarize("MongoDB", MongoExpenseDB(**config.MONGO_CONFIG))
