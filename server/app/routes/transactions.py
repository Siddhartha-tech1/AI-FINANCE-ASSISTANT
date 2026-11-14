"""Authenticated transaction endpoints."""

from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.database import get_database
from app.services.transaction_service import (
    object_id_or_none,
    serialize_transaction,
    transaction_document,
    transaction_filter,
    validate_transaction,
)

transactions_bp = Blueprint("transactions", __name__, url_prefix="/api/v1/transactions")


def request_data():
    return request.get_json(silent=True) or {}


@transactions_bp.post("")
@jwt_required()
def create_transaction():
    data = request_data()
    errors = validate_transaction(data)
    if errors:
        return jsonify({"error": "validation_error", "details": errors}), 400

    document = transaction_document(data)
    document["user_id"] = object_id_or_none(get_jwt_identity())
    database = get_database(current_app)
    result = database.transactions.insert_one(document)
    if document.get("predicted_category") and document["predicted_category"] != document["category"]:
        database.predictions.insert_one({
            "user_id": document["user_id"],
            "transaction_id": result.inserted_id,
            "description": document["description"],
            "predicted_category": document["predicted_category"],
            "corrected_category": document["category"],
            "created_at": datetime.now(timezone.utc),
        })
    created = database.transactions.find_one({"_id": result.inserted_id, "user_id": document["user_id"]})
    return jsonify({"transaction": serialize_transaction(created)}), 201


@transactions_bp.get("")
@jwt_required()
def list_transactions():
    database = get_database(current_app)
    query = transaction_filter(get_jwt_identity(), request.args)
    transactions = database.transactions.find(query).sort("date", -1)
    return jsonify({"transactions": [serialize_transaction(item) for item in transactions]})


@transactions_bp.get("/<transaction_id>")
@jwt_required()
def get_transaction(transaction_id):
    record_id = object_id_or_none(transaction_id)
    if record_id is None:
        return jsonify({"error": "not_found"}), 404
    transaction = get_database(current_app).transactions.find_one(
        {"_id": record_id, "user_id": object_id_or_none(get_jwt_identity())}
    )
    if transaction is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"transaction": serialize_transaction(transaction)})


@transactions_bp.put("/<transaction_id>")
@jwt_required()
def update_transaction(transaction_id):
    record_id = object_id_or_none(transaction_id)
    data = request_data()
    errors = validate_transaction(data)
    if record_id is None or errors:
        return jsonify({"error": "validation_error", "details": errors}), 400

    database = get_database(current_app)
    query = {"_id": record_id, "user_id": object_id_or_none(get_jwt_identity())}
    database.transactions.update_one(query, {"$set": transaction_document(data)})
    transaction = database.transactions.find_one(query)
    if transaction is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"transaction": serialize_transaction(transaction)})


@transactions_bp.delete("/<transaction_id>")
@jwt_required()
def delete_transaction(transaction_id):
    record_id = object_id_or_none(transaction_id)
    if record_id is None:
        return jsonify({"error": "not_found"}), 404
    result = get_database(current_app).transactions.delete_one(
        {"_id": record_id, "user_id": object_id_or_none(get_jwt_identity())}
    )
    if result.deleted_count == 0:
        return jsonify({"error": "not_found"}), 404
    return "", 204
