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
