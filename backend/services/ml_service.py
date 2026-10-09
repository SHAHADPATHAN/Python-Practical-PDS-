"""
ML service — loads the existing trained Random Forest model and
exposes prediction + metadata endpoints.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

from backend.utils import cache, paths


# ─── Model meta-data from practical_09_classifier_report.txt ─────────────────
MODEL_META: Dict[str, Any] = {
    "algorithm":         "Random Forest Classifier",
    "n_estimators":       200,
    "max_depth":           20,
    "min_samples_split":    4,
    "min_samples_leaf":     2,
    "class_weight":    "balanced",
    "random_state":        42,
    "classes":      ["benign", "bot", "scanner", "suspicious"],
    "train_rows":      14_643,
    "test_rows":        3_661,
    "feature_count":    9_450,
    "accuracy":         0.9921,
    "precision":        0.9923,
    "recall":           0.9921,
    "f1":               0.9921,
    "confusion_matrix": {
        "benign":     {"benign": 915, "bot": 0,   "scanner": 0,   "suspicious": 0},
        "bot":        {"benign": 7,   "bot": 908, "scanner": 0,   "suspicious": 0},
        "scanner":    {"benign": 5,   "bot": 0,   "scanner": 911, "suspicious": 0},
        "suspicious": {"benign": 13,  "bot": 4,   "scanner": 0,   "suspicious": 898},
    },
    "top_features": [
        {"feature": "bot_indicator_none",       "importance": 0.067312},
        {"feature": "scanner_indicator_none",   "importance": 0.044988},
        {"feature": "requests_per_ip_hour",     "importance": 0.044685},
        {"feature": "requests_per_ip_minute",   "importance": 0.040784},
        {"feature": "user_agent_length",        "importance": 0.039513},
        {"feature": "scanner_and_high_volume",  "importance": 0.037494},
        {"feature": "is_browser",               "importance": 0.037283},
        {"feature": "rapid_request",            "importance": 0.035969},
        {"feature": "rapid_request_5s",         "importance": 0.034356},
        {"feature": "user_agent_entropy",       "importance": 0.034030},
        {"feature": "requests_per_ip",          "importance": 0.032953},
        {"feature": "requests_in_chunk",        "importance": 0.032537},
        {"feature": "rapid_request_1s",         "importance": 0.026119},
        {"feature": "rapid_and_high_volume",    "importance": 0.025093},
        {"feature": "unique_ports_per_ip",      "importance": 0.024682},
    ],
    "leakage_warning": (
        "Some features (bot_indicator_none, scanner_indicator_none) are "
        "derived from the same indicators used during labeling. Therefore "
        "this 99.21% accuracy should NOT be interpreted as proof of "
        "real-world generalization."
    ),
    "model_file": str(paths.MODEL_FILE),
}


def _load_model():
    if cache.has("ml_model"):
        return cache.get("ml_model")

    if not paths.MODEL_FILE.exists():
        return None

    try:
        pkg = joblib.load(paths.MODEL_FILE)
        cache.set("ml_model", pkg)
        return pkg
    except Exception as exc:
        print(f"[ML] Failed to load model: {exc}")
        return None


def get_model_info() -> Dict[str, Any]:
    pkg = _load_model()
    info = dict(MODEL_META)
    info["model_loaded"] = pkg is not None
    info["model_file_exists"] = paths.MODEL_FILE.exists()
    if paths.MODEL_FILE.exists():
        info["model_file_size_mb"] = round(
            paths.MODEL_FILE.stat().st_size / 1024 / 1024, 2
        )
    return info


def predict(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attempt to run the trained model against a dict of feature values.
    Returns prediction, probability, and contributing signals.
    """
    pkg = _load_model()
    if pkg is None:
        return {"error": "Model not loaded", "available": False}

    model         = pkg.get("model")
    label_encoder = pkg.get("label_encoder")
    feature_cols  = pkg.get("feature_columns", [])

    if model is None or label_encoder is None:
        return {"error": "Model package is incomplete", "available": False}

    # Build a single-row dataframe aligned to training columns
    row = {col: features.get(col, 0) for col in feature_cols}
    X   = pd.DataFrame([row])

    # Handle booleans
    bool_cols = X.select_dtypes(include=["bool"]).columns
    if len(bool_cols):
        X[bool_cols] = X[bool_cols].astype(int)

    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
    X = X.apply(pd.to_numeric, errors="coerce").fillna(0)

    try:
        pred_idx  = model.predict(X)[0]
        proba     = model.predict_proba(X)[0]
        classes   = label_encoder.classes_.tolist()
        pred_label = label_encoder.inverse_transform([pred_idx])[0]

        probabilities = {
            cls: round(float(p), 4)
            for cls, p in zip(classes, proba)
        }

        # Top contributing features (from model's feature importances)
        importances = model.feature_importances_
        fi_series   = pd.Series(importances, index=feature_cols)
        top_signals = fi_series.nlargest(5).to_dict()

        return {
            "available":     True,
            "prediction":    pred_label,
            "confidence":    round(float(max(proba)) * 100, 1),
            "probabilities": probabilities,
            "top_signals":   {
                k: round(float(v), 6) for k, v in top_signals.items()
            },
        }
    except Exception as exc:
        return {"error": str(exc), "available": False}
