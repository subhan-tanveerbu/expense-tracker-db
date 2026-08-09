"""
Database-Based Expense Tracker (Week 2)

Extends the Week 1 CSV tracker so expenses can be stored in SQLite,
MySQL, PostgreSQL, or MongoDB -- same CLI, same expense structure,
different backend underneath. Pick a backend at startup (or switch
mid-session from the menu).
"""

import sys
from datetime import datetime

import config
from db.sqlite_db import SQLiteExpenseDB
from db.mysql_db import MySQLExpenseDB
from db.postgres_db import PostgresExpenseDB
from db.mongo_db import MongoExpenseDB


BACKENDS = {
    "1": ("SQLite", lambda: SQLiteExpenseDB(**config.SQLITE_CONFIG)),
    "2": ("MySQL", lambda: MySQLExpenseDB(**config.MYSQL_CONFIG)),
    "3": ("PostgreSQL", lambda: PostgresExpenseDB(**config.POSTGRES_CONFIG)),
    "4": ("MongoDB", lambda: MongoExpenseDB(**config.MONGO_CONFIG)),
}


def choose_backend():
    print("\nWhich database do you want to use?")
    for key, (name, _) in BACKENDS.items():
        print(f"  {key}. {name}")
    choice = input("Choice: ").strip()
    if choice not in BACKENDS:
        print("Invalid choice, defaulting to SQLite.")
        choice = "1"
    name, factory = BACKENDS[choice]
    db = factory()
    try:
        db.connect()
        db.setup()
        print(f"Connected to {name}.")
        return db, name
    except (ConnectionError, RuntimeError) as e:
        print(f"Failed to connect to {name}: {e}")
        print("Falling back to SQLite so you can keep working.")
        db = SQLiteExpenseDB(**config.SQLITE_CONFIG)
        db.connect()
        db.setup()
        return db, "SQLite"


def valid_date(text):
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def prompt_expense_fields(defaults=None):
    """Collect date/category/description/amount, with basic validation."""
    defaults = defaults or {}

    date = input(f"Date (YYYY-MM-DD){' [' + str(defaults.get('date','')) + ']' if defaults else ''}: ").strip()
    if not date and defaults:
        date = defaults.get("date")
    while date and not valid_date(str(date)):
        date = input("Invalid format. Date (YYYY-MM-DD): ").strip()

    category = input(f"Category{' [' + str(defaults.get('category','')) + ']' if defaults else ''}: ").strip()
    if not category and defaults:
        category = defaults.get("category")

    description = input(f"Description{' [' + str(defaults.get('description','')) + ']' if defaults else ''}: ").strip()
    if not description and defaults:
        description = defaults.get("description")

    amount_raw = input(f"Amount{' [' + str(defaults.get('amount','')) + ']' if defaults else ''}: ").strip()
    amount = defaults.get("amount") if defaults else None
    if amount_raw:
        try:
            amount = float(amount_raw)
        except ValueError:
            print("Invalid amount, keeping previous/blank value.")

    return date, category, description, amount


def print_table(rows):
    if not rows:
        print("No records found.")
        return
    for r in rows:
        rid = r.get("id", "")
        print(f"  [{rid}] {r.get('date')} | {r.get('category'):<15} | "
              f"{str(r.get('description') or ''):<20} | {r.get('amount')}")


def add_expense(db):
    print("\n-- Add Expense --")
    date, category, description, amount = prompt_expense_fields()
    if not (date and category and amount is not None):
        print("Date, category, and amount are required. Cancelled.")
        return
    try:
        new_id = db.add_expense(date, category, description, amount)
        print(f"Added expense with id {new_id}.")
    except RuntimeError as e:
        print(f"Error: {e}")


def view_expenses(db):
    print("\n-- All Expenses --")
    print_table(db.view_expenses())


def search_expenses(db):
    print("\n-- Search by Category --")
    category = input("Category: ").strip()
    print_table(db.search_by_category(category))


def update_expense(db):
    print("\n-- Update Expense --")
    expense_id = input("Expense id to update: ").strip()
    if not expense_id:
        print("Cancelled.")
        return
    print("Leave a field blank to keep it unchanged.")
    date, category, description, amount = prompt_expense_fields()
    try:
        affected = db.update_expense(
            expense_id,
            date=date or None,
            category=category or None,
            description=description or None,
            amount=amount,
        )
        print(f"Updated {affected} record(s)." if affected else "No record matched that id.")
    except Exception as e:
        print(f"Error: {e}")


def delete_expense(db):
    print("\n-- Delete Expense --")
    expense_id = input("Expense id to delete: ").strip()
    confirm = input(f"Are you sure you want to delete id {expense_id}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return
    try:
        affected = db.delete_expense(expense_id)
        print(f"Deleted {affected} record(s)." if affected else "No record matched that id.")
    except Exception as e:
        print(f"Error: {e}")


def summary(db):
    print("\n-- Category Summary --")
    rows = db.summary_by_category()
    if not rows:
        print("No records found.")
        return
    for r in rows:
        print(f"  {r['category']:<15} count={r['count']:<4} "
              f"total={r['total']:<10} avg={round(float(r['average']), 2)}")


def highest(db):
    print("\n-- Highest Expense --")
    row = db.highest_expense()
    if not row:
        print("No records found.")
        return
    print(f"  [{row.get('id')}] {row.get('date')} | {row.get('category')} | "
          f"{row.get('description')} | {row.get('amount')}")


def date_range(db):
    print("\n-- Filter by Date Range --")
    start = input("Start date (YYYY-MM-DD): ").strip()
    end = input("End date (YYYY-MM-DD): ").strip()
    if not (valid_date(start) and valid_date(end)):
        print("Invalid date(s). Cancelled.")
        return
    print_table(db.filter_by_date_range(start, end))


MENU = """
========== Expense Tracker (Database Edition) ==========
Current backend: {backend}
1. Add Expense
2. View Expenses
3. Search by Category
4. Update Expense
5. Delete Expense
6. Category Summary
7. Highest Expense
8. Filter by Date Range
9. Switch Database
10. Exit
"""


def main():
    db, backend_name = choose_backend()

    actions = {
        "1": add_expense,
        "2": view_expenses,
        "3": search_expenses,
        "4": update_expense,
        "5": delete_expense,
        "6": summary,
        "7": highest,
        "8": date_range,
    }

    while True:
        print(MENU.format(backend=backend_name))
        choice = input("Choose an option: ").strip()

        if choice in actions:
            actions[choice](db)
        elif choice == "9":
            db.close()
            db, backend_name = choose_backend()
        elif choice == "10":
            db.close()
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
    except Exception as e:
        print(f"Unexpected error: {e}")
