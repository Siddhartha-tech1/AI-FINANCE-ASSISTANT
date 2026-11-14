# Machine Learning Features

## 1. Expense category prediction
Input: transaction description.  
Output: one category from Food, Transport, Shopping, Bills, Entertainment, Health, Education, Other.

Beginner implementation:
1. Prepare a labelled CSV dataset with `description` and `category`.
2. Clean descriptions.
3. Split into training and testing data.
4. Convert text using TF-IDF.
5. Train a Logistic Regression classifier.
6. Evaluate using accuracy, precision, recall, F1-score, and confusion matrix.
7. Save the trained pipeline using joblib.
8. Load it in Flask and expose `/ml/predict-category`.

Important:
- A tiny sample dataset is only for checking that the code runs, not for claiming good model accuracy.
- Let the user change an incorrect category.
- Keep the predicted category separate from the final user-selected category.
- If the model is missing or uncertain, allow manual category selection.

## 2. Spending forecast
1. Read the user's past expense transactions.
2. Calculate total expenses for each month.
3. Check whether enough monthly history exists.
4. Use a simple baseline and Linear Regression as a beginner model.
5. Evaluate using chronological test data and MAE/RMSE.
6. Return an estimate for the next month.

If there is not enough history, return an `insufficient_data` message. Never present the estimate as guaranteed.

## 3. AI insights
Start with simple rule-based insights:
- Highest spending category.
- Budget almost used.
- Budget exceeded.
- Expenses increased compared with last month.
- Expenses are greater than income.

Each insight should be based on actual calculations from the signed-in user's data.

## 4. Chatbot
Start with a simple intent/rule-based chatbot. Support questions such as:
- How much did I spend this month?
- Which category did I spend most on?
- How much budget is remaining?

Use only the authenticated user's data. Do not invent answers or provide professional investment/tax advice.
