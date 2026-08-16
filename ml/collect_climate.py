"""
Fetches real climate data from NASA POWER (power.larc.nasa.gov) -- free,
no API key required. Malaria transmission is strongly climate-driven
(mosquito breeding needs rainfall + warmth), and this was an explicitly
disclosed gap in the original model (demographic features only). This
adds it back with real data.

Simplification, disclosed: climate is queried at each country's capital
city coordinates (see country_coords.py), not averaged across the whole
country. Real climate varies within a country, but this is a reasonable
and transparent approximation given no-cost, no-key data sources.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

from country_coords import CAPITAL_COORDS

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

YEAR_START = 2000
YEAR_END = 2024


def fetch_climate_for_country(iso3: str, lat: float, lon: float) -> dict:
    cache_path = RAW_DIR / f"climate_{iso3}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
    params = {
        "parameters": "PRECTOTCORR,T2M",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": YEAR_START,
        "end": YEAR_END,
        "format": "JSON",
    }
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    cache_path.write_text(json.dumps(data))
    time.sleep(0.3)
    return data


def main():
    print(f"Fetching NASA POWER climate data for {len(CAPITAL_COORDS)} countries...")
    ok, failed = 0, []
    for iso3, (lat, lon) in CAPITAL_COORDS.items():
        try:
            data = fetch_climate_for_country(iso3, lat, lon)
            n_years = len([k for k in data["properties"]["parameter"]["T2M"] if k.endswith("13")])
            print(f"  {iso3}: {n_years} annual records cached")
            ok += 1
        except Exception as e:
            print(f"  {iso3}: FAILED -- {e}")
            failed.append(iso3)

    print(f"\nDone: {ok}/{len(CAPITAL_COORDS)} succeeded")
    if failed:
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
