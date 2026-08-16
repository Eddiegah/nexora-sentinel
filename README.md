# Nexora Sentinel

Malaria outbreak risk prediction for Africa, trained end-to-end on real public health and demographic data — no synthetic data, no fabricated metrics. Every number in this README is reproducible by re-running the pipeline in `ml/`.

## What it does

Given a country and year, Nexora Sentinel predicts a malaria risk class (**Low / Medium / High**) using an XGBoost classifier trained on WHO malaria incidence data and World Bank demographic/infrastructure indicators, and explains *why* using SHAP. Users can also run "what-if" scenarios by overriding individual feature values (e.g. "what if sanitation access improved to 90%?") to see how the prediction shifts.

## Data sources

Both are free, public, and require no API key:

| Source | What | Link |
|---|---|---|
| WHO Global Health Observatory | Estimated malaria incidence (per 1,000 population at risk) — the prediction target | [ghoapi.azureedge.net](https://ghoapi.azureedge.net/api/MALARIA_EST_INCIDENCE) |
| World Bank Open Data | Urban/rural population %, population growth, urban growth, water access %, sanitation access % — the model's features | [api.worldbank.org](https://api.worldbank.org/v2/country) |

Coverage: **45 African countries, years 2000–2024, 1,101 country-year records** after joining and cleaning. Full methodology, including exact indicator codes and dropped-row counts, is in [`data/processed/methodology.json`](data/processed/methodology.json).

## Methodology, honestly

**Risk labels are not an official WHO classification.** There is no single standard 3-tier malaria risk scale usable directly for ML. This project bins the real incidence values in this dataset into tertiles (bottom third = Low, middle third = Medium, top third = High). The exact cutpoints are written to `methodology.json` for full reproducibility — this is a modeling choice, disclosed as such, not a clinical standard.

**Two evaluations are reported, not one.** For year-over-year data like this, a random train/test split lets the model see e.g. Ghana-2015 in training and Ghana-2016 in test — adjacent years are highly correlated, so a random split tends to look better than the model's real forecasting ability. A temporal holdout (train on 2000–2019, test on 2020–2024) is the harder, more honest number and the one that actually matches a "predict future risk" framing.

| Model | Evaluation | Accuracy |
|---|---|---|
| Logistic Regression | Random 80/20 split | 62.4% |
| XGBoost | Random 80/20 split | 95.5% |
| **XGBoost** | **Temporal holdout (train <2020, test ≥2020)** | **81.0%** |

The temporal holdout figure is the one that should be trusted as representative of real predictive performance. Full metrics: [`docs/metrics.json`](docs/metrics.json).

**Explainability is real, not illustrative.** SHAP (TreeExplainer) values are computed against the actual trained model and served per-prediction via the API. Summary plot: [`docs/shap_summary.png`](docs/shap_summary.png).

### A known limitation

The current feature set is demographic/infrastructure-based (urbanization, water/sanitation access, population growth). Real-world malaria transmission is also strongly driven by climate factors — rainfall, temperature, humidity — which aren't in this dataset yet. This is a reasonable v1 given the free, no-key-required data sources used, but climate data (e.g. from NOAA or a similar source) would likely be the single biggest improvement to prediction quality.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌────────────┐
│  Next.js     │ HTTP │  FastAPI      │ SQL  │ PostgreSQL │
│  dashboard   │─────▶│  backend      │─────▶│  history   │
│  (port 3000) │      │  (port 8000)  │      │ (port 5432)│
└─────────────┘      └──────┬───────┘      └────────────┘
                             │ loads once at startup
                             ▼
                   XGBoost model + SHAP explainer
                   (trained offline in ml/, artifacts
                    committed to ml/artifacts/)
```

## Tech stack

- **ML**: pandas, scikit-learn, XGBoost, SHAP
- **Backend**: FastAPI, psycopg (PostgreSQL), Pydantic
- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS
- **Infra**: Docker Compose (Postgres + backend + frontend)

## Running it

### Option A: Docker Compose (recommended)

```bash
docker compose up -d
```

Starts Postgres, the backend on `http://localhost:8000`, and the frontend on `http://localhost:3000`. First run builds both images (a few minutes); subsequent runs are fast.

### Option B: Manual local dev

```bash
# ML pipeline (only needed if you want to regenerate data/model from scratch)
cd ml && pip install -r requirements.txt
python collect_data.py    # fetch + cache real WHO/World Bank data
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

### Option C: Deploy your own copy (Render + Vercel, both free)

This is how to get a public URL you can share. Both platforms deploy straight from this GitHub repo — no local build step needed.

**1. Backend + database, on Render**

- Sign in to [Render](https://render.com) with GitHub.
- **New +** → **Blueprint** → select this repo. Render reads [`render.yaml`](render.yaml) and provisions a free web service (`nexora-sentinel-backend`) and a free Postgres database automatically.
- Click **Apply**. First build takes a few minutes.
- Once live, confirm at `https://nexora-sentinel-backend.onrender.com/health` — expect `{"status":"ok","model_loaded":true,"db_connected":true}`.
- If Render assigned a different URL (the exact name can be taken), note it — you'll need it in step 2.

**2. Frontend, on Vercel**

- Sign in to [Vercel](https://vercel.com) with GitHub.
- **Add New** → **Project** → import this repo.
- Set **Root Directory** to `frontend` (the one manual setting required).
- Deploy. `frontend/.env.production` already points at `https://nexora-sentinel-backend.onrender.com`, so no environment variables are needed *unless* Render gave you a different URL — in that case, add `NEXT_PUBLIC_API_URL` under Project Settings → Environment Variables and redeploy.
- Your shareable link is the `https://<project>.vercel.app` URL Vercel gives you.

**Known free-tier tradeoffs** (worth knowing before you share the link):
- Render's free web service spins down after 15 minutes of no traffic and takes about a minute to wake up — the first request after a quiet period will be slow, not broken.
- Render's free Postgres database expires 30 days after creation (14-day grace period after that before deletion). The app still works fine without a database — predictions just won't persist to `/history`. Recreate the database blueprint if you want history back after expiry.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | API/model/DB status |
| `/countries` | GET | List of 45 countries with years of available data |
| `/predict` | POST | Predict risk for a country/year, with optional what-if feature overrides |
| `/history` | GET | Recent predictions (requires DB) |

Interactive docs at `http://localhost:8000/docs` once the backend is running.

## Project structure

```
ml/                  Data collection, dataset build, training, SHAP
  collect_data.py     Fetches + caches real WHO/World Bank data
  build_dataset.py     Joins, cleans, engineers risk labels
  train.py              Trains + evaluates (random split + temporal holdout)
  explain.py             Computes real SHAP values
  artifacts/            Trained model, encoders, SHAP explainer (committed)
backend/              FastAPI service
frontend/             Next.js dashboard
data/processed/       Cleaned dataset + methodology.json
docs/                 metrics.json, shap_summary.png
docker-compose.yml
```

## License

MIT — see [LICENSE](LICENSE).
