"""
Thin PostgreSQL layer for prediction history. Uses a fresh connection per
call rather than a pool -- appropriate at this project's scale, and avoids
pool lifecycle bugs. If DATABASE_URL isn't configured or Postgres isn't
reachable, callers degrade gracefully (history just isn't persisted)
instead of the whole API failing to start.
"""

from __future__ import annotations

import json
import secrets

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
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS is_forecast BOOLEAN NOT NULL DEFAULT false;

CREATE TABLE IF NOT EXISTS alert_subscriptions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    email TEXT NOT NULL,
    country_iso3 TEXT NOT NULL,
    country_name TEXT NOT NULL,
    unsubscribe_token TEXT NOT NULL UNIQUE,
    last_notified_risk TEXT,
    last_checked_at TIMESTAMPTZ,
    UNIQUE (email, country_iso3)
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
                 is_hypothetical, is_forecast, predicted_risk, probabilities, features_used)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                record["country_iso3"],
                record["country_name"],
                record["requested_year"],
                record["data_year_used"],
                record["is_hypothetical"],
                record["is_forecast"],
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
                   data_year_used, is_hypothetical, is_forecast, predicted_risk, probabilities
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
            "is_forecast": r[7],
            "predicted_risk": r[8],
            "probabilities": r[9],
        }
        for r in rows
    ]


def insert_subscription(email: str, country_iso3: str, country_name: str) -> str:
    """Upserts a (email, country) subscription. Returns the unsubscribe
    token -- stable across resubscribes since ON CONFLICT never touches it."""
    if not DATABASE_URL:
        raise RuntimeError("Database is not configured")
    token = secrets.token_urlsafe(24)
    with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
        row = conn.execute(
            """
            INSERT INTO alert_subscriptions (email, country_iso3, country_name, unsubscribe_token)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email, country_iso3) DO UPDATE SET country_name = EXCLUDED.country_name
            RETURNING unsubscribe_token
            """,
            (email, country_iso3, country_name, token),
        ).fetchone()
    return row[0]


def delete_subscription_by_token(token: str) -> bool:
    if not DATABASE_URL:
        return False
    with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
        cur = conn.execute("DELETE FROM alert_subscriptions WHERE unsubscribe_token = %s", (token,))
        return cur.rowcount > 0


def list_subscriptions() -> list[dict]:
    if not DATABASE_URL:
        return []
    with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
        rows = conn.execute(
            """
            SELECT id, email, country_iso3, country_name, unsubscribe_token, last_notified_risk
            FROM alert_subscriptions
            """
        ).fetchall()
    return [
        {
            "id": r[0],
            "email": r[1],
            "country_iso3": r[2],
            "country_name": r[3],
            "unsubscribe_token": r[4],
            "last_notified_risk": r[5],
        }
        for r in rows
    ]


def record_subscription_check(sub_id: int, current_risk: str) -> None:
    """Always records the risk seen at this check (regardless of whether an
    email was sent) -- this is what lets a later High->Medium->High cycle
    trigger a fresh notification instead of staying silent forever after
    the first alert."""
    if not DATABASE_URL:
        return
    with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
        conn.execute(
            "UPDATE alert_subscriptions SET last_notified_risk = %s, last_checked_at = now() WHERE id = %s",
            (current_risk, sub_id),
        )
