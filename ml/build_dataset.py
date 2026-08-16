"""
Joins the raw WHO malaria data with the raw World Bank indicators into one
training-ready table, engineers the risk label, and writes both the
cleaned CSV and a methodology.json documenting exactly how -- so the
"96% accuracy" kind of claim in a pitch document is always traceable back
to a real, inspectable process instead of being an unverifiable number.

Risk label methodology (documented, not hidden): there is no single
official 3-tier WHO malaria risk classification usable directly for ML.
This pipeline bins the real WHO-reported incidence values into tertiles
(bottom third = Low, middle third = Medium, top third = High) computed
from this dataset's own distribution. The exact cutpoints are written to
methodology.json for full transparency.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from countries import AFRICAN_COUNTRIES
from collect_data import WORLD_BANK_INDICATORS, RAW_DIR

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_malaria() -> pd.DataFrame:
    raw = json.loads((RAW_DIR / "who_malaria_incidence.json").read_text())["value"]
    df = pd.DataFrame(raw)[["SpatialDim", "TimeDim", "NumericValue"]]
    df.columns = ["country_iso3", "year", "malaria_incidence"]
    return df


def load_world_bank_indicator(code: str, feature_name: str) -> pd.DataFrame:
    raw = json.loads((RAW_DIR / f"worldbank_{code}.json").read_text())
    rows = [
        {"country_iso3": r["countryiso3code"], "year": int(r["date"]), feature_name: r["value"]}
        for r in raw
        if r.get("value") is not None and r.get("countryiso3code")
    ]
    return pd.DataFrame(rows)


def build() -> tuple[pd.DataFrame, dict]:
    malaria = load_malaria()

    features = None
    for code, name in WORLD_BANK_INDICATORS.items():
        indicator_df = load_world_bank_indicator(code, name)
        features = indicator_df if features is None else features.merge(indicator_df, on=["country_iso3", "year"], how="outer")

    df = malaria.merge(features, on=["country_iso3", "year"], how="inner")

    # Per-country linear interpolation for small gaps in the World Bank
    # indicators (they're slowly-changing demographic series, so this is a
    # defensible fill -- NOT applied to the malaria target itself).
    feature_cols = list(WORLD_BANK_INDICATORS.values())
    df = df.sort_values(["country_iso3", "year"])
    df[feature_cols] = df.groupby("country_iso3")[feature_cols].transform(lambda s: s.interpolate(limit_direction="both"))

    before = len(df)
    df = df.dropna(subset=feature_cols + ["malaria_incidence"])
    dropped = before - len(df)

    df["country"] = df["country_iso3"].map(AFRICAN_COUNTRIES)

    # Risk label: tertiles of the real incidence distribution in this dataset.
    q1, q2 = df["malaria_incidence"].quantile([1 / 3, 2 / 3])
    def label(v: float) -> str:
        if v <= q1:
            return "Low"
        if v <= q2:
            return "Medium"
        return "High"
    df["risk_level"] = df["malaria_incidence"].apply(label)

    methodology = {
        "target_variable": {
            "source": "WHO Global Health Observatory",
            "indicator_code": "MALARIA_EST_INCIDENCE",
            "indicator_name": "Estimated malaria incidence (per 1,000 population at risk)",
            "url": "https://ghoapi.azureedge.net/api/MALARIA_EST_INCIDENCE",
        },
        "features": {
            name: {"source": "World Bank Open Data", "indicator_code": code}
            for code, name in WORLD_BANK_INDICATORS.items()
        },
        "risk_label_methodology": {
            "method": "tertile binning of malaria_incidence within this dataset",
            "low_upper_bound": float(q1),
            "medium_upper_bound": float(q2),
            "note": "There is no single official WHO 3-tier risk classification; "
                    "these cutpoints are computed from this dataset's own distribution "
                    "and are fully reproducible by re-running build_dataset.py.",
        },
        "countries": len(df["country_iso3"].unique()),
        "year_range": [int(df["year"].min()), int(df["year"].max())],
        "records_after_join_and_cleaning": len(df),
        "records_dropped_missing_features": dropped,
    }

    return df, methodology


def main():
    df, methodology = build()
    df = df.sort_values(["country", "year"]).reset_index(drop=True)

    out_csv = PROCESSED_DIR / "malaria_africa.csv"
    df.to_csv(out_csv, index=False)

    out_meta = PROCESSED_DIR / "methodology.json"
    out_meta.write_text(json.dumps(methodology, indent=2))

    print(f"Wrote {len(df)} records -> {out_csv}")
    print(f"Countries: {methodology['countries']}, years {methodology['year_range'][0]}-{methodology['year_range'][1]}")
    print(f"Risk label distribution:\n{df['risk_level'].value_counts()}")
    print(f"\nMethodology -> {out_meta}")


if __name__ == "__main__":
    main()
