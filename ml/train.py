"""
Trains and honestly evaluates the malaria risk classifier.

Two evaluation protocols are reported, deliberately, because they answer
different questions and it would be easy to accidentally overstate the
model by only reporting the flattering one:

  1. Random split (80/20, stratified by risk_level): the standard ML
     evaluation. For year-over-year panel data like this, a random split
     lets the model see e.g. Ghana-2015 in training and Ghana-2016 in
     test -- adjacent years are highly correlated, so this number tends
     to look better than the model's real forecasting ability.

  2. Temporal holdout (train on years <= 2019, test on 2020-2024): the
     evaluation that actually matches the pitch's "predict outbreak risk"
     framing -- can the model generalize to years it has never seen,
     using only patterns learned from the past? This is the harder, more
     honest number.

Both are saved to metrics.json. Whichever is reported publicly, it's
reproducible by re-running this script against data/processed/malaria_africa.csv.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier

BASE = Path(__file__).resolve().parents[1]
DATA_CSV = BASE / "data" / "processed" / "malaria_africa.csv"
ARTIFACTS = Path(__file__).resolve().parent / "artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)

FEATURE_COLS = [
    "country_encoded", "year",
    "urban_population_pct", "rural_population_pct",
    "urban_growth_pct", "population_growth_pct",
    "water_access_pct", "sanitation_access_pct",
]
TEMPORAL_SPLIT_YEAR = 2020  # train < this, test >= this


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_CSV)
    return df


def prepare(df: pd.DataFrame, le_country: LabelEncoder, le_target: LabelEncoder) -> tuple[np.ndarray, np.ndarray]:
    df = df.copy()
    df["country_encoded"] = le_country.transform(df["country_iso3"])
    X = df[FEATURE_COLS].to_numpy()
    y = le_target.transform(df["risk_level"])
    return X, y


def evaluate(model, X_test, y_test, label_names) -> dict:
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, preds, average="weighted", zero_division=0)
    report = classification_report(y_test, preds, target_names=label_names, output_dict=True, zero_division=0)
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1, "report": report}


def main():
    df = load_data()

    le_country = LabelEncoder().fit(df["country_iso3"])
    le_target = LabelEncoder().fit(df["risk_level"])
    label_names = list(le_target.classes_)

    results = {"random_split": {}, "temporal_holdout": {}}

    # --- Random split ---
    X, y = prepare(df, le_country, le_target)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    scaler = StandardScaler().fit(X_train)
    logreg = LogisticRegression(max_iter=1000, random_state=42)
    logreg.fit(scaler.transform(X_train), y_train)
    results["random_split"]["logistic_regression"] = evaluate(logreg, scaler.transform(X_test), y_test, label_names)

    xgb_random = XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.08,
        subsample=0.9, colsample_bytree=0.9, random_state=42,
        eval_metric="mlogloss",
    )
    xgb_random.fit(X_train, y_train)
    results["random_split"]["xgboost"] = evaluate(xgb_random, X_test, y_test, label_names)

    # --- Temporal holdout ---
    train_df = df[df["year"] < TEMPORAL_SPLIT_YEAR]
    test_df = df[df["year"] >= TEMPORAL_SPLIT_YEAR]
    Xt_train, yt_train = prepare(train_df, le_country, le_target)
    Xt_test, yt_test = prepare(test_df, le_country, le_target)

    xgb_temporal = XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.08,
        subsample=0.9, colsample_bytree=0.9, random_state=42,
        eval_metric="mlogloss",
    )
    xgb_temporal.fit(Xt_train, yt_train)
    results["temporal_holdout"]["xgboost"] = evaluate(xgb_temporal, Xt_test, yt_test, label_names)
    results["temporal_holdout"]["train_years"] = f"< {TEMPORAL_SPLIT_YEAR}"
    results["temporal_holdout"]["test_years"] = f">= {TEMPORAL_SPLIT_YEAR}"
    results["temporal_holdout"]["train_size"] = len(train_df)
    results["temporal_holdout"]["test_size"] = len(test_df)

    # --- Final production model: trained on ALL data (random-split XGBoost
    # architecture, since that's the one being served) so the deployed
    # model benefits from every real record we have, not just 80% of it.
    final_model = XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.08,
        subsample=0.9, colsample_bytree=0.9, random_state=42,
        eval_metric="mlogloss",
    )
    final_model.fit(X, y)

    joblib.dump(final_model, ARTIFACTS / "best_model.pkl")
    joblib.dump(le_country, ARTIFACTS / "label_encoder_country.pkl")
    joblib.dump(le_target, ARTIFACTS / "label_encoder_target.pkl")
    joblib.dump(FEATURE_COLS, ARTIFACTS / "feature_columns.pkl")

    metrics_path = BASE / "docs" / "metrics.json"
    metrics_path.parent.mkdir(exist_ok=True)
    metrics_path.write_text(json.dumps(results, indent=2, default=float))

    print("\n=== Random split (80/20, stratified) ===")
    print(f"Logistic Regression: acc={results['random_split']['logistic_regression']['accuracy']*100:.2f}%")
    print(f"XGBoost:             acc={results['random_split']['xgboost']['accuracy']*100:.2f}%")

    print(f"\n=== Temporal holdout (train {results['temporal_holdout']['train_years']}, "
          f"test {results['temporal_holdout']['test_years']}) ===")
    print(f"  train size={results['temporal_holdout']['train_size']}, test size={results['temporal_holdout']['test_size']}")
    print(f"XGBoost: acc={results['temporal_holdout']['xgboost']['accuracy']*100:.2f}%")

    print(f"\nProduction model (trained on all {len(df)} records) saved -> {ARTIFACTS}")
    print(f"Metrics -> {metrics_path}")


if __name__ == "__main__":
    main()
