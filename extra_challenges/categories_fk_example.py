"""
Extra Challenge: categories table + foreign key (SQLite version).

Demonstrates normalizing category out of the expenses table into its
own categories table, connected via a foreign key -- this is the
relational-database way of avoiding duplicate category text in every
row (the normalization concept from Week 2's topic list).

Run directly: python extra_challenges/categories_fk_example.py
"""

import sqlite3

conn = sqlite3.connect("expenses_normalized.db")
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses_normalized (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        description TEXT,
        amount REAL NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
""")
conn.commit()


def get_or_create_category(name):
    cur.execute("SELECT id FROM categories WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def add_expense(date, category_name, description, amount):
    category_id = get_or_create_category(category_name)
    cur.execute(
        "INSERT INTO expenses_normalized (date, category_id, description, amount) "
        "VALUES (?, ?, ?, ?)",
        (date, category_id, description, amount),
    )
    conn.commit()


def view_expenses_with_category_names():
    cur.execute("""
        SELECT e.id, e.date, c.name AS category, e.description, e.amount
        FROM expenses_normalized e
        INNER JOIN categories c ON e.category_id = c.id
        ORDER BY e.date
    """)
    return cur.fetchall()


if __name__ == "__main__":
    add_expense("2026-08-01", "Food", "Burger", 850)
    add_expense("2026-08-02", "Food", "Groceries", 2200)
    add_expense("2026-08-02", "Transport", "Metro Card", 250)

    print("Expenses joined with category names via INNER JOIN:")
    for row in view_expenses_with_category_names():
        print(" ", row)

    conn.close()
