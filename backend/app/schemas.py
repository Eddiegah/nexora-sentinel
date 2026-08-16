from __future__ import annotations

from pydantic import BaseModel


class PredictRequest(BaseModel):
    country_iso3: str
    year: int
    # Optional what-if overrides. If omitted, the real recorded value for
    # this country/year (or the nearest year with data) is used instead.
    urban_population_pct: float | None = None
    rural_population_pct: float | None = None
    urban_growth_pct: float | None = None
    population_growth_pct: float | None = None
    water_access_pct: float | None = None
    sanitation_access_pct: float | None = None
    avg_precipitation_mm_day: float | None = None
    avg_temperature_c: float | None = None


class PredictResponse(BaseModel):
    country_iso3: str
    country_name: str
    requested_year: int
    data_year_used: int
    is_hypothetical: bool
    features_used: dict[str, float]
    predicted_risk: str
    probabilities: dict[str, float]
    shap_contributions: dict[str, float]


class CountryOut(BaseModel):
    iso3: str
    name: str
    years_available: list[int]


class HistoryRecord(BaseModel):
    id: int
    created_at: str
    country_iso3: str
    country_name: str
    requested_year: int
    data_year_used: int
    is_hypothetical: bool
    predicted_risk: str
    probabilities: dict[str, float]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    db_connected: bool


class OverviewEntry(BaseModel):
    country_iso3: str
    country_name: str
    year: int
    predicted_risk: str
    probabilities: dict[str, float]


class TrendPoint(BaseModel):
    year: int
    predicted_risk: str
    probabilities: dict[str, float]
