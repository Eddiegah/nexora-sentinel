# ml/models/train.py
# Purpose: Train and evaluate ML models on the cleaned malaria dataset
# We train two models and compare their performance

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb
import os
import pickle

print("=" * 55)
print("NEXORA SENTINEL — MODEL TRAINING")
print("=" * 55)

# ── 1. LOAD CLEANED DATA ──────────────────────────────────────────
df = pd.read_csv("data/processed/malaria_clean.csv")
print(f"\nLoaded {len(df)} rows of cleaned data")

# ── 2. SELECT FEATURES ────────────────────────────────────────────
# Features = the columns we use to make predictions
# We drop columns that are not useful for prediction:
# - country, country_code: text identifiers (we'll encode country)
# - geometry: geographic format we won't use here
# - malaria_incidence: this is what risk_level is derived FROM
#   (using it would be "cheating" — the model would just read the answer)
# - malaria_cases: also too directly related to the target
# - risk_level: this is what we're trying to PREDICT

FEATURES_TO_DROP = [
    "country_code",
    "geometry", 
    "malaria_incidence",
    "malaria_cases",
    "risk_level"
]

# Drop columns that don't exist (safety check)
FEATURES_TO_DROP = [c for c in FEATURES_TO_DROP if c in df.columns]

# Our feature matrix X and target vector y
X = df.drop(columns=FEATURES_TO_DROP)
y = df["risk_level"]

print(f"Features being used: {list(X.columns)}")
print(f"Target: risk_level")
print(f"Class distribution:\n{y.value_counts()}")

# ── 3. ENCODE COUNTRY NAME ────────────────────────────────────────
# Machine learning models only understand numbers, not text
# LabelEncoder converts "Ghana" -> 12, "Nigeria" -> 34, etc.

le_country = LabelEncoder()
X["country"] = le_country.fit_transform(X["country"])

# ── 4. SPLIT INTO TRAIN AND TEST SETS ─────────────────────────────
# We split our data into two parts:
# - Training set (80%): the model learns from this
# - Test set (20%): we hide this from the model, then test on it
#
# This simulates the real world — the model will face data it never saw
# If it performs well on test data, it has genuinely learned patterns

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,        # 20% goes to test
    random_state=42,      # fixed seed for reproducibility
    stratify=y            # ensure equal class distribution in both sets
)

print(f"\nTraining samples: {len(X_train)}")
print(f"Test samples:     {len(X_test)}")

# ── 5. SCALE FEATURES ─────────────────────────────────────────────
# Logistic Regression is sensitive to feature scale
# StandardScaler makes all features have mean=0, std=1
# This prevents large numbers from dominating small ones

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ── 6. TRAIN MODEL 1: LOGISTIC REGRESSION ─────────────────────────
print("\n" + "=" * 55)
print("MODEL 1: LOGISTIC REGRESSION (Baseline)")
print("=" * 55)

lr_model = LogisticRegression(
    max_iter=1000,    # maximum iterations to converge
    random_state=42
)
lr_model.fit(X_train_scaled, y_train)

# Evaluate on test set
lr_predictions = lr_model.predict(X_test_scaled)
lr_accuracy = accuracy_score(y_test, lr_predictions)

print(f"Accuracy: {lr_accuracy:.2%}")
print("\nDetailed Report:")
print(classification_report(y_test, lr_predictions))

# ── 7. TRAIN MODEL 2: XGBOOST ─────────────────────────────────────
print("=" * 55)
print("MODEL 2: XGBOOST")
print("=" * 55)

# XGBoost needs numeric labels
le_target = LabelEncoder()
y_train_encoded = le_target.fit_transform(y_train)
y_test_encoded = le_target.transform(y_test)

xgb_model = xgb.XGBClassifier(
    n_estimators=100,     # number of trees
    max_depth=4,          # how deep each tree goes
    learning_rate=0.1,    # how fast it learns
    random_state=42,
    eval_metric="mlogloss",
    verbosity=0
)
xgb_model.fit(X_train, y_train_encoded)

# Evaluate
xgb_predictions_encoded = xgb_model.predict(X_test)
xgb_predictions = le_target.inverse_transform(xgb_predictions_encoded)
xgb_accuracy = accuracy_score(y_test, xgb_predictions)

print(f"Accuracy: {xgb_accuracy:.2%}")
print("\nDetailed Report:")
print(classification_report(y_test, xgb_predictions))

# ── 8. COMPARE AND SAVE BEST MODEL ────────────────────────────────
print("=" * 55)
print("COMPARISON")
print("=" * 55)
print(f"Logistic Regression: {lr_accuracy:.2%}")
print(f"XGBoost:             {xgb_accuracy:.2%}")

if xgb_accuracy >= lr_accuracy:
    print("\nWinner: XGBoost ✓")
    best_model = xgb_model
    best_name = "xgboost"
else:
    print("\nWinner: Logistic Regression ✓")
    best_model = lr_model
    best_name = "logistic_regression"

# ── 9. SAVE THE MODEL AND TOOLS ───────────────────────────────────
# pickle saves Python objects to disk so we can load them later
# We need to save: the model, the scaler, and the label encoders

os.makedirs("ml/artifacts", exist_ok=True)

with open("ml/artifacts/best_model.pkl", "wb") as f:
    pickle.dump(best_model, f)

with open("ml/artifacts/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

with open("ml/artifacts/label_encoder_country.pkl", "wb") as f:
    pickle.dump(le_country, f)

with open("ml/artifacts/label_encoder_target.pkl", "wb") as f:
    pickle.dump(le_target, f)

print(f"\n✓ Best model saved to ml/artifacts/best_model.pkl")
print(f"✓ Scaler saved to ml/artifacts/scaler.pkl")
print(f"✓ Label encoders saved")
print("\nTraining complete!")
