"""Application factory for the AI Finance Assistant API."""

import os

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

from app.database import init_mongodb
from app.routes.auth import auth_bp
from app.routes.transactions import transactions_bp
from app.routes.budgets import budgets_bp
from app.routes.analytics import analytics_bp, dashboard_bp
from app.routes.ml import ml_bp
from app.routes.assistant import assistant_bp


def create_app(test_config=None):
    """Create and configure the Flask application."""
    load_dotenv()

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),
        MONGODB_URI=os.environ.get("MONGODB_URI"),
        MONGODB_DB_NAME=os.environ.get("MONGODB_DB_NAME", "ai_finance_assistant"),
    )

    if test_config:
        app.config.update(test_config)
        if app.config.get("TESTING") and "MONGODB_URI" not in test_config:
            app.config["MONGODB_URI"] = None

    allowed_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
    JWTManager(app)
    init_mongodb(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(assistant_bp)

    @app.get("/api/v1/health")
    def health_check():
        return jsonify({"status": "ok", "service": "ai-finance-assistant-api"})

    return app
