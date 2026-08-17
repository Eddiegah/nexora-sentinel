"""
Sends real malaria risk alert emails via Resend's HTTP API. Plain requests
call, no SDK dependency, matching the project's minimal-dependency style.
Silently no-ops if RESEND_API_KEY isn't configured -- alerts are an
optional feature, not a hard dependency for the rest of the app.
"""

from __future__ import annotations

import logging

import requests

from app.config import PUBLIC_BACKEND_URL, PUBLIC_FRONTEND_URL, RESEND_API_KEY, RESEND_FROM_EMAIL

logger = logging.getLogger("nexora")

RESEND_URL = "https://api.resend.com/emails"


def is_configured() -> bool:
    return bool(RESEND_API_KEY)


def send_risk_alert(to_email: str, country_name: str, risk: str, year: int, unsubscribe_token: str) -> bool:
    """Returns True if the email was actually sent (2xx from Resend)."""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not configured -- skipping alert email to %s", to_email)
        return False

    unsubscribe_url = f"{PUBLIC_BACKEND_URL}/alerts/unsubscribe?token={unsubscribe_token}"
    dashboard_url = PUBLIC_FRONTEND_URL

    html = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
      <h2 style="color: #0f766e;">Nexora Sentinel Risk Alert</h2>
      <p>
        The predicted malaria outbreak risk for <strong>{country_name}</strong> in {year}
        has reached <strong style="color: #e11d48;">{risk}</strong>.
      </p>
      <p>
        <a href="{dashboard_url}" style="color: #0d9488;">View the full prediction and SHAP explanation &rarr;</a>
      </p>
      <p style="margin-top: 32px; font-size: 12px; color: #78716c;">
        This is a real model prediction based on real WHO, World Bank, and NASA climate data --
        not a public health advisory. Model accuracy on unseen future data is honestly reported
        as 81.0% (temporal holdout evaluation).
        <br /><br />
        <a href="{unsubscribe_url}" style="color: #78716c;">Unsubscribe from alerts for {country_name}</a>
      </p>
    </div>
    """

    try:
        resp = requests.post(
            RESEND_URL,
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={
                "from": RESEND_FROM_EMAIL,
                "to": [to_email],
                "subject": f"Malaria risk alert: {country_name} is now {risk} risk",
                "html": html,
            },
            timeout=15,
        )
        if resp.status_code >= 300:
            logger.error("Resend returned %s for %s: %s", resp.status_code, to_email, resp.text[:300])
            return False
        return True
    except requests.RequestException:
        logger.exception("Failed to send alert email to %s", to_email)
        return False
