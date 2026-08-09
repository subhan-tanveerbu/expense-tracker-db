# 💾 Database-Based Expense Tracker (Week 2)

A command-line Personal Expense Tracker that extends the [Week 1 CSV
version](https://github.com/subhan-tanveerbu/Personal-Expense-Tracker)
to store the same expense data across **SQLite, MySQL, PostgreSQL,
and MongoDB** — same CLI menu, same expense structure, four different
databases underneath.

---

## 📌 Project Overview

Built as a Week 2 mini project to practice relational (SQL) and
document-based (NoSQL) database fundamentals: schema design, CRUD
operations, parameterized queries, JOINs, GROUP BY reporting, and
connecting Python to real database servers.

---

## ✨ Features

- ➕ Add, 📋 view, 🔍 search, ✏️ update, and 🗑️ delete expenses
- 📊 Category-wise summary (count / total / average) via `GROUP BY`
- 💸 Highest single expense lookup
- 📅 Filter expenses by date range
- 🔀 Switch between SQLite / MySQL / PostgreSQL / MongoDB at runtime
- 🔒 Parameterized queries everywhere (no string-formatted SQL)
- ⚠️ Connection and query error handling with graceful fallback to SQLite

---

## 🛠️ Technologies Used

- Python 3
- `sqlite3` (standard library)
- `mysql-connector-python`
- `psycopg2-binary`
- `pymongo`
- `python-dotenv`

---

## 📂 Project Structure

```
expense-tracker-db/
│
├── main.py                          # CLI entry point & menu loop
├── config.py                        # Reads connection settings from .env
├── requirements.txt                 # Python dependencies
├── .env.example                     # Template for your local credentials
├── .gitignore
│
├── db/
│   ├── base.py                      # Abstract interface (shared contract)
│   ├── sqlite_db.py                 # SQLite implementation
│   ├── mysql_db.py                  # MySQL implementation
│   ├── postgres_db.py               # PostgreSQL implementation
│   └── mongo_db.py                  # MongoDB implementation
│
└── extra_challenges/
    ├── categories_fk_example.py     # Normalized categories table + FK (SQLite)
    └── compare_databases.py         # Compares record counts/totals across all 4
```

Each backend in `db/` implements the same `ExpenseDB` interface from
`db/base.py`, so `main.py` never needs to know which database it's
actually talking to — it just calls `db.add_expense(...)`,
`db.view_expenses()`, etc.

---

## 🚀 Getting Started

### 1. Install the database servers

You need SQLite (already built into Python — nothing to install),
plus MySQL, PostgreSQL, and MongoDB servers running locally.

| Database | Windows | Mac (Homebrew) | Linux (apt) |
|---|---|---|---|
| MySQL | [MySQL Installer](https://dev.mysql.com/downloads/installer/) | `brew install mysql && brew services start mysql` | `sudo apt install mysql-server` |
| PostgreSQL | [postgresql.org installer](https://www.postgresql.org/download/windows/) | `brew install postgresql@16 && brew services start postgresql@16` | `sudo apt install postgresql postgresql-contrib` |
| MongoDB | [MongoDB Community MSI](https://www.mongodb.com/try/download/community) | `brew tap mongodb/brew && brew install mongodb-community && brew services start mongodb-community` | Follow MongoDB's official apt repo docs, then `sudo systemctl start mongod` |

Verify each is running:
```
mysql -u root -p
psql -U postgres
mongosh
```

### 2. Clone and set up the project

```
git clone <your-repo-url>
cd expense-tracker-db
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure your credentials

```
cp .env.example .env
```
Then edit `.env` with your actual MySQL/PostgreSQL/MongoDB passwords.
`config.py` loads this automatically. If you skip this step, the app
falls back to `root`/blank-password local defaults, which works for
most default local installs.

### 4. Run the app

```
python3 main.py
```

You'll be asked which database to use, then dropped into the menu.
The app auto-creates the database, table/collection, and schema on
first connection — no manual `CREATE DATABASE` step required.

---

## 📸 Sample Menu

```
========== Expense Tracker (Database Edition) ==========
Current backend: SQLite
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
```

---

## 🧩 Extra Challenges Covered

- ✅ Monthly/category spending via SQL `GROUP BY` — see menu option 6
- ✅ Compare the same records across all four databases — run
  `python extra_challenges/compare_databases.py`
- ✅ Database switch option — menu option 9, live during the session
- ✅ Filter expenses by date range — menu option 8
- ✅ Categories table connected via foreign key — see
  `extra_challenges/categories_fk_example.py`
- ✅ MongoDB stores a full mirrored document per expense by design —
  see `db/mongo_db.py`

---

## 🎯 Concepts Demonstrated

- Schema design, normalization, primary/foreign keys
- SQL: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `WHERE`, `ORDER BY`,
  `LIMIT`, `INNER JOIN`, `GROUP BY`, `HAVING`-style aggregation
- Parameterized queries (SQL injection–safe) in all three SQL backends
- NoSQL document modeling and MongoDB's aggregation pipeline
- Python ↔ database integration with `sqlite3`, `mysql-connector-python`,
  `psycopg2`, and `pymongo`
- Try/except error handling around connections and queries
- Abstract base classes for writing backend-agnostic application code

---

## 📚 Learning Outcomes

Through this project, I learned how to:
- Design the same schema across three different SQL engines and one
  document store, and reason about where they diverge.
- Write parameterized queries to avoid SQL injection.
- Build a clean abstraction (`ExpenseDB`) so application logic doesn't
  care which database is plugged in underneath.
- Handle connection failures and missing databases gracefully instead
  of crashing.
- Compare relational vs document-based data modeling in practice.

---

## 👨‍💻 Author

**Subhan Tanveer**
- GitHub: [subhan-tanveerbu](https://github.com/subhan-tanveerbu)

---

## 📄 License

This project is created for educational and learning purposes.
