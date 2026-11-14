EXPENSE_CATEGORIES = {
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Other",
}

INCOME_CATEGORIES = {
    "Salary",
    "Freelance",
    "Business",
    "Investment",
    "Gift",
    "Other Income",
}

TRANSACTION_CATEGORIES = EXPENSE_CATEGORIES | INCOME_CATEGORIES
VALID_CATEGORIES_BY_TYPE = {
    "expense": EXPENSE_CATEGORIES,
    "income": INCOME_CATEGORIES,
}

TRANSACTION_TYPES = {"income", "expense"}
