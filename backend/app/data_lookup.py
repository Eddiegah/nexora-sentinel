"""
Loads the real processed dataset once at startup so /predict can look up
actual recorded feature values for a country/year, and /countries can
report exactly which countries and years have real data behind them.
"""

from __future__ import annotations

import pandas as pd

from app.config import PROCESSED_DATA_CSV

FEATURE_COLS = [
    "urban_population_pct", "rural_population_pct",
    "urban_growth_pct", "population_growth_pct",
    "water_access_pct", "sanitation_access_pct",
    "avg_precipitation_mm_day", "avg_temperature_c",
]

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
