"""Explainable forecast, insights, and rule-based finance chat."""

import math

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.database import get_database
from app.services.analytics_service import category_breakdown, monthly_trends, selected_month, totals
from app.services.budget_service import budget_status

assistant_bp = Blueprint("assistant", __name__, url_prefix="/api/v1")


@assistant_bp.get("/ml/forecast")
@jwt_required()
def forecast():
    month, database, user_id = selected_month(request.args.get("month")), get_database(current_app), get_jwt_identity()
    history = monthly_trends(database, user_id, month, 6)
    expenses = [row["expenses"] for row in history if row["expenses"] > 0]
    if len(expenses) < 3:
        return jsonify({"status": "insufficient_data", "message": "At least three months with recorded expenses are needed for an estimate."})
    positions = [[index] for index in range(len(expenses))]
    model = LinearRegression().fit(positions, expenses)
    estimate = round(max(0, float(model.predict([[len(expenses)]])[0])), 2)
    metrics = {"mae": None, "mse": None, "rmse": None, "r2": None}
    if len(expenses) >= 4:
        train_x, test_x = positions[:-1], positions[-1:]
        train_y, test_y = expenses[:-1], expenses[-1:]
        evaluation_model = LinearRegression().fit(train_x, train_y)
        predicted = evaluation_model.predict(test_x)
        metrics.update({
            "mae": round(float(mean_absolute_error(test_y, predicted)), 2),
            "mse": round(float(mean_squared_error(test_y, predicted)), 2),
            "rmse": round(math.sqrt(float(mean_squared_error(test_y, predicted))), 2),
        })
        # R2 needs at least two values in the holdout set; expose null otherwise.
        if len(test_y) >= 2:
            metrics["r2"] = round(float(r2_score(test_y, predicted)), 4)
    return jsonify({"status": "estimate", "next_month": estimate, "metrics": metrics, "basis": "Linear regression over recorded monthly expenses; this is an estimate, not a guarantee."})


@assistant_bp.get("/insights")
@jwt_required()
def insights():
    month, database, user_id = selected_month(request.args.get("month")), get_database(current_app), get_jwt_identity()
    summary, categories, status = totals(database, user_id, month), category_breakdown(database, user_id, month), budget_status(database, user_id, month)
    result = []
    if categories: result.append({"title": "Highest spending category", "message": f"{categories[0]['category']} is your highest expense category at ₹{categories[0]['amount']:.2f}."})
    if summary["expenses"] > summary["income"]: result.append({"title": "Expenses exceed income", "message": "Your recorded expenses are greater than your recorded income this month."})
    if status and status["percentage_used"] >= 100: result.append({"title": "Budget exceeded", "message": "You have exceeded your monthly budget."})
    elif status and status["percentage_used"] >= 80: result.append({"title": "Budget almost used", "message": f"You have used {status['percentage_used']:.0f}% of your monthly budget."})
    previous = monthly_trends(database, user_id, month, 2)
    if len(previous) == 2 and previous[0]["expenses"] > 0 and previous[1]["expenses"] > previous[0]["expenses"]:
        increase = round((previous[1]["expenses"] - previous[0]["expenses"]) / previous[0]["expenses"] * 100)
        result.append({"title": "Spending increased", "message": f"Your recorded expenses are {increase}% higher than last month."})
    return jsonify({"insights": result})


@assistant_bp.post("/chat")
@jwt_required()
def chat():
    message = (request.get_json(silent=True) or {}).get("message", "")
    if not isinstance(message, str) or not message.strip(): return jsonify({"error": "validation_error", "details": {"message": "Message is required."}}), 400
    month, database, user_id, text = selected_month(None), get_database(current_app), get_jwt_identity(), message.lower()
    if "spend" in text: answer = f"You spent ₹{totals(database, user_id, month)['expenses']:.2f} this month."
    elif "most" in text or "highest" in text:
        categories = category_breakdown(database, user_id, month); answer = f"Your highest category is {categories[0]['category']} at ₹{categories[0]['amount']:.2f}." if categories else "You have no expense data this month."
    elif "budget" in text:
        status = budget_status(database, user_id, month); answer = f"You have ₹{status['remaining']:.2f} remaining." if status else "You have not created a budget for this month."
    else: answer = "I can help with this month's spending, highest category, or remaining budget."
    return jsonify({"answer": answer})
