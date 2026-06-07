# backend/tests/test_api.py
# Basic tests for the Nexora Sentinel API

from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from backend.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_countries():
    response = client.get("/countries")
    assert response.status_code == 200
    assert "countries" in response.json()
    assert len(response.json()["countries"]) > 0

def test_predict_ghana():
    response = client.post("/predict", json={
        "country": "Ghana",
        "year": 2024,
        "urban_population_pct": 58.0,
        "rural_population_pct": 42.0,
        "urban_growth": 3.2,
        "rural_growth": 1.8,
        "water_access_pct": 61.0
    })
    assert response.status_code == 200
    data = response.json()
    assert "risk_level" in data
    assert data["risk_level"] in ["Low", "Medium", "High"]
    assert "confidence" in data

def test_predict_invalid_country():
    response = client.post("/predict", json={
        "country": "Wakanda",
        "year": 2024,
        "urban_population_pct": 50.0,
        "rural_population_pct": 50.0,
        "urban_growth": 2.0,
        "rural_growth": 1.5,
        "water_access_pct": 60.0
    })
    assert response.status_code == 200
    assert "error" in response.json()