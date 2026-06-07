# mlops/mlflow/train_with_mlflow.py
# Purpose: Train models with full MLflow experiment tracking
# Every run is logged — parameters, metrics, and artifacts

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, f1_score,
    precision_score, recall_score
)
import xgboost as xgb
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import pickle
import os

print("=" * 55)
print("NEXORA SENTINEL — MLFLOW EXPERIMENT TRACKING")
print("=" * 55)

# ── 1. SETUP MLFLOW ───────────────────────────────────────────────
# MLflow stores all experiments in a local folder called mlruns
# Set the experiment name — all runs group under this name

mlflow.set_experiment("nexora-sentinel-malaria-prediction")
print("\nMLflow experiment: nexora-sentinel-malaria-prediction")

# ── 2. LOAD AND PREPARE DATA ──────────────────────────────────────
df = pd.read_csv("data/processed/malaria_clean.csv")
print(f"Loaded {len(df)} records")

FEATURES_TO_DROP = [
    "country_code", "geometry",
    "malaria_incidence", "malaria_cases", "risk_level"
]
FEATURES_TO_DROP = [c for c in FEATURES_TO_DROP if c in df.columns]

X = df.drop(columns=FEATURES_TO_DROP)
y = df["risk_level"]

le_country = LabelEncoder()
X["country"] = le_country.fit_transform(X["country"])

le_target = LabelEncoder()
y_encoded = le_target.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Training: {len(X_train)} | Test: {len(X_test)}")

# ── 3. RUN 1: LOGISTIC REGRESSION ────────────────────────────────
print("\n" + "─" * 55)
print("RUN 1: Logistic Regression")

with mlflow.start_run(run_name="logistic_regression"):

    # Parameters to log
    params = {
        "model_type": "LogisticRegression",
        "max_iter": 1000,
        "random_state": 42,
        "test_size": 0.2,
        "n_features": X_train.shape[1],
        "n_samples": len(X_train)
    }

    # Log all parameters
    mlflow.log_params(params)

    # Train model
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train_scaled, y_train)
    preds = lr.predict(X_test_scaled)

    # Calculate metrics
    metrics = {
        "accuracy": accuracy_score(y_test, preds),
        "f1_macro": f1_score(y_test, preds, average="macro"),
        "precision_macro": precision_score(
            y_test, preds, average="macro", zero_division=0
        ),
        "recall_macro": recall_score(y_test, preds, average="macro")
    }

    # Log all metrics
    mlflow.log_metrics(metrics)

    # Log the model itself
    mlflow.sklearn.log_model(lr, "logistic_regression_model")

    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  F1 Score:  {metrics['f1_macro']:.4f}")
    print(f"  Precision: {metrics['precision_macro']:.4f}")
    print(f"  Recall:    {metrics['recall_macro']:.4f}")
    print(f"  ✓ Run logged to MLflow")

    lr_accuracy = metrics["accuracy"]

# ── 4. RUN 2: XGBOOST (DEFAULT) ───────────────────────────────────
print("\n" + "─" * 55)
print("RUN 2: XGBoost (Default Parameters)")

with mlflow.start_run(run_name="xgboost_default"):

    params = {
        "model_type": "XGBoost",
        "n_estimators": 100,
        "max_depth": 4,
        "learning_rate": 0.1,
        "random_state": 42,
        "test_size": 0.2,
        "n_features": X_train.shape[1],
        "n_samples": len(X_train)
    }

    mlflow.log_params(params)

    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        eval_metric="mlogloss",
        verbosity=0
    )
    xgb_model.fit(X_train, y_train)
    preds = xgb_model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, preds),
        "f1_macro": f1_score(y_test, preds, average="macro"),
        "precision_macro": precision_score(
            y_test, preds, average="macro", zero_division=0
        ),
        "recall_macro": recall_score(y_test, preds, average="macro")
    }

    mlflow.log_metrics(metrics)
    mlflow.xgboost.log_model(xgb_model, "xgboost_model")

    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  F1 Score:  {metrics['f1_macro']:.4f}")
    print(f"  Precision: {metrics['precision_macro']:.4f}")
    print(f"  Recall:    {metrics['recall_macro']:.4f}")
    print(f"  ✓ Run logged to MLflow")

    xgb_default_accuracy = metrics["accuracy"]

# ── 5. RUN 3: XGBOOST (TUNED) ─────────────────────────────────────
print("\n" + "─" * 55)
print("RUN 3: XGBoost (Tuned Parameters)")

with mlflow.start_run(run_name="xgboost_tuned"):

    params = {
        "model_type": "XGBoost_Tuned",
        "n_estimators": 200,
        "max_depth": 6,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
        "test_size": 0.2,
        "n_features": X_train.shape[1],
        "n_samples": len(X_train)
    }

    mlflow.log_params(params)

    xgb_tuned = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="mlogloss",
        verbosity=0
    )
    xgb_tuned.fit(X_train, y_train)
    preds = xgb_tuned.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, preds),
        "f1_macro": f1_score(y_test, preds, average="macro"),
        "precision_macro": precision_score(
            y_test, preds, average="macro", zero_division=0
        ),
        "recall_macro": recall_score(y_test, preds, average="macro")
    }

    mlflow.log_metrics(metrics)
    mlflow.xgboost.log_model(xgb_tuned, "xgboost_tuned_model")

    # Log SHAP charts as artifacts
    if os.path.exists("docs/shap_summary.png"):
        mlflow.log_artifact("docs/shap_summary.png")
    if os.path.exists("docs/feature_importance.png"):
        mlflow.log_artifact("docs/feature_importance.png")

    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  F1 Score:  {metrics['f1_macro']:.4f}")
    print(f"  Precision: {metrics['precision_macro']:.4f}")
    print(f"  Recall:    {metrics['recall_macro']:.4f}")
    print(f"  ✓ Run logged to MLflow")
    print(f"  ✓ SHAP charts logged as artifacts")

    xgb_tuned_accuracy = metrics["accuracy"]

# ── 6. SUMMARY ────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("EXPERIMENT SUMMARY")
print("=" * 55)
print(f"  Logistic Regression:  {lr_accuracy:.4f}")
print(f"  XGBoost (Default):    {xgb_default_accuracy:.4f}")
print(f"  XGBoost (Tuned):      {xgb_tuned_accuracy:.4f}")

best = max(lr_accuracy, xgb_default_accuracy, xgb_tuned_accuracy)
print(f"\n  Best accuracy: {best:.4f}")
print(f"\n✓ All runs tracked in MLflow")
print(f"✓ Run: mlflow ui")
print(f"✓ Open: http://127.0.0.1:5000")
print("\nStage 2B Complete!")