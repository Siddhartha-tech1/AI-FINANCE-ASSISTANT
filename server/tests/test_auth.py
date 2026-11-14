from types import SimpleNamespace

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app import create_app


class MemoryUsers:
    def __init__(self):
        self.records = []

    def insert_one(self, document):
        if self.find_one({"email": document["email"]}):
            raise DuplicateKeyError("duplicate email")
        document = {**document, "_id": ObjectId()}
        self.records.append(document)
        return SimpleNamespace(inserted_id=document["_id"])

    def find_one(self, query):
        return next((record for record in self.records if all(record.get(key) == value for key, value in query.items())), None)


class MemoryDatabase:
    def __init__(self):
        self.users = MemoryUsers()


def test_register_login_and_current_user_flow():
    app = create_app({"TESTING": True, "JWT_SECRET_KEY": "test-secret-key-with-at-least-32-chars"})
    app.extensions["mongo_db"] = MemoryDatabase()
    client = app.test_client()

    registration = client.post("/api/v1/auth/register", json={"name": "Asha", "email": "ASHA@example.com", "password": "secure-pass"})
    assert registration.status_code == 201
    assert registration.json["user"]["email"] == "asha@example.com"
    assert "password_hash" not in registration.json["user"]

    duplicate = client.post("/api/v1/auth/register", json={"name": "Asha", "email": "asha@example.com", "password": "secure-pass"})
    assert duplicate.status_code == 409

    login = client.post("/api/v1/auth/login", json={"email": "asha@example.com", "password": "secure-pass"})
    assert login.status_code == 200

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {login.json['access_token']}"})
    assert me.status_code == 200
    assert me.json["user"]["name"] == "Asha"


def test_auth_rejects_invalid_credentials_and_missing_token():
    app = create_app({"TESTING": True, "JWT_SECRET_KEY": "test-secret-key-with-at-least-32-chars"})
    app.extensions["mongo_db"] = MemoryDatabase()
    client = app.test_client()

    assert client.post("/api/v1/auth/login", json={"email": "nobody@example.com", "password": "wrong"}).status_code == 401
    assert client.get("/api/v1/auth/me").status_code == 401
