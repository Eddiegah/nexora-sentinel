from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import data_lookup, database, ml_model
from app.config import CORS_ORIGINS
from app.schemas import (
    CountryOut,
    HealthResponse,
    HistoryRecord,
    PredictRequest,
    PredictResponse,
)

logger = logging.getLogger("nexora")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_model.load_artifacts()
    data_lookup.load()
    if database.is_configured():
        try:
            database.init_db()
        except Exception:
            logger.exception("Failed to initialize database -- history will be unavailable")
    yield


app = FastAPI(title="Nexora Sentinel API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        model_loaded=ml_model.is_loaded(),
        db_connected=database.check_connection(),
    )


@app.get("/countries", response_model=list[CountryOut])
def countries():
    return data_lookup.list_countries()


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        real_features, data_year_used = data_lookup.lookup_features(req.country_iso3, req.year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    overrides = req.model_dump(exclude={"country_iso3", "year"}, exclude_none=True)
    features_used = {**real_features, **overrides}
    is_hypothetical = bool(overrides)

    try:
        result = ml_model.predict(req.country_iso3, req.year, features_used)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    country_name = data_lookup.country_name(req.country_iso3)

    response = PredictResponse(
        country_iso3=req.country_iso3,
        country_name=country_name,
        requested_year=req.year,
        data_year_used=data_year_used,
        is_hypothetical=is_hypothetical,
        features_used=features_used,
        predicted_risk=result["predicted_risk"],
        probabilities=result["probabilities"],
        shap_contributions=result["shap_contributions"],
    )

    try:
        database.insert_prediction({
            "country_iso3": req.country_iso3,
            "country_name": country_name,
            "requested_year": req.year,
            "data_year_used": data_year_used,
            "is_hypothetical": is_hypothetical,
            "predicted_risk": result["predicted_risk"],
            "probabilities": result["probabilities"],
            "features_used": features_used,
        })
    except Exception:
        logger.exception("Failed to persist prediction to history")

    return response


@app.get("/history", response_model=list[HistoryRecord])
def history(limit: int = 50):
    return database.fetch_history(limit=limit)
