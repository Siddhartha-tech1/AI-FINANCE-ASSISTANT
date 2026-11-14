"""Authentication HTTP endpoints."""

import re

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from pymongo.errors import DuplicateKeyError

from app.database import get_database
from app.services.auth_service import (
    create_user,
    find_user_by_id,
    password_matches,
    serialize_user,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def payload():
    return request.get_json(silent=True) or {}


def registration_errors(data):
    errors = {}
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        errors["name"] = "Name is required."
    if not isinstance(data.get("email"), str) or not EMAIL_PATTERN.match(data["email"].strip()):
        errors["email"] = "A valid email address is required."
    if not isinstance(data.get("password"), str) or len(data["password"]) < 8:
        errors["password"] = "Password must be at least 8 characters."
    return errors


@auth_bp.post("/register")
def register():
    data = payload()
    errors = registration_errors(data)
    if errors:
        return jsonify({"error": "validation_error", "details": errors}), 400

    try:
        user = create_user(get_database(current_app), data["name"], data["email"], data["password"])
    except DuplicateKeyError:
        return jsonify({"error": "email_taken", "message": "An account with this email already exists."}), 409

    return jsonify({"user": serialize_user(user), "access_token": create_access_token(str(user["_id"]))}), 201


@auth_bp.post("/login")
def login():
    data = payload()
    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "validation_error", "message": "Email and password are required."}), 400

    user = get_database(current_app).users.find_one({"email": email.strip().lower()})
    if user is None or not password_matches(password, user["password_hash"]):
        return jsonify({"error": "invalid_credentials", "message": "Email or password is incorrect."}), 401

    return jsonify({"user": serialize_user(user), "access_token": create_access_token(str(user["_id"]))})


@auth_bp.get("/me")
@jwt_required()
def current_user():
    user = find_user_by_id(get_database(current_app), get_jwt_identity())
    if user is None:
        return jsonify({"error": "user_not_found"}), 404
    return jsonify({"user": serialize_user(user)})


@auth_bp.post("/logout")
@jwt_required()
def logout():
    return jsonify({"message": "Logged out. Remove the access token on the client."})
