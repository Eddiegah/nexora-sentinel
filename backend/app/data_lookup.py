"""
Loads the real processed dataset once at startup so /predict can look up
actual recorded feature values for a country/year, and /countries can
report exactly which countries and years have real data behind them.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.config import PROCESSED_DATA_CSV

FEATURE_COLS = [
    "urban_population_pct", "rural_population_pct",
    "urban_growth_pct", "population_growth_pct",
    "water_access_pct", "sanitation_access_pct",
    "avg_precipitation_mm_day", "avg_temperature_c",
]

# Forecasting beyond the real data: a simple, disclosed linear trend fit on
# each country's own recent history -- not a climate or demographic model,
# just a transparent extrapolation. Capped at a short horizon so it stays
# defensible (long-range linear extrapolation of e.g. urbanization % would
# eventually produce nonsense).
PCT_FEATURES = {"urban_population_pct", "rural_population_pct", "water_access_pct", "sanitation_access_pct"}
FORECAST_LOOKBACK_YEARS = 10
FORECAST_MAX_HORIZON = 6

_df: pd.DataFrame | None = None


def load() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = pd.read_csv(PROCESSED_DATA_CSV)
    return _df


def list_countries() -> list[dict]:
    df = load()
    out = []
    for iso3, group in df.groupby("country_iso3"):
        out.append({
            "iso3": iso3,
            "name": group["country"].iloc[0],
            "years_available": sorted(int(y) for y in group["year"].unique()),
        })
    return sorted(out, key=lambda c: c["name"])


def country_name(country_iso3: str) -> str:
    df = load()
    match = df[df["country_iso3"] == country_iso3]
    if match.empty:
        raise ValueError(f"No data available for country '{country_iso3}'")
    return match["country"].iloc[0]


def lookup_features(country_iso3: str, year: int) -> tuple[dict, int]:
    """Returns (feature dict, actual year used). Falls back to the nearest
    available year for that country if the exact year isn't in the data --
    still real recorded data, just not from the exact requested year."""
    df = load()
    country_df = df[df["country_iso3"] == country_iso3]
    if country_df.empty:
        raise ValueError(f"No data available for country '{country_iso3}'")

    exact = country_df[country_df["year"] == year]
    if not exact.empty:
        row = exact.iloc[0]
        used_year = year
    else:
        country_df = country_df.copy()
        country_df["year_distance"] = (country_df["year"] - year).abs()
        row = country_df.sort_values("year_distance").iloc[0]
        used_year = int(row["year"])

    features = {col: float(row[col]) for col in FEATURE_COLS}
    return features, used_year


def forecast_features(country_iso3: str, year: int) -> tuple[dict, int]:
    """Extrapolates each feature via a linear trend fit on the country's own
    last FORECAST_LOOKBACK_YEARS of real data. Returns (forecasted feature
    dict, last real year the fit was based on). Raises ValueError if year
    isn't actually in the future, or is beyond the supported horizon."""
    df = load()
    country_df = df[df["country_iso3"] == country_iso3].sort_values("year")
    if country_df.empty:
        raise ValueError(f"No data available for country '{country_iso3}'")

    last_real_year = int(country_df["year"].max())
    if year <= last_real_year:
        raise ValueError(f"{year} is not beyond the real data range for '{country_iso3}'")
    if year > last_real_year + FORECAST_MAX_HORIZON:
        raise ValueError(
            f"Cannot forecast {year}: forecasting is limited to {FORECAST_MAX_HORIZON} years "
            f"beyond the last real data point ({last_real_year}) to stay within a defensible "
            f"linear-trend horizon."
        )

    recent = country_df.tail(FORECAST_LOOKBACK_YEARS)
    years = recent["year"].to_numpy(dtype=float)

    features = {}
    for col in FEATURE_COLS:
        values = recent[col].to_numpy(dtype=float)
        if len(values) < 2 or np.ptp(years) == 0:
            # Not enough distinct real years for this country to fit a trend
            # (sparse World Bank/NASA coverage for some small countries) --
            # fall back to a flat projection from the last real value rather
            # than failing outright.
            projected = float(values[-1])
        else:
            slope, intercept = np.polyfit(years, values, 1)
            projected = slope * year + intercept
        if col in PCT_FEATURES:
            projected = max(0.0, min(100.0, projected))
        features[col] = float(projected)

    return features, last_real_year


def resolve_features(country_iso3: str, year: int) -> tuple[dict, int, bool]:
    """Single entry point for /predict and /overview: real recorded data for
    years within the dataset, a disclosed linear-trend forecast for years
    beyond it. Returns (features, data_year_used, is_forecast)."""
    df = load()
    country_df = df[df["country_iso3"] == country_iso3]
    if country_df.empty:
        raise ValueError(f"No data available for country '{country_iso3}'")

    last_real_year = int(country_df["year"].max())
    if year > last_real_year:
        features, base_year = forecast_features(country_iso3, year)
        return features, base_year, True

    features, used_year = lookup_features(country_iso3, year)
    return features, used_year, False
