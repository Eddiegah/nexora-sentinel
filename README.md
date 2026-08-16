# Nexora Sentinel

Malaria outbreak risk prediction for Africa, trained end-to-end on real public health, demographic, and climate data — no synthetic data, no fabricated metrics. Every number in this README is reproducible by re-running the pipeline in `ml/`.

**Live**: [nexora-sentinel.vercel.app](https://nexora-sentinel.vercel.app) &middot; API: [nexora-sentinel-backend.onrender.com/docs](https://nexora-sentinel-backend.onrender.com/docs)

## What it does

Given a country and year, Nexora Sentinel predicts a malaria risk class (**Low / Medium / High**) using an XGBoost classifier trained on WHO malaria incidence data, World Bank demographic/infrastructure indicators, and NASA climate data, and explains *why* using SHAP. Three views:

- **Predict** — pick a country/year, get a prediction with a SHAP breakdown. "What-if" overrides let you change individual feature values (e.g. "what if sanitation access improved to 90%?") to see how the prediction shifts.
- **Country Trend** — predicted risk for every year 2000–2024 for one country, showing how risk has actually evolved.
- **Africa Overview** — predicted risk for all 45 countries at once, sorted by severity.

## Data sources

All free, public, and require no API key:

| Source | What | Link |
|---|---|---|
| WHO Global Health Observatory | Estimated malaria incidence (per 1,000 population at risk) — the prediction target | [ghoapi.azureedge.net](https://ghoapi.azureedge.net/api/MALARIA_EST_INCIDENCE) |
| World Bank Open Data | Urban/rural population %, population growth, urban growth, water access %, sanitation access % | [api.worldbank.org](https://api.worldbank.org/v2/country) |
| NASA POWER | Annual average temperature and precipitation | [power.larc.nasa.gov](https://power.larc.nasa.gov/api/temporal/monthly/point) |

Coverage: **45 African countries, years 2000–2024, 1,101 country-year records** after joining and cleaning. Full methodology, including exact indicator codes and dropped-row counts, is in [`data/processed/methodology.json`](data/processed/methodology.json).

## Methodology, honestly

**Risk labels are not an official WHO classification.** There is no single standard 3-tier malaria risk scale usable directly for ML. This project bins the real incidence values in this dataset into tertiles (bottom third = Low, middle third = Medium, top third = High). The exact cutpoints are written to `methodology.json` for full reproducibility — this is a modeling choice, disclosed as such, not a clinical standard.

**Two evaluations are reported, not one.** For year-over-year data like this, a random train/test split lets the model see e.g. Ghana-2015 in training and Ghana-2016 in test — adjacent years are highly correlated, so a random split tends to look better than the model's real forecasting ability. A temporal holdout (train on 2000–2019, test on 2020–2024) is the harder, more honest number and the one that actually matches a "predict future risk" framing.

| Model | Evaluation | Accuracy |
|---|---|---|
| Logistic Regression | Random 80/20 split | 71.0% |
| XGBoost | Random 80/20 split | 93.7% |
| **XGBoost** | **Temporal holdout (train <2020, test ≥2020)** | **81.0%** |

The temporal holdout figure is the one that should be trusted as representative of real predictive performance. Full metrics: [`docs/metrics.json`](docs/metrics.json).

Adding real climate data measurably improved the honest baseline (Logistic Regression random-split accuracy rose from 62.4% to 71.0%); the temporal holdout figure held steady at 81.0% rather than improving, which is itself an honest result worth reporting rather than hiding — reported as computed, not adjusted to look better.

**Explainability is real, not illustrative.** SHAP (TreeExplainer) values are computed against the actual trained model and served per-prediction via the API. `avg_temperature_c` is the single most important feature in the model overall — more important than country identity — which is a real, scientifically grounded result: temperature is a well-established driver of mosquito vector survival and malaria parasite development rate. Summary plot: [`docs/shap_summary.png`](docs/shap_summary.png).

### Known limitations, disclosed

- **Climate data is a single representative point per country** (each capital city's coordinates — see [`ml/country_coords.py`](ml/country_coords.py)), not averaged across the whole country. Real climate varies within a country; this is a reasonable, transparent simplification given free, no-key data sources, not a hidden shortcut.
- Risk tertiles are computed from this dataset's own distribution, not a clinical standard (see above).

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌────────────┐
│  Next.js     │ HTTP │  FastAPI      │ SQL  │ PostgreSQL │
│  dashboard   │─────▶│  backend      │─────▶│  (Neon,    │
│  (Vercel)    │      │  (Render)     │      │  no expiry)│
└─────────────┘      └──────┬───────┘      └────────────┘
                             │ loads once at startup
                             ▼
                   XGBoost model + SHAP explainer
                   (trained offline in ml/, artifacts
                    committed to ml/artifacts/)

GitHub Actions pings /health every 10 min to keep the free
Render instance warm (avoids cold-start spin-down).
```

## Tech stack

- **ML**: pandas, scikit-learn, XGBoost, SHAP
- **Backend**: FastAPI, psycopg (PostgreSQL), Pydantic, slowapi (rate limiting)
- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS
- **Infra**: Docker Compose (local), Render + Vercel + Neon (deployed), GitHub Actions (keep-alive)

## Running it

### Option A: Docker Compose (recommended for local dev)

```bash
docker compose up -d
```

Starts Postgres, the backend on `http://localhost:8000`, and the frontend on `http://localhost:3000`. First run builds both images (a few minutes); subsequent runs are fast.

### Option B: Manual local dev

```bash
# ML pipeline (only needed if you want to regenerate data/model from scratch)
cd ml && pip install -r requirements.txt
python collect_data.py    # fetch + cache real WHO/World Bank data
python collect_climate.py # fetch + cache real NASA POWER climate data
python build_dataset.py   # join, clean, engineer risk labels
python train.py           # train + honestly evaluate the model
python explain.py         # compute real SHAP values

# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install
npm run dev
```

The backend works without a database configured — `/predict` still returns predictions, it just skips writing to history and `/health` reports `db_connected: false`. To enable history, copy `backend/.env.example` to `backend/.env` and point `DATABASE_URL` at a running Postgres instance.

### Option C: Deploy your own copy (Render + Vercel + Neon, all free, no expiry)

**1. Database, on Neon**

- Sign in to [Neon](https://neon.tech) with GitHub, create a free project.
- Copy the connection string it gives you (starts with `postgresql://`).
- Neon's free tier doesn't have a hard expiry date, unlike Render's own free Postgres.

**2. Backend, on Render**

- Sign in to [Render](https://render.com) with GitHub.
- **New +** → **Blueprint** → select this repo. Render reads [`render.yaml`](render.yaml) and provisions a free web service (`nexora-sentinel-backend`).
- Click **Apply**. First build takes a few minutes.
- Once created, go to the service's **Environment** tab and set `DATABASE_URL` to the Neon connection string from step 1 (this is marked `sync: false` in `render.yaml` specifically so it's set once, manually, here — never commit a real connection string to the repo).
- Confirm at `https://nexora-sentinel-backend.onrender.com/health` — expect `{"status":"ok","model_loaded":true,"db_connected":true}`.

**3. Frontend, on Vercel**

- Sign in to [Vercel](https://vercel.com) with GitHub.
- **Add New** → **Project** → import this repo.
- Set **Root Directory** to `frontend` (the one manual setting required).
- Deploy. `frontend/.env.production` already points at `https://nexora-sentinel-backend.onrender.com`, so no environment variables are needed *unless* Render gave you a different URL — in that case, add `NEXT_PUBLIC_API_URL` under Project Settings → Environment Variables and redeploy.
- Your shareable link is the `https://<project>.vercel.app` URL Vercel gives you.

**4. Keep the backend warm (optional but recommended)**

[`.github/workflows/keepalive.yml`](.github/workflows/keepalive.yml) pings `/health` every 10 minutes via GitHub Actions (free, unlimited minutes on public repos) so the free Render instance never cold-starts for a visitor. It's already in this repo and runs automatically once pushed to GitHub — no setup needed. Uses close to the full 750 free instance-hours/month Render allows for one service, so avoid running other free Render web services on the same account alongside this one.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | API/model/DB status |
| `/countries` | GET | List of 45 countries with years of available data |
| `/predict` | POST | Predict risk for a country/year, with optional what-if feature overrides (rate limited: 30/min) |
| `/history` | GET | Recent predictions (requires DB) |
| `/overview` | GET | Predictions for all 45 countries at once (rate limited: 10/min) |
| `/trend` | GET | Predictions for every year available for one country (rate limited: 30/min) |

Interactive docs at `http://localhost:8000/docs` once the backend is running (or the live `/docs` link above).

## Project structure

```
ml/                    Data collection, dataset build, training, SHAP
  collect_data.py       Fetches + caches real WHO/World Bank data
  collect_climate.py     Fetches + caches real NASA POWER climate data
  country_coords.py       Capital-city coordinates used for climate queries
  build_dataset.py         Joins, cleans, engineers risk labels
  train.py                  Trains + evaluates (random split + temporal holdout)
  explain.py                 Computes real SHAP values
  artifacts/                Trained model, encoders, SHAP explainer (committed)
backend/                FastAPI service
frontend/               Next.js dashboard (Predict / Trend / Overview views)
data/processed/         Cleaned dataset + methodology.json
docs/                   metrics.json, shap_summary.png
docker-compose.yml
render.yaml             Render Blueprint (backend web service)
.github/workflows/      Keep-alive ping
```

## License

MIT — see [LICENSE](LICENSE).
