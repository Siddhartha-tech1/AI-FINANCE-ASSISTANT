from bson import ObjectId

from app.services.budget_service import budget_status, validate_budget


class Transactions:
    def aggregate(self, pipeline):
        return [{"_id": "Food", "spent": 750}, {"_id": "Transport", "spent": 100}]


class Budgets:
    def __init__(self, user_id):
        self.user_id = user_id

    def find_one(self, query):
        if query["user_id"] == self.user_id and query["month"] == "2026-11":
            return {"_id": ObjectId(), "user_id": self.user_id, "month": "2026-11", "total_budget": 1000, "category_limits": {"Food": 800}}
        return None


class Database:
    def __init__(self, user_id):
        self.transactions = Transactions()
        self.budgets = Budgets(user_id)


def test_budget_status_is_calculated_server_side():
    user_id = ObjectId()
    status = budget_status(Database(user_id), str(user_id), "2026-11")

    assert status["spent"] == 850
    assert status["remaining"] == 150
    assert status["percentage_used"] == 85
    assert status["categories"]["Food"]["remaining"] == 50


def test_budget_validation_rejects_invalid_category_limit():
    errors = validate_budget({"month": "2026-11", "total_budget": 1000, "category_limits": {"Invalid": 100}})
    assert "category_limits" in errors
