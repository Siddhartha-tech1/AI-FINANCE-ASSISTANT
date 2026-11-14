"""Authenticated budget endpoints."""

from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pymongo.errors import DuplicateKeyError

from app.database import get_database
from app.services.budget_service import budget_document, budget_status, serialize_budget, valid_month, validate_budget
from app.services.transaction_service import object_id_or_none

budgets_bp = Blueprint("budgets", __name__, url_prefix="/api/v1/budgets")


@budgets_bp.post("")
@jwt_required()
def create_budget():
    data = request.get_json(silent=True) or {}
    errors = validate_budget(data)
    if errors: return jsonify({"error": "validation_error", "details": errors}), 400
    document = budget_document(data) | {"user_id": object_id_or_none(get_jwt_identity())}
    try:
        result = get_database(current_app).budgets.insert_one(document)
    except DuplicateKeyError:
        return jsonify({"error": "budget_exists", "message": "A budget already exists for this month."}), 409
    return jsonify({"budget": serialize_budget(get_database(current_app).budgets.find_one({"_id": result.inserted_id, "user_id": document["user_id"]}))}), 201


@budgets_bp.get("")
@jwt_required()
def list_budgets():
    budgets = get_database(current_app).budgets.find({"user_id": object_id_or_none(get_jwt_identity())}).sort("month", -1)
    return jsonify({"budgets": [serialize_budget(item) for item in budgets]})


@budgets_bp.get("/status")
@jwt_required()
def get_budget_status():
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    if not valid_month(month): return jsonify({"error": "validation_error", "details": {"month": "Month must use YYYY-MM format."}}), 400
    status = budget_status(get_database(current_app), get_jwt_identity(), month)
    if status is None: return jsonify({"error": "not_found", "message": "No budget exists for this month."}), 404
    return jsonify(status)


@budgets_bp.put("/<budget_id>")
@jwt_required()
def update_budget(budget_id):
    data, record_id = request.get_json(silent=True) or {}, object_id_or_none(budget_id)
    errors = validate_budget(data)
    if record_id is None or errors: return jsonify({"error": "validation_error", "details": errors}), 400
    database, query = get_database(current_app), {"_id": record_id, "user_id": object_id_or_none(get_jwt_identity())}
    database.budgets.update_one(query, {"$set": budget_document(data)})
    result = database.budgets.find_one(query)
    return (jsonify({"budget": serialize_budget(result)}), 200) if result else (jsonify({"error": "not_found"}), 404)


@budgets_bp.delete("/<budget_id>")
@jwt_required()
def delete_budget(budget_id):
    record_id = object_id_or_none(budget_id)
    result = get_database(current_app).budgets.delete_one({"_id": record_id, "user_id": object_id_or_none(get_jwt_identity())}) if record_id else None
    return ("", 204) if result and result.deleted_count else (jsonify({"error": "not_found"}), 404)
