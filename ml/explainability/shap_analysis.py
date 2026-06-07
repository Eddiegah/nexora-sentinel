# ml/explainability/shap_analysis.py
# Purpose: Generate SHAP explanations for our XGBoost model
# SHAP tells us WHY the model made each prediction

import pandas as pd
import numpy as np
import shap
import pickle
import matplotlib
matplotlib.use('Agg')  # Required for Windows — renders without display
import matplotlib.pyplot as plt
import os

print("=" * 55)
print("NEXORA SENTINEL — SHAP EXPLAINABILITY")
print("=" * 55)

# ── 1. LOAD MODEL AND DATA ────────────────────────────────────────
print("\nLoading model and data...")

with open("ml/artifacts/best_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("ml/artifacts/label_encoder_country.pkl", "rb") as f:
    le_country = pickle.load(f)

with open("ml/artifacts/label_encoder_target.pkl", "rb") as f:
    le_target = pickle.load(f)

df = pd.read_csv("data/processed/malaria_clean.csv")
print(f"Loaded {len(df)} records")

# ── 2. PREPARE FEATURES ───────────────────────────────────────────
# Same preparation as training — must match exactly

FEATURES_TO_DROP = [
    "country_code", "geometry",
    "malaria_incidence", "malaria_cases", "risk_level"
]
FEATURES_TO_DROP = [c for c in FEATURES_TO_DROP if c in df.columns]

X = df.drop(columns=FEATURES_TO_DROP)
y = df["risk_level"]

# Encode country
X["country"] = le_country.transform(X["country"])

print(f"Features: {list(X.columns)}")

# ── 3. CREATE SHAP EXPLAINER ──────────────────────────────────────
# TreeExplainer is optimized for XGBoost and gradient boosting models
# It calculates exact SHAP values (not approximations)

print("\nCalculating SHAP values...")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

print(f"SHAP values shape: {np.array(shap_values).shape}")
print("SHAP calculation complete!")

# ── 4. FEATURE IMPORTANCE FROM SHAP ──────────────────────────────
# Mean absolute SHAP value = overall importance of each feature
# Higher = more influential in predictions

print("\n" + "=" * 55)
print("FEATURE IMPORTANCE (via SHAP)")
print("=" * 55)

# For multiclass, average across all classes
# shap_values shape is (550, 14, 3) — samples x features x classes
# Convert to numpy array and handle 3D case
shap_array = np.array(shap_values)

if shap_array.ndim == 3:
    # Average absolute SHAP across all classes and all samples
    mean_shap = np.abs(shap_array).mean(axis=0).mean(axis=1)
elif isinstance(shap_values, list):
    mean_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
else:
    mean_shap = np.abs(shap_array).mean(axis=0)

# Ensure it's a flat 1D array of plain Python floats
mean_shap = [float(x) for x in mean_shap.flatten()]

feature_names = list(X.columns)
importance_values = [float(v) for v in mean_shap]

feature_importance = pd.DataFrame({
    "feature": feature_names,
    "importance": importance_values
})

# Sort manually using zip to avoid pandas sorting issues
paired = list(zip(importance_values, feature_names))
paired.sort(reverse=True)
feature_importance = pd.DataFrame({
    "feature": [p[1] for p in paired],
    "importance": [p[0] for p in paired]
})

print(feature_importance.to_string(index=False))

# ── 5. SAVE SHAP SUMMARY PLOT ─────────────────────────────────────
# This creates the iconic SHAP beeswarm plot
# Shows which features push predictions High or Low

print("\nGenerating SHAP summary plot...")
os.makedirs("docs", exist_ok=True)

plt.figure(figsize=(10, 6))

if isinstance(shap_values, list):
    # For multiclass we show the class with most variation
    shap.summary_plot(
        shap_values[2],  # class index 2 (usually High risk)
        X,
        feature_names=list(X.columns),
        show=False,
        plot_size=(10, 6)
    )
else:
    shap.summary_plot(
        shap_values,
        X,
        feature_names=list(X.columns),
        show=False,
        plot_size=(10, 6)
    )

plt.title("Nexora Sentinel — Feature Impact on Malaria Risk Prediction",
          fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig("docs/shap_summary.png", dpi=150, bbox_inches='tight')
plt.close()
print("✓ SHAP summary plot saved to docs/shap_summary.png")

# ── 6. SAVE FEATURE IMPORTANCE CHART ─────────────────────────────
plt.figure(figsize=(10, 6))
colors = ['#ef4444' if i < 3 else '#f59e0b' if i < 6 else '#22c55e'
          for i in range(len(feature_importance))]
bars = plt.barh(
    feature_importance['feature'][::-1],
    feature_importance['importance'][::-1],
    color=colors[::-1]
)
plt.xlabel('Mean |SHAP Value| (Feature Importance)', fontsize=11)
plt.title('Nexora Sentinel — What Drives Malaria Outbreak Risk?',
          fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig("docs/feature_importance.png", dpi=150, bbox_inches='tight')
plt.close()
print("✓ Feature importance chart saved to docs/feature_importance.png")

# ── 7. EXPLAIN A SINGLE PREDICTION ───────────────────────────────
# ── 7. EXPLAIN GHANA'S PREDICTION ────────────────────────────────
print("\n" + "=" * 55)
print("EXAMPLE: EXPLAINING GHANA'S PREDICTION")
print("=" * 55)

ghana_rows = df[df["country"] == "Ghana"].copy()

if len(ghana_rows) > 0:
    ghana_X = ghana_rows.drop(columns=FEATURES_TO_DROP)
    ghana_X["country"] = le_country.transform(ghana_X["country"])

    ghana_shap = np.array(explainer.shap_values(ghana_X))

    if ghana_shap.ndim == 3:
        ghana_avg = np.abs(ghana_shap).mean(axis=0).mean(axis=1)
    else:
        ghana_avg = np.abs(ghana_shap).mean(axis=0)

    ghana_features = list(ghana_X.columns)
    ghana_impacts = [float(x) for x in ghana_avg.flatten()]

    paired = list(zip(ghana_impacts, ghana_features))
    paired.sort(reverse=True)

    print("\nTop factors driving Ghana's malaria risk prediction:")
    for impact, feature in paired[:5]:
        bar = "█" * max(1, int(impact * 100))
        print(f"  {feature:<40} {bar} {impact:.4f}")

else:
    print("Ghana not found in dataset")

# ── 8. SAVE EXPLAINER ─────────────────────────────────────────────
with open("ml/artifacts/shap_explainer.pkl", "wb") as f:
    pickle.dump(explainer, f)

print("\n✓ SHAP explainer saved to ml/artifacts/shap_explainer.pkl")
print("\nStage 2A Complete — SHAP Explainability is ready!")