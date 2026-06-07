# backend/main.py
# Purpose: The main FastAPI application
# This is the entry point for our entire backend API

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd
import os

# ── 1. CREATE THE APP ─────────────────────────────────────────────
# FastAPI() creates our application
# The title and description appear in auto-generated API docs

app = FastAPI(
    title="Nexora Sentinel API",
    description="AI-powered malaria outbreak prediction for Africa",
    version="1.0.0"
)

# ── 2. CORS MIDDLEWARE ────────────────────────────────────────────
# CORS = Cross-Origin Resource Sharing
# This allows our React frontend (running on port 3000)
# to talk to our API (running on port 8000)
# Without this, the browser would block the connection

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow all origins for development
    allow_methods=["*"],      # allow GET, POST, etc.
    allow_headers=["*"],
)

# ── 3. LOAD THE TRAINED MODEL ─────────────────────────────────────
# We load the model once when the server starts
# This is much faster than loading it on every request

MODEL_PATH = "ml/artifacts/best_model.pkl"
ENCODER_PATH = "ml/artifacts/label_encoder_country.pkl"
TARGET_ENCODER_PATH = "ml/artifacts/label_encoder_target.pkl"

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(ENCODER_PATH, "rb") as f:
        le_country = pickle.load(f)
    with open(TARGET_ENCODER_PATH, "rb") as f:
        le_target = pickle.load(f)
    print("✓ Model and encoders loaded successfully")
except Exception as e:
    print(f"ERROR loading model: {e}")
    model = None

# ── 4. LOAD COUNTRY DATA FOR THE /countries ENDPOINT ──────────────
try:
    df = pd.read_csv("data/processed/malaria_clean.csv")
    countries = sorted(df["country"].unique().tolist())
    print(f"✓ Loaded {len(countries)} countries")
except Exception as e:
    print(f"ERROR loading data: {e}")
    countries = []

# ── 5. DEFINE REQUEST SCHEMA ──────────────────────────────────────
# This defines exactly what data the /predict endpoint expects
# Pydantic validates it automatically — wrong types get rejected

class PredictionRequest(BaseModel):
    country: str       # e.g. "Ghana"
    year: int          # e.g. 2024
    urban_population_pct: float = 50.0
    rural_population_pct: float = 50.0
    urban_growth: float = 2.0
    rural_growth: float = 1.5
    water_access_pct: float = 60.0

# ── 6. DEFINE ROUTES (ENDPOINTS) ──────────────────────────────────

# Root endpoint — health check
@app.get("/")
def root():
    return {
        "message": "Nexora Sentinel API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

# Countries endpoint — returns list of all countries
@app.get("/countries")
def get_countries():
    return {
        "countries": countries,
        "total": len(countries)
    }

# Predict endpoint — the main ML prediction
@app.post("/predict")
def predict(request: PredictionRequest):

    if model is None:
        return {"error": "Model not loaded"}

    # Check if country is known
    if request.country not in le_country.classes_:
        return {
            "error": f"Country '{request.country}' not recognized",
            "available_countries": list(le_country.classes_)
        }

    # Encode country name to number
    country_encoded = le_country.transform([request.country])[0]

    # Build feature array in same order as training
    features = np.array([[
        country_encoded,
        request.year,
        request.rural_population_pct,
        request.urban_population_pct,
        request.rural_growth,
        request.urban_growth,
        request.water_access_pct,
        request.water_access_pct,   # rural water (approximate)
        request.water_access_pct,   # urban water (approximate)
        max(0, request.water_access_pct - 20),  # sanitation
        max(0, request.water_access_pct - 15),  # rural sanitation
        min(100, request.water_access_pct + 10), # urban sanitation
        0.0,   # latitude placeholder
        0.0,   # longitude placeholder
    ]])

    # Make prediction
    prediction_encoded = model.predict(features)[0]
    prediction = le_target.inverse_transform([prediction_encoded])[0]

    # Get confidence scores
    probabilities = model.predict_proba(features)[0]
    confidence = float(max(probabilities))

    # Risk color for the dashboard
    risk_colors = {
        "Low": "#22c55e",      # green
        "Medium": "#f59e0b",   # amber
        "High": "#ef4444"      # red
    }

    return {
        "country": request.country,
        "year": request.year,
        "risk_level": prediction,
        "confidence": round(confidence * 100, 1),
        "color": risk_colors.get(prediction, "#gray"),
        "message": f"{prediction} malaria outbreak risk predicted for {request.country} in {request.year}"
    }