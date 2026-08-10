"""
Abstract interface every database backend must implement.

Keeping one shared contract (ExpenseDB) means main.py never has to know
whether it's talking to SQLite, MySQL, PostgreSQL, or MongoDB -- it just
calls the same methods, and each backend translates them into the right
query language underneath.
"""

from abc import ABC, abstractmethod


class ExpenseDB(ABC):

    @abstractmethod
    def connect(self):
        """Open the connection/client."""
        raise NotImplementedError

    @abstractmethod
    def setup(self):
        """Create the table/collection if it doesn't already exist."""
        raise NotImplementedError

    @abstractmethod
    def add_expense(self, date, category, description, amount):
        """Insert a new expense. Returns the new record's id."""
        raise NotImplementedError

    @abstractmethod
    def view_expenses(self):
        """Return all expenses as a list of dicts, ordered by date."""
        raise NotImplementedError

    @abstractmethod
    def search_by_category(self, category):
        """Return expenses matching a category."""
        raise NotImplementedError

    @abstractmethod
    def update_expense(self, expense_id, date=None, category=None,
                        description=None, amount=None):
        """Update only the fields that are provided. Returns rows affected."""
        raise NotImplementedError

    @abstractmethod
    def delete_expense(self, expense_id):
        """Delete an expense by id. Returns rows affected."""
        raise NotImplementedError

    @abstractmethod
    def summary_by_category(self):
        """Return count/total/average grouped by category."""
        raise NotImplementedError

    @abstractmethod
    def highest_expense(self):
        """Return the single largest expense, or None if empty."""
        raise NotImplementedError

    @abstractmethod
    def filter_by_date_range(self, start_date, end_date):
        """Return expenses where start_date <= date <= end_date (YYYY-MM-DD)."""
        raise NotImplementedError

    @abstractmethod
    def filter_by_date_range(self, start_date, end_date):
        """Return expenses where start_date <= date <= end_date (YYYY-MM-DD)."""
        raise NotImplementedError

    @abstractmethod
    def monthly_spending_by_category(self, year, month):
        """Return spending grouped by category for a specific month."""
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """Close the connection/client cleanly."""
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """Close the connection/client cleanly."""
        raise NotImplementedError
