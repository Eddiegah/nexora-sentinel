"""
Loads the trained production model + encoders + SHAP explainer once at
startup and exposes a single predict() function used by the /predict route.
"""

from __future__ import annotations

import joblib
import numpy as np

from app.config import ML_ARTIFACTS_DIR

FEATURE_COLS = [
    "country_encoded", "year",
    "urban_population_pct", "rural_population_pct",
    "urban_growth_pct", "population_growth_pct",
    "water_access_pct", "sanitation_access_pct",
    "avg_precipitation_mm_day", "avg_temperature_c",
]

_model = None
_le_country = None
_le_target = None
_explainer = None


def load_artifacts() -> bool:
    """Loads all artifacts. Returns True on success. Any failure here means
    /predict cannot serve requests, but the API should still start so
    /health can report the problem instead of crashing outright."""
    global _model, _le_country, _le_target, _explainer
    try:
        _model = joblib.load(ML_ARTIFACTS_DIR / "best_model.pkl")
        _le_country = joblib.load(ML_ARTIFACTS_DIR / "label_encoder_country.pkl")
        _le_target = joblib.load(ML_ARTIFACTS_DIR / "label_encoder_target.pkl")
        _explainer = joblib.load(ML_ARTIFACTS_DIR / "shap_explainer.pkl")
        return True
    except FileNotFoundError:
        return False


def is_loaded() -> bool:
    return _model is not None


def known_countries() -> set[str]:
    return set(_le_country.classes_) if _le_country is not None else set()


def predict(country_iso3: str, year: int, features: dict) -> dict:
    """features must contain exactly the 8 non-country/year feature cols."""
    if _model is None:
        raise RuntimeError("Model artifacts are not loaded")
    if country_iso3 not in _le_country.classes_:
        raise ValueError(f"Country '{country_iso3}' was not part of the training data")

    country_encoded = int(_le_country.transform([country_iso3])[0])
    row = {
        "country_encoded": country_encoded,
        "year": year,
        **features,
    }
    X = np.array([[row[col] for col in FEATURE_COLS]])

    pred_encoded = int(_model.predict(X)[0])
    pred_label = _le_target.inverse_transform([pred_encoded])[0]

    proba = _model.predict_proba(X)[0]
    probabilities = {label: float(p) for label, p in zip(_le_target.classes_, proba)}

    shap_values = _explainer.shap_values(X)  # shape (1, n_features, n_classes)
    class_shap = shap_values[0, :, pred_encoded]
    display_names = {c: c for c in FEATURE_COLS}
    display_names["country_encoded"] = "country"
    shap_contributions = {
        display_names[col]: float(val)
        for col, val in zip(FEATURE_COLS, class_shap)
    }

    return {
        "predicted_risk": pred_label,
        "probabilities": probabilities,
        "shap_contributions": shap_contributions,
    }
