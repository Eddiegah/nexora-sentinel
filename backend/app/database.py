"""
Thin PostgreSQL layer for prediction history. Uses a fresh connection per
call rather than a pool -- appropriate at this project's scale, and avoids
pool lifecycle bugs. If DATABASE_URL isn't configured or Postgres isn't
reachable, callers degrade gracefully (history just isn't persisted)
instead of the whole API failing to start.
"""

from __future__ import annotations

import json

import psycopg

from app.config import DATABASE_URL

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    country_iso3 TEXT NOT NULL,
    country_name TEXT NOT NULL,
    requested_year INTEGER NOT NULL,
    data_year_used INTEGER NOT NULL,
    is_hypothetical BOOLEAN NOT NULL,
    predicted_risk TEXT NOT NULL,
    probabilities JSONB NOT NULL,
    features_used JSONB NOT NULL
);
"""


def is_configured() -> bool:
    return bool(DATABASE_URL)


def check_connection() -> bool:
    if not DATABASE_URL:
        return False
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
            conn.execute("SELECT 1")
        return True
    except psycopg.OperationalError:
        return False


def init_db() -> None:
    if not DATABASE_URL:
        return
    with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
        conn.execute(CREATE_TABLE_SQL)


def insert_prediction(record: dict) -> None:
    if not DATABASE_URL:
        return
    with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
        conn.execute(
            """
            INSERT INTO predictions
                (country_iso3, country_name, requested_year, data_year_used,
                 is_hypothetical, predicted_risk, probabilities, features_used)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                record["country_iso3"],
                record["country_name"],
                record["requested_year"],
                record["data_year_used"],
                record["is_hypothetical"],
                record["predicted_risk"],
                json.dumps(record["probabilities"]),
                json.dumps(record["features_used"]),
            ),
        )


def fetch_history(limit: int = 50) -> list[dict]:
    if not DATABASE_URL:
        return []
    with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, country_iso3, country_name, requested_year,
                   data_year_used, is_hypothetical, predicted_risk, probabilities
            FROM predictions
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "id": r[0],
            "created_at": r[1].isoformat(),
            "country_iso3": r[2],
            "country_name": r[3],
            "requested_year": r[4],
            "data_year_used": r[5],
            "is_hypothetical": r[6],
            "predicted_risk": r[7],
            "probabilities": r[8],
        }
        for r in rows
    ]
