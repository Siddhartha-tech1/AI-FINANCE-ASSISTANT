from app import create_app


class FakeCollection:
    def __init__(self):
        self.indexes = []

    def create_index(self, keys, **options):
        self.indexes.append((keys, options))


class FakeDatabase:
    def __init__(self):
        self.users = FakeCollection()
        self.transactions = FakeCollection()
        self.budgets = FakeCollection()
        self.predictions = FakeCollection()
        self.insights = FakeCollection()


class FakeClient:
    def __init__(self, *args, **kwargs):
        self.database = FakeDatabase()

    def __getitem__(self, name):
        return self.database


def test_configured_database_creates_required_indexes(monkeypatch):
    monkeypatch.setattr("app.database.MongoClient", FakeClient)

    app = create_app({"MONGODB_URI": "mongodb://example.test", "MONGODB_DB_NAME": "test_db"})
    database = app.extensions["mongo_db"]

    assert database.users.indexes[0][1]["unique"] is True
    assert database.transactions.indexes[0][0] == [("user_id", 1), ("date", 1)]
    assert database.budgets.indexes[0][1]["unique"] is True
    assert database.predictions.indexes[0][0] == [("user_id", 1), ("transaction_id", 1)]
    assert database.insights.indexes[0][0] == [("user_id", 1), ("created_at", 1)]
