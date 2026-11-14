"""Authentication business logic and safe user serialization."""

from datetime import datetime, timezone

import bcrypt
from bson import ObjectId


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def password_matches(password, password_hash):
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_user(database, name, email, password):
    result = database.users.insert_one(
        {
            "name": name.strip(),
            "email": email.strip().lower(),
            "password_hash": hash_password(password),
            "created_at": datetime.now(timezone.utc),
        }
    )
    return database.users.find_one({"_id": result.inserted_id})


def serialize_user(user):
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "created_at": user["created_at"].isoformat(),
    }


def find_user_by_id(database, user_id):
    try:
        return database.users.find_one({"_id": ObjectId(user_id)})
    except (TypeError, ValueError):
        return None
