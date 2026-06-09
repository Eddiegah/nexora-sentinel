from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd
import os
import anthropic
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
# Database setup
def get_db_connection():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            country VARCHAR(100),
            year INTEGER,
            risk_level VARCHAR(50),
            confidence FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()
load_dotenv()

app = FastAPI(
    title="Nexora Sentinel API",
    description="AI-powered malaria outbreak prediction for Africa",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
le_country = None
le_target = None
countries = []

try:
    with open("ml/artifacts/best_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("ml/artifacts/label_encoder_country.pkl", "rb") as f:
        le_country = pickle.load(f)
    with open("ml/artifacts/label_encoder_target.pkl", "rb") as f:
        le_target = pickle.load(f)
    print("Model loaded successfully")
except Exception as e:
    print(f"ERROR loading model: {e}")

try:
    df = pd.read_csv("data/processed/malaria_clean.csv")
    countries = sorted(df["country"].unique().tolist())
    print(f"Loaded {len(countries)} countries")
except Exception as e:
    print(f"ERROR loading data: {e}")


class PredictionRequest(BaseModel):
    country: str
    year: int
    urban_population_pct: float = 50.0
    rural_population_pct: float = 50.0
    urban_growth: float = 2.0
    rural_growth: float = 1.5
    water_access_pct: float = 60.0


class ReportRequest(BaseModel):
    country: str
    year: int
    risk_level: str
    confidence: float


@app.get("/")
def root():
    return {
        "message": "Nexora Sentinel API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/countries")
def get_countries():
    return {
        "countries": countries,
        "total": len(countries)
    }


@app.post("/predict")
def predict(request: PredictionRequest):
    if model is None:
        return {"error": "Model not loaded"}
    if request.country not in le_country.classes_:
        return {"error": f"Country '{request.country}' not recognized"}
    country_encoded = le_country.transform([request.country])[0]
    features = np.array([[
        country_encoded,
        request.year,
        request.rural_population_pct,
        request.urban_population_pct,
        request.rural_growth,
        request.urban_growth,
        request.water_access_pct,
        request.water_access_pct,
        request.water_access_pct,
        max(0, request.water_access_pct - 20),
        max(0, request.water_access_pct - 15),
        min(100, request.water_access_pct + 10),
        0.0,
        0.0,
    ]])
    prediction_encoded = model.predict(features)[0]
    prediction = le_target.inverse_transform([prediction_encoded])[0]
    probabilities = model.predict_proba(features)[0]
    confidence = float(max(probabilities))
    risk_colors = {
        "Low": "#22c55e",
        "Medium": "#f59e0b",
        "High": "#ef4444"
    }
    # Save to database
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO predictions (country, year, risk_level, confidence) VALUES (%s, %s, %s, %s)",
            (request.country, request.year, prediction, round(confidence * 100, 1))
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB save error: {e}")
    return {
        "country": request.country,
        "year": request.year,
        "risk_level": prediction,
        "confidence": round(confidence * 100, 1),
        "color": risk_colors.get(prediction, "#gray"),
        "message": f"{prediction} malaria outbreak risk predicted for {request.country} in {request.year}"
    }


@app.post("/report")
def generate_report(request: ReportRequest):
    try:
        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        prompt = f"""You are a professional public health analyst specializing in infectious disease surveillance in Africa.

Generate a concise professional health intelligence report based on this malaria outbreak prediction:

Country: {request.country}
Year: {request.year}
Predicted Risk Level: {request.risk_level}
Model Confidence: {request.confidence}%

Your report must include:
1. A one-sentence executive summary
2. Key risk factors for this country and risk level
3. Recommended actions for health officials
4. One specific data-driven insight

Keep the report under 200 words. Write in professional paragraphs, no bullet points."""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return {
            "country": request.country,
            "year": request.year,
            "risk_level": request.risk_level,
            "confidence": request.confidence,
            "report": message.content[0].text,
            "model": "claude-haiku-4-5"
        }
    except Exception as e:
        return {
            "error": str(e),
            "report": "Report generation failed. Please try again."
            @app.get("/history")
def get_history():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT country, year, risk_level, confidence, created_at FROM predictions ORDER BY created_at DESC LIMIT 20"
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {
            "history": [
                {
                    "country": row[0],
                    "year": row[1],
                    "risk_level": row[2],
                    "confidence": row[3],
                    "created_at": str(row[4])
                }
                for row in rows
            ]
        }
    except Exception as e:
        return {"error": str(e), "history": []}
        }