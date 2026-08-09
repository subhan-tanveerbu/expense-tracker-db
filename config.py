"""
Central place for connection settings. Reads from a .env file if
python-dotenv is installed and a .env exists, otherwise falls back to
sensible local-dev defaults (which you can also just edit directly).
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional; env vars / defaults still work

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "expense_tracker"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
}

POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", ""),
    "database": os.getenv("POSTGRES_DATABASE", "expense_tracker"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
}

MONGO_CONFIG = {
    "uri": os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
    "database": os.getenv("MONGO_DATABASE", "expense_tracker"),
}

SQLITE_CONFIG = {
    "db_path": os.getenv("SQLITE_PATH", "expenses_sqlite.db"),
}
