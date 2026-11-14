"""Train the expense category classifier outside the Flask request lifecycle."""

from pathlib import Path
import re

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "datasets" / "expense_categories.csv"
MODEL_PATH = ROOT / "expense_classifier.joblib"


def build_model():
    return Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english")), ("classifier", LogisticRegression(max_iter=1000))])


def load_dataset():
    """Clean blank, duplicate, and inconsistent text rows before training."""
    seen, cleaned = set(), []
    for line in DATASET.read_text(encoding="utf-8").splitlines()[1:]:
        if not line.strip() or "," not in line:
            continue
        description, category = (part.strip() for part in line.split(",", 1))
        description = re.sub(r"\s+", " ", description.lower())
        category = category.title()
        key = (description, category)
        if description and category and key not in seen:
            seen.add(key)
            cleaned.append(key)
    descriptions, categories = zip(*cleaned)
    return descriptions, categories


def evaluate(descriptions, categories):
    """Return readable held-out metrics for the small educational dataset."""
    train_x, test_x, train_y, test_y = train_test_split(
        descriptions, categories, test_size=0.25, random_state=42, stratify=categories
    )
    model = build_model().fit(train_x, train_y)
    predicted = model.predict(test_x)
    precision, recall, f1, _ = precision_recall_fscore_support(test_y, predicted, average="weighted", zero_division=0)
    return {
        "accuracy": round(float(accuracy_score(test_y, predicted)), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "confusion_matrix": confusion_matrix(test_y, predicted, labels=sorted(set(categories))).tolist(),
        "labels": sorted(set(categories)),
        "classification_report": classification_report(test_y, predicted, zero_division=0),
    }


def train():
    descriptions, categories = load_dataset()
    model = build_model()
    model.fit(descriptions, categories)
    joblib.dump(model, MODEL_PATH)
    return MODEL_PATH


if __name__ == "__main__":
    descriptions, categories = load_dataset()
    print(f"Saved model to {train()}")
    print(evaluate(descriptions, categories))
