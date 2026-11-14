"""Authenticated dashboard and analytics endpoints."""

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.database import get_database
from app.services.analytics_service import category_breakdown, dashboard_summary, monthly_trends, selected_month
from app.services.budget_service import valid_month

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/v1/dashboard")
analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/v1/analytics")


def requested_month():
    month = request.args.get("month")
    if month and not valid_month(month):
        return None
    return selected_month(month)


@dashboard_bp.get("/summary")
@jwt_required()
def summary():
    month = requested_month()
    if month is None: return jsonify({"error": "validation_error", "details": {"month": "Month must use YYYY-MM format."}}), 400
    return jsonify(dashboard_summary(get_database(current_app), get_jwt_identity(), month))


@analytics_bp.get("/category-breakdown")
@jwt_required()
def categories():
    month = requested_month()
    if month is None: return jsonify({"error": "validation_error", "details": {"month": "Month must use YYYY-MM format."}}), 400
    return jsonify({"month": month, "categories": category_breakdown(get_database(current_app), get_jwt_identity(), month)})


@analytics_bp.get("/monthly-trends")
@jwt_required()
def trends():
    month = requested_month()
    try: count = min(max(int(request.args.get("months", 6)), 1), 24)
    except ValueError: return jsonify({"error": "validation_error", "details": {"months": "Months must be a number."}}), 400
    if month is None: return jsonify({"error": "validation_error", "details": {"month": "Month must use YYYY-MM format."}}), 400
    return jsonify({"trends": monthly_trends(get_database(current_app), get_jwt_identity(), month, count)})
