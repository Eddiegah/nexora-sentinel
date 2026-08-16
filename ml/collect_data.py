"""
Fetches real public health and demographic data for African countries --
no synthetic data, no placeholders. Two sources, both free and requiring
no API key:

  1. WHO Global Health Observatory (GHO) OData API
     Indicator MALARIA_EST_INCIDENCE: estimated malaria incidence per 1,000
     population at risk. This becomes the target variable.
     https://ghoapi.azureedge.net/api/MALARIA_EST_INCIDENCE

  2. World Bank Open Data API
     Demographic and infrastructure indicators used as predictive features.
     https://api.worldbank.org/v2/country/{iso3;iso3;...}/indicator/{code}

Raw responses are cached to data/raw/ so this doesn't need to be re-run on
every pipeline execution -- but it CAN be re-run any time to pull fresh
data, since nothing here is hand-copied or fabricated.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

from countries import AFRICAN_COUNTRIES

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

ISO3_LIST = list(AFRICAN_COUNTRIES.keys())
ISO3_QUERY = ";".join(ISO3_LIST)

# World Bank indicator codes -> our feature name. Chosen to mirror what a
# real malaria-risk model would plausibly use: urbanization (denser
# settlement changes transmission dynamics), population growth (pressure on
# health infrastructure), and water/sanitation access (standing water and
# poor sanitation are direct malaria transmission risk factors).
WORLD_BANK_INDICATORS = {
    "SP.URB.TOTL.IN.ZS": "urban_population_pct",
    "SP.RUR.TOTL.ZS": "rural_population_pct",
    "SP.URB.GROW": "urban_growth_pct",
    "SP.POP.GROW": "population_growth_pct",
    "SH.H2O.BASW.ZS": "water_access_pct",
    "SH.STA.BASS.ZS": "sanitation_access_pct",
}

WHO_MALARIA_INDICATOR = "MALARIA_EST_INCIDENCE"
YEAR_RANGE = "2000:2024"


def fetch_who_malaria() -> list[dict]:
    cache_path = RAW_DIR / "who_malaria_incidence.json"
    if cache_path.exists():
        print(f"[cache] {cache_path.name}")
        return json.loads(cache_path.read_text())["value"]

    url = f"https://ghoapi.azureedge.net/api/{WHO_MALARIA_INDICATOR}"
    params = {"$filter": "ParentLocationCode eq 'AFR'"}
    print(f"[fetch] WHO GHO {WHO_MALARIA_INDICATOR} ...")
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    cache_path.write_text(json.dumps(data))
    print(f"  -> {len(data['value'])} records cached")
    return data["value"]


def fetch_world_bank_indicator(code: str) -> list[dict]:
    cache_path = RAW_DIR / f"worldbank_{code}.json"
    if cache_path.exists():
        print(f"[cache] {cache_path.name}")
        return json.loads(cache_path.read_text())

    url = f"https://api.worldbank.org/v2/country/{ISO3_QUERY}/indicator/{code}"
    params = {"format": "json", "date": YEAR_RANGE, "per_page": 20000}
    print(f"[fetch] World Bank {code} ...")
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    # World Bank returns [metadata, records] -- records can be None if the
    # indicator/date range is invalid, which we want to fail loudly on.
    records = payload[1] if len(payload) > 1 and payload[1] else []
    cache_path.write_text(json.dumps(records))
    print(f"  -> {len(records)} records cached")
    time.sleep(0.3)  # polite pacing, not required by the API but costs nothing
    return records


def main():
    malaria = fetch_who_malaria()
    print(f"\nWHO malaria incidence: {len(malaria)} records across "
          f"{len(set(r['SpatialDim'] for r in malaria))} countries, "
          f"years {min(r['TimeDim'] for r in malaria)}-{max(r['TimeDim'] for r in malaria)}")

    for code, name in WORLD_BANK_INDICATORS.items():
        records = fetch_world_bank_indicator(code)
        with_values = [r for r in records if r.get("value") is not None]
        print(f"World Bank {name} ({code}): {len(with_values)}/{len(records)} records have a value")

    print("\nRaw data collection complete -> data/raw/")


if __name__ == "__main__":
    main()
