"""MongoDB setup and collection indexes."""

from pymongo import ASCENDING, MongoClient


def create_required_indexes(database):
    """Create the indexes defined in the database specification."""
    database.users.create_index([("email", ASCENDING)], unique=True, name="users_email_unique")
    database.transactions.create_index(
        [("user_id", ASCENDING), ("date", ASCENDING)],
        name="transactions_user_date",
    )
    database.budgets.create_index(
        [("user_id", ASCENDING), ("month", ASCENDING)],
        unique=True,
        name="budgets_user_month_unique",
    )
    database.predictions.create_index(
        [("user_id", ASCENDING), ("transaction_id", ASCENDING)],
        name="predictions_user_transaction",
    )
    database.insights.create_index(
        [("user_id", ASCENDING), ("created_at", ASCENDING)],
        name="insights_user_created_at",
    )


def init_mongodb(app):
    """Attach a configured Mongo database to the Flask app, when available."""
    uri = app.config.get("MONGODB_URI")
    if not uri:
        return

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    database = client[app.config["MONGODB_DB_NAME"]]
    create_required_indexes(database)
    app.extensions["mongo_client"] = client
    app.extensions["mongo_db"] = database


def get_database(app):
    """Return the configured database or raise a clear setup error."""
    database = app.extensions.get("mongo_db")
    if database is None:
        raise RuntimeError("MongoDB is not configured. Set MONGODB_URI before using data routes.")
    return database
