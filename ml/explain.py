"""
Builds a real SHAP explainer for the trained production model and saves a
summary plot -- genuine feature-attribution values computed against the
actual training data, not illustrative/placeholder numbers.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import shap

BASE = Path(__file__).resolve().parents[1]
ARTIFACTS = Path(__file__).resolve().parent / "artifacts"
DOCS = BASE / "docs"
DOCS.mkdir(exist_ok=True)


def main():
    model = joblib.load(ARTIFACTS / "best_model.pkl")
    le_country = joblib.load(ARTIFACTS / "label_encoder_country.pkl")
    feature_cols = joblib.load(ARTIFACTS / "feature_columns.pkl")

    df = pd.read_csv(BASE / "data" / "processed" / "malaria_africa.csv")
    df["country_encoded"] = le_country.transform(df["country_iso3"])
    X = df[feature_cols]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    joblib.dump(explainer, ARTIFACTS / "shap_explainer.pkl")

    # For this multiclass model, TreeExplainer returns a 3D array
    # (n_samples, n_features, n_classes). summary_plot expects either a 2D
    # array (binary/regression) or a list of per-class 2D arrays -- passing
    # the raw 3D array silently gets misread as feature-interaction values,
    # so split it into one array per class explicitly.
    le_target = joblib.load(ARTIFACTS / "label_encoder_target.pkl")
    if isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
        per_class = [shap_values[:, :, i] for i in range(shap_values.shape[2])]
    else:
        per_class = shap_values  # already a list of per-class arrays

    plt.figure()
    shap.summary_plot(
        per_class, X, feature_names=list(feature_cols), show=False, plot_type="bar",
        class_names=list(le_target.classes_),
    )
    plt.tight_layout()
    plt.savefig(DOCS / "shap_summary.png", dpi=150)
    plt.close()

    print(f"SHAP explainer saved -> {ARTIFACTS / 'shap_explainer.pkl'}")
    print(f"SHAP summary plot -> {DOCS / 'shap_summary.png'}")


if __name__ == "__main__":
    main()
