"""Transaction validation, persistence, and safe serialization."""

from datetime import date
from re import escape

from bson import ObjectId

from app.constants import TRANSACTION_CATEGORIES, TRANSACTION_TYPES, VALID_CATEGORIES_BY_TYPE


def validate_transaction(data):
    errors = {}
    if not isinstance(data.get("description"), str) or not data["description"].strip():
        errors["description"] = "Description is required."

    amount = data.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount <= 0:
        errors["amount"] = "Amount must be a positive number."

    if data.get("type") not in TRANSACTION_TYPES:
        errors["type"] = "Type must be income or expense."
    transaction_type = data.get("type")
    if transaction_type in TRANSACTION_TYPES and data.get("category") not in VALID_CATEGORIES_BY_TYPE[transaction_type]:
        errors["category"] = f"Category is not supported for {transaction_type} transactions."
    elif transaction_type not in TRANSACTION_TYPES and data.get("category") not in TRANSACTION_CATEGORIES:
        errors["category"] = "Category is not supported."

    transaction_date = data.get("date")
    if not isinstance(transaction_date, str):
        errors["date"] = "Date must use YYYY-MM-DD format."
    else:
        try:
            date.fromisoformat(transaction_date)
        except ValueError:
            errors["date"] = "Date must use YYYY-MM-DD format."
    return errors


def transaction_document(data):
    document = {
        "description": data["description"].strip(),
        "amount": round(float(data["amount"]), 2),
        "date": data["date"],
        "type": data["type"],
        "category": data["category"],
    }
    # The suggested category is retained for transparency, while `category`
    # remains the user's final, editable choice.
    if data.get("predicted_category") in TRANSACTION_CATEGORIES:
        document["predicted_category"] = data["predicted_category"]
    return document


def serialize_transaction(transaction):
    result = {key: value for key, value in transaction.items() if key not in {"_id", "user_id"}}
    result["id"] = str(transaction["_id"])
    return result


def transaction_filter(user_id, filters):
    query = {"user_id": ObjectId(user_id)}
    if filters.get("type") in TRANSACTION_TYPES:
        query["type"] = filters["type"]
    if filters.get("category") in TRANSACTION_CATEGORIES:
        query["category"] = filters["category"]
    if filters.get("date_from") or filters.get("date_to"):
        date_query = {}
        if filters.get("date_from"):
            date_query["$gte"] = filters["date_from"]
        if filters.get("date_to"):
            date_query["$lte"] = filters["date_to"]
        query["date"] = date_query
    if filters.get("search"):
        query["description"] = {"$regex": escape(filters["search"]), "$options": "i"}
    return query


def object_id_or_none(value):
    try:
        return ObjectId(value)
    except (TypeError, ValueError):
        return None
