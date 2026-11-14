# API Specification

Base path: `/api/v1`  
All protected endpoints require a valid JWT bearer token.

## Authentication
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Log in |
| GET | `/auth/me` | Get current user |
| POST | `/auth/logout` | Log out / invalidate session according to implementation |

## Transactions
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/transactions` | Add transaction |
| GET | `/transactions` | List user's transactions |
| GET | `/transactions/:id` | Get one transaction |
| PUT | `/transactions/:id` | Edit transaction |
| DELETE | `/transactions/:id` | Delete transaction |

Transaction fields: description, amount, date, type, category. Type is `income` or `expense`.

## Budgets
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/budgets` | Create monthly budget |
| GET | `/budgets` | List/get budgets |
| PUT | `/budgets/:id` | Update budget |
| DELETE | `/budgets/:id` | Delete budget |
| GET | `/budgets/status` | Get budget usage |

## Dashboard and AI
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/dashboard/summary` | Income, expenses, balance |
| GET | `/analytics/category-breakdown` | Expense totals by category |
| GET | `/analytics/monthly-trends` | Monthly chart data |
| POST | `/ml/predict-category` | Predict expense category |
| GET | `/ml/forecast` | Estimate future expenses |
| GET | `/insights` | Get financial insights |
| POST | `/chat` | Ask about own finance data / app |

## Example transaction request
```json
{
  "description": "Uber ride",
  "amount": 300,
  "date": "2026-11-12",
  "type": "expense",
  "category": "Transport"
}
```

## Rules
- Validate all request data.
- Never accept a client-provided user ID as proof of ownership.
- Return only the signed-in user's data.
- Use clear error responses for invalid input, unauthorized access, and missing records.
