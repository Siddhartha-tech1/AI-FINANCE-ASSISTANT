from types import SimpleNamespace

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app import create_app


def matches(document, query):
    return all(document.get(key) == value for key, value in query.items())


class MemoryUsers:
    def __init__(self):
        self.records = []

    def insert_one(self, document):
        if self.find_one({"email": document["email"]}):
            raise DuplicateKeyError("duplicate")
        document = {**document, "_id": ObjectId()}
        self.records.append(document)
        return SimpleNamespace(inserted_id=document["_id"])

    def find_one(self, query):
        return next((record for record in self.records if matches(record, query)), None)


class Cursor(list):
    def sort(self, field, direction):
        return Cursor(sorted(self, key=lambda item: item[field], reverse=direction < 0))


class MemoryTransactions:
    def __init__(self):
        self.records = []

    def insert_one(self, document):
        document = {**document, "_id": ObjectId()}
        self.records.append(document)
        return SimpleNamespace(inserted_id=document["_id"])

    def find_one(self, query):
        return next((record for record in self.records if matches(record, query)), None)

    def find(self, query):
        return Cursor(record for record in self.records if matches(record, query))

    def update_one(self, query, update):
        record = self.find_one(query)
        if record:
            record.update(update["$set"])

    def delete_one(self, query):
        record = self.find_one(query)
        if record:
            self.records.remove(record)
            return SimpleNamespace(deleted_count=1)
        return SimpleNamespace(deleted_count=0)


class MemoryDatabase:
    def __init__(self):
        self.users = MemoryUsers()
        self.transactions = MemoryTransactions()


def register(client, name, email):
    response = client.post("/api/v1/auth/register", json={"name": name, "email": email, "password": "safe-password"})
    return {"Authorization": f"Bearer {response.json['access_token']}"}


def test_transactions_are_validated_and_scoped_to_current_user():
    app = create_app({"TESTING": True, "JWT_SECRET_KEY": "test-secret-key-with-at-least-32-chars"})
    database = MemoryDatabase()
    app.extensions["mongo_db"] = database
    client = app.test_client()
    alice = register(client, "Alice", "alice@example.com")
    bob = register(client, "Bob", "bob@example.com")

    invalid = client.post("/api/v1/transactions", headers=alice, json={"amount": -1})
    assert invalid.status_code == 400

    untrusted_user_id = str(ObjectId())
    created = client.post(
        "/api/v1/transactions",
        headers=alice,
        json={
            "description": "Lunch",
            "amount": 250,
            "date": "2026-11-14",
            "type": "expense",
            "category": "Food",
            "user_id": untrusted_user_id,
        },
    )
    assert created.status_code == 201
    transaction_id = created.json["transaction"]["id"]

    assert client.get(f"/api/v1/transactions/{transaction_id}", headers=bob).status_code == 404
    assert client.put(f"/api/v1/transactions/{transaction_id}", headers=bob, json={"description": "Changed", "amount": 1, "date": "2026-11-14", "type": "expense", "category": "Food"}).status_code == 404

    listing = client.get("/api/v1/transactions", headers=alice)
    assert listing.status_code == 200
    assert listing.json["transactions"][0]["description"] == "Lunch"
    assert database.transactions.records[0]["user_id"] != ObjectId(untrusted_user_id)

    assert client.delete(f"/api/v1/transactions/{transaction_id}", headers=alice).status_code == 204
