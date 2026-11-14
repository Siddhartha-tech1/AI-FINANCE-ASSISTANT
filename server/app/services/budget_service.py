"""Budget validation and server-side spending calculations."""

from datetime import datetime, timezone

from bson import ObjectId

from app.constants import EXPENSE_CATEGORIES


def valid_month(value):
    try:
        return isinstance(value, str) and datetime.strptime(value, "%Y-%m").strftime("%Y-%m") == value
    except ValueError:
        return False


def validate_budget(data):
    errors = {}
    if not valid_month(data.get("month")):
        errors["month"] = "Month must use YYYY-MM format."
    budget = data.get("total_budget")
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget < 0:
        errors["total_budget"] = "Total budget must be a non-negative number."
    limits = data.get("category_limits", {})
    if not isinstance(limits, dict):
        errors["category_limits"] = "Category limits must be an object."
    else:
        for category, amount in limits.items():
            if category not in EXPENSE_CATEGORIES or isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount < 0:
                errors["category_limits"] = "Category limits must use valid categories and non-negative amounts."
                break
    return errors


def budget_document(data):
    return {"month": data["month"], "total_budget": round(float(data["total_budget"]), 2), "category_limits": {key: round(float(value), 2) for key, value in data.get("category_limits", {}).items()}}


def serialize_budget(budget):
    return {"id": str(budget["_id"]), "month": budget["month"], "total_budget": budget["total_budget"], "category_limits": budget.get("category_limits", {})}


def spending_for_month(database, user_id, month):
    rows = database.transactions.aggregate([
        {"$match": {"user_id": ObjectId(user_id), "type": "expense", "date": {"$gte": f"{month}-01", "$lt": next_month(month)}}},
        {"$group": {"_id": "$category", "spent": {"$sum": "$amount"}}},
    ])
    return {row["_id"]: round(float(row["spent"]), 2) for row in rows}


def next_month(month):
    year, current_month = map(int, month.split("-"))
    return f"{year + 1:04d}-01" if current_month == 12 else f"{year:04d}-{current_month + 1:02d}-01"


def budget_status(database, user_id, month):
    budget = database.budgets.find_one({"user_id": ObjectId(user_id), "month": month})
    if budget is None:
        return None
    spending = spending_for_month(database, user_id, month)
    total_spent = round(sum(spending.values()), 2)
    total_budget = budget["total_budget"]
    categories = {category: {"limit": limit, "spent": spending.get(category, 0), "remaining": round(limit - spending.get(category, 0), 2), "percentage_used": round((spending.get(category, 0) / limit * 100) if limit else 0, 2)} for category, limit in budget.get("category_limits", {}).items()}
    return {"budget": serialize_budget(budget), "spent": total_spent, "remaining": round(total_budget - total_spent, 2), "percentage_used": round((total_spent / total_budget * 100) if total_budget else 0, 2), "categories": categories}
