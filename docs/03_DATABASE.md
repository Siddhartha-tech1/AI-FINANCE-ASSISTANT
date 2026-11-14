# MongoDB Database Design

Database name: `ai_finance_assistant`

Use these five collections.

## 1. users
```json
{
  "_id": "ObjectId",
  "name": "Sample User",
  "email": "user@example.com",
  "password_hash": "bcrypt-hash",
  "created_at": "ISO date"
}
```
Email must be unique. Never store a plain-text password.

## 2. transactions
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "description": "Swiggy dinner",
  "amount": 450,
  "date": "2026-11-12",
  "type": "expense",
  "category": "Food",
  "predicted_category": "Food"
}
```
`type` is `income` or `expense`. Amount is a positive number. Categories: Food, Transport, Shopping, Bills, Entertainment, Health, Education, Other.

## 3. budgets
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "month": "2026-11",
  "total_budget": 15000,
  "category_limits": {
    "Food": 4000,
    "Transport": 2000
  }
}
```
Allow one budget per user per month.

## 4. predictions
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "transaction_id": "ObjectId",
  "predicted_category": "Food",
  "confidence": 0.91,
  "created_at": "ISO date"
}
```

## 5. insights
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "title": "Food budget warning",
  "message": "You have used 85% of your Food budget.",
  "created_at": "ISO date"
}
```

## Important rules
- Every user's record must contain `user_id`.
- Get `user_id` from the verified login token, not from the frontend request.
- Filter reads, updates, and deletes by both document ID and authenticated user ID.
- Add indexes for `users.email`, `transactions.user_id + date`, and `budgets.user_id + month`.
