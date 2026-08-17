from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Local dev: backend/app/config.py -> parents[2] is the NexoraSentinel repo
# root, where ml/ and data/ are siblings of backend/. In Docker, the image
# instead copies ml/artifacts and data/processed flat under /app, so these
# paths are overridable via env vars to match that layout.
BASE_DIR = Path(__file__).resolve().parents[2]
ML_ARTIFACTS_DIR = Path(os.getenv("ML_ARTIFACTS_DIR", str(BASE_DIR / "ml" / "artifacts")))
PROCESSED_DATA_CSV = Path(os.getenv("PROCESSED_DATA_CSV", str(BASE_DIR / "data" / "processed" / "malaria_africa.csv")))

DATABASE_URL = os.getenv("DATABASE_URL", "")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Email alerts (all optional -- alerts silently no-op if RESEND_API_KEY isn't set)
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "Nexora Sentinel <onboarding@resend.dev>")
PUBLIC_BACKEND_URL = os.getenv("PUBLIC_BACKEND_URL", "https://nexora-sentinel-backend.onrender.com")
PUBLIC_FRONTEND_URL = os.getenv("PUBLIC_FRONTEND_URL", "https://nexora-sentinel.vercel.app")
# Shared secret required on /alerts/check so only the scheduled GitHub
# Actions job (or the operator) can trigger real email sends.
CRON_SECRET = os.getenv("CRON_SECRET", "")
