"""
MongoDB backend. Requires a running MongoDB server (see README).
Stores each expense as a document instead of a row -- no fixed schema,
no CREATE TABLE step, and querying uses Mongo's filter-dict syntax
instead of SQL WHERE clauses.
"""

from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from db.base import ExpenseDB


class MongoExpenseDB(ExpenseDB):

    def __init__(self, uri, database, collection="expenses"):
        self.uri = uri
        self.database_name = database
        self.collection_name = collection
        self.client = None
        self.collection = None

    def connect(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")  # fail fast if server is unreachable
            db = self.client[self.database_name]
            self.collection = db[self.collection_name]
            return self.client
        except PyMongoError as e:
            raise ConnectionError(f"Could not connect to MongoDB: {e}")

    def setup(self):
        # Collections are created lazily on first insert in MongoDB --
        # nothing to do here, but an index helps category/date queries.
        self.collection.create_index("category")
        self.collection.create_index("date")

    @staticmethod
    def _to_dict(doc):
        if doc is None:
            return None
        doc = dict(doc)
        doc["id"] = str(doc.pop("_id"))
        return doc

    def add_expense(self, date, category, description, amount):
        try:
            result = self.collection.insert_one({
                "date": date,
                "category": category,
                "description": description,
                "amount": float(amount),
            })
            return str(result.inserted_id)
        except PyMongoError as e:
            raise RuntimeError(f"Insert failed: {e}")

    def view_expenses(self):
        docs = self.collection.find().sort("date", ASCENDING)
        return [self._to_dict(d) for d in docs]

    def search_by_category(self, category):
        docs = self.collection.find({"category": category}).sort("date", ASCENDING)
        return [self._to_dict(d) for d in docs]

    def update_expense(self, expense_id, date=None, category=None,
                        description=None, amount=None):
        updates = {}
        if date is not None:
            updates["date"] = date
        if category is not None:
            updates["category"] = category
        if description is not None:
            updates["description"] = description
        if amount is not None:
            updates["amount"] = float(amount)
        if not updates:
            return 0
        result = self.collection.update_one(
            {"_id": ObjectId(expense_id)}, {"$set": updates}
        )
        return result.modified_count

    def delete_expense(self, expense_id):
        result = self.collection.delete_one({"_id": ObjectId(expense_id)})
        return result.deleted_count

    def summary_by_category(self):
        pipeline = [
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "total": {"$sum": "$amount"},
                "average": {"$avg": "$amount"},
            }},
            {"$sort": {"total": -1}},
        ]
        results = list(self.collection.aggregate(pipeline))
        return [
            {"category": r["_id"], "count": r["count"],
             "total": r["total"], "average": r["average"]}
            for r in results
        ]

    def highest_expense(self):
        doc = self.collection.find_one(sort=[("amount", DESCENDING)])
        return self._to_dict(doc)

    def filter_by_date_range(self, start_date, end_date):
        docs = self.collection.find(
            {"date": {"$gte": start_date, "$lte": end_date}}
        ).sort("date", ASCENDING)
        return [self._to_dict(d) for d in docs]

    def monthly_spending_by_category(self, year, month):
        prefix = f"{year}-{int(month):02d}"

        pipeline = [
            {
                "$match": {
                    "date": {
                        "$regex": f"^{prefix}-"
                    }
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "total": {"$sum": "$amount"},
                    "average": {"$avg": "$amount"}
                }
            },
            {
                "$sort": {"total": -1}
            }
        ]

        rows = list(self.collection.aggregate(pipeline))

        return [
            {
                "category": row["_id"],
                "count": row["count"],
                "total": row["total"],
                "average": row["average"]
            }
            for row in rows
        ]
    
    def close(self):
        if self.client:
            self.client.close()
