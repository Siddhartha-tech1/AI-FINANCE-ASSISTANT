"""Model loading and prediction helpers."""

from functools import lru_cache
from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent / "expense_classifier.joblib"


@lru_cache(maxsize=1)
def load_model():
    return joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None


def predict_category(description):
    model = load_model()
    if model is None:
        return None
    category = model.predict([description])[0]
    confidence = round(float(max(model.predict_proba([description])[0])), 4)
    return {"predicted_category": category, "confidence": confidence}
