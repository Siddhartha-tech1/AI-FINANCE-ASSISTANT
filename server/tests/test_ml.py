from app.constants import TRANSACTION_CATEGORIES
from ml.predict import load_model, predict_category
from ml.train_classifier import evaluate, load_dataset, train


def test_classifier_can_train_and_predict_from_sample_dataset():
    train()
    load_model.cache_clear()
    prediction = predict_category("uber ride")

    assert prediction["predicted_category"] in TRANSACTION_CATEGORIES
    assert 0 <= prediction["confidence"] <= 1


def test_classifier_evaluation_reports_standard_metrics():
    descriptions, categories = load_dataset()
    metrics = evaluate(descriptions, categories)

    assert {"accuracy", "precision", "recall", "f1", "confusion_matrix", "labels"} <= metrics.keys()
    assert 0 <= metrics["accuracy"] <= 1
