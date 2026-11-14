"""ML-assisted category prediction endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ml.predict import predict_category

ml_bp = Blueprint("ml", __name__, url_prefix="/api/v1/ml")


@ml_bp.post("/predict-category")
@jwt_required()
def predict_expense_category():
    data = request.get_json(silent=True) or {}
    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        return jsonify({"error": "validation_error", "details": {"description": "Description is required."}}), 400
    prediction = predict_category(description.strip())
    if prediction is None:
        return jsonify({"error": "model_unavailable", "message": "Category model is not trained. Select a category manually."}), 503
    return jsonify(prediction)
