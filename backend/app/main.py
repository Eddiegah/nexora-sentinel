import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app import data_lookup, database, ml_model
from app.config import CORS_ORIGINS
from app.schemas import (
    CountryOut,
    HealthResponse,
    HistoryRecord,
    OverviewEntry,
    PredictRequest,
    PredictResponse,
    TrendPoint,
)

logger = logging.getLogger("nexora")

limiter = Limiter(key_func=get_remote_address)


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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    # Vercel assigns a new preview URL per deploy/branch, so an exact-match
    # allowlist would need updating on every deploy. This is a public demo
    # API with no cookies/auth, so allowing any vercel.app subdomain is a
    # reasonable tradeoff.
    allow_origin_regex=r"https://.*\.vercel\.app",
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
@limiter.limit("30/minute")
def predict(request: Request, req: PredictRequest):
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


@app.get("/overview", response_model=list[OverviewEntry])
@limiter.limit("10/minute")
def overview(request: Request, year: int = 2024):
    """Predictions for every country's nearest-available year to `year`,
    in one call -- real recorded data, no what-if overrides, not persisted
    to history (this is a bulk dashboard view, not a user prediction)."""
    if not ml_model.is_loaded():
        raise HTTPException(status_code=503, detail="Model artifacts are not loaded")

    out = []
    for c in data_lookup.list_countries():
        try:
            features, data_year_used = data_lookup.lookup_features(c["iso3"], year)
            result = ml_model.predict(c["iso3"], data_year_used, features)
        except ValueError:
            continue
        out.append(OverviewEntry(
            country_iso3=c["iso3"],
            country_name=c["name"],
            year=data_year_used,
            predicted_risk=result["predicted_risk"],
            probabilities=result["probabilities"],
        ))
    return out


@app.get("/trend", response_model=list[TrendPoint])
@limiter.limit("30/minute")
def trend(request: Request, country_iso3: str):
    """Predicted risk for every year of real recorded data available for
    one country -- shows how risk has evolved 2000-2024, not persisted to
    history."""
    if not ml_model.is_loaded():
        raise HTTPException(status_code=503, detail="Model artifacts are not loaded")

    matches = [c for c in data_lookup.list_countries() if c["iso3"] == country_iso3]
    if not matches:
        raise HTTPException(status_code=404, detail=f"No data available for country '{country_iso3}'")

    out = []
    for year in matches[0]["years_available"]:
        features, data_year_used = data_lookup.lookup_features(country_iso3, year)
        result = ml_model.predict(country_iso3, data_year_used, features)
        out.append(TrendPoint(
            year=data_year_used,
            predicted_risk=result["predicted_risk"],
            probabilities=result["probabilities"],
        ))
    return out
