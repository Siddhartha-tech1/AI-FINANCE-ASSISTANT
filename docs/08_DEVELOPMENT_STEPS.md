# Development Steps

Build the application in this order. Finish and test one step before starting the next.

## Step 1 — Basic setup
- Create React/Vite frontend.
- Create Flask backend.
- Add folder structure and environment examples.
- Add a simple health endpoint.
Done when both apps start locally.

## Step 2 — MongoDB
- Connect Flask to MongoDB Atlas.
- Create the five collections as needed.
- Add indexes.
Done when the backend can connect and perform a test read/write.

## Step 3 — Authentication
- Register, login, logout.
- Hash passwords with bcrypt.
- Protect backend routes with JWT.
Done when protected routes reject unauthenticated requests.

## Step 4 — Transactions
- Add, list, edit, delete.
- Search and filter.
- Enforce user ownership.
Done when CRUD works for two separate test users without data crossing.

## Step 5 — Budgets
- Create monthly budget.
- Add category limits.
- Calculate spent, remaining, and percentage used.
Done when values match manually checked examples.

## Step 6 — Dashboard
- KPI cards.
- Income/expense chart.
- Category breakdown chart.
- Recent transactions.
Done when all displayed figures come from MongoDB and match test data.

## Step 7 — ML categorization
- Prepare dataset.
- Train and evaluate classifier.
- Save model.
- Add prediction API and connect transaction form.
Done when prediction works and user can correct it.

## Step 8 — Forecast and insights
- Add monthly spending estimate.
- Add rule-based insights.
Done when insufficient history is handled correctly and insights have a clear calculation basis.

## Step 9 — Chatbot
- Answer a small set of finance questions using the signed-in user's data.
Done when answers match database calculations and cannot access another user's data.

## Step 10 — Final checks
- Test registration and login.
- Test transaction CRUD.
- Test budget calculations.
- Check dashboard totals.
- Test ML predictions and insufficient-data behavior.
- Check user data isolation.
- Run frontend production build and backend tests.

Do not start with visual polish before the main data flow works. Apply the screenshot-inspired styling while building the dashboard and pages.
