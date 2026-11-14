# Technical Overview

## Technology
| Part | Technology |
|---|---|
| Frontend | React + Vite |
| Styling | Tailwind CSS |
| Backend | Python Flask |
| Database | MongoDB Atlas |
| MongoDB library | PyMongo |
| Authentication | JWT + bcrypt |
| Machine Learning | scikit-learn |
| Data handling | pandas, NumPy |
| Model saving | joblib |
| Charts | Recharts |
| API testing | Postman |
| Coding assistant | Codex |

## Simple architecture
React frontend -> Flask API -> MongoDB

The Flask backend also calls Python ML functions for expense categorization and spending estimates. A separate ML server is not needed.

## Suggested folders
```text
AI-Finance-Assistant/
  AGENTS.md
  README.md
  docs/
    00_START_HERE.md
    01_PRD.md
    02_TECHNICAL_OVERVIEW.md
    03_DATABASE.md
    04_API_SPEC.md
    05_UI_SPEC.md
    06_ML_FEATURES.md
    08_DEVELOPMENT_STEPS.md
  client/
    src/
      components/
      pages/
      services/
      context/
  server/
    app/
      routes/
      services/
      models/
    ml/
      datasets/
      train_classifier.py
      predict.py
      train_forecast.py
    tests/
    run.py
    requirements.txt
    .env.example
```

## Coding rules
- Keep frontend and backend separate.
- Keep Flask routes, business logic, and database access in separate files.
- Keep ML training code separate from API routes.
- Use environment variables for secrets.
- Use the authenticated user's ID for every personal-data query.
- Calculate financial totals on the backend.
- Add tests as each feature is completed.
