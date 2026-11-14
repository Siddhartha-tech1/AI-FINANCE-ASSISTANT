from bson import ObjectId

from app.services.analytics_service import category_breakdown, monthly_trends, totals


class Transactions:
    def aggregate(self, pipeline):
        group_id = next(stage["$group"]["_id"] for stage in pipeline if "$group" in stage)
        if group_id == "$type":
            return [{"_id": "income", "total": 1000}, {"_id": "expense", "total": 325}]
        if group_id == "$category":
            return [{"_id": "Food", "amount": 200}, {"_id": "Transport", "amount": 125}]
        return [{"_id": {"month": "2026-10", "type": "income"}, "amount": 1000}, {"_id": {"month": "2026-11", "type": "expense"}, "amount": 325}]


class Database:
    transactions = Transactions()


def test_dashboard_calculations_are_based_on_aggregated_transactions():
    user_id, database = str(ObjectId()), Database()
    assert totals(database, user_id, "2026-11") == {"income": 1000.0, "expenses": 325.0, "balance": 675.0}
    assert category_breakdown(database, user_id, "2026-11")[0] == {"category": "Food", "amount": 200.0}
    trends = monthly_trends(database, user_id, "2026-11", 2)
    assert trends == [{"month": "2026-10", "income": 1000.0, "expenses": 0}, {"month": "2026-11", "income": 0, "expenses": 325.0}]
