"""Server-verified dashboard and analytics calculations."""

from datetime import datetime

from bson import ObjectId

from app.services.budget_service import budget_status, next_month, valid_month


def selected_month(value):
    return value if valid_month(value) else datetime.now().strftime("%Y-%m")


def month_match(user_id, month):
    return {"user_id": ObjectId(user_id), "date": {"$gte": f"{month}-01", "$lt": next_month(month)}}


def totals(database, user_id, month):
    rows = database.transactions.aggregate([
        {"$match": month_match(user_id, month)},
        {"$group": {"_id": "$type", "total": {"$sum": "$amount"}}},
    ])
    values = {row["_id"]: round(float(row["total"]), 2) for row in rows}
    income, expenses = values.get("income", 0), values.get("expense", 0)
    return {"income": income, "expenses": expenses, "balance": round(income - expenses, 2)}


def category_breakdown(database, user_id, month):
    rows = database.transactions.aggregate([
        {"$match": month_match(user_id, month) | {"type": "expense"}},
        {"$group": {"_id": "$category", "amount": {"$sum": "$amount"}}},
        {"$sort": {"amount": -1}},
    ])
    return [{"category": row["_id"], "amount": round(float(row["amount"]), 2)} for row in rows]


def month_range(end_month, count):
    result, month = [], end_month
    for _ in range(count):
        result.append(month)
        year, current = map(int, month.split("-"))
        month = f"{year - 1:04d}-12" if current == 1 else f"{year:04d}-{current - 1:02d}"
    return list(reversed(result))


def monthly_trends(database, user_id, end_month, count=6):
    months = month_range(end_month, count)
    rows = database.transactions.aggregate([
        {"$match": {"user_id": ObjectId(user_id), "date": {"$gte": f"{months[0]}-01", "$lt": next_month(end_month)}}},
        {"$group": {"_id": {"month": {"$substr": ["$date", 0, 7]}, "type": "$type"}, "amount": {"$sum": "$amount"}}},
    ])
    values = {(row["_id"]["month"], row["_id"]["type"]): round(float(row["amount"]), 2) for row in rows}
    return [{"month": month, "income": values.get((month, "income"), 0), "expenses": values.get((month, "expense"), 0)} for month in months]


def dashboard_summary(database, user_id, month):
    summary = totals(database, user_id, month)
    status = budget_status(database, user_id, month)
    summary.update({"month": month, "budget_remaining": status["remaining"] if status else None, "budget_percentage_used": status["percentage_used"] if status else None})
    return summary
