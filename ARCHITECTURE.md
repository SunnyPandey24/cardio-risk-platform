# System Architecture

This project is now a full, layered data platform — not just an analysis notebook. This
document explains how the pieces fit together.

```
                                   ┌─────────────────────────┐
                                   │   Interactive Dashboard  │
                                   │  (docs/index.html)       │
                                   │  Charts · Explorer ·     │
                                   │  Risk Calculator         │
                                   └────────────┬─────────────┘
                                                │ fetch() — optional live mode
                                                ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                            FastAPI Backend (backend/)                     │
│  /predict   /auth/signup  /auth/login  /history  /stats/summary           │
│  /health    /metrics (Prometheus)                                         │
│  JWT auth · Pydantic validation · SQLAlchemy ORM                          │
└───────────────────────────┬─────────────────────────────┬────────────────┘
                             │                             │
                             ▼                             ▼
                  ┌───────────────────┐         ┌────────────────────────┐
                  │  Postgres (prod)   │         │  Prometheus + Grafana  │
                  │  SQLite (local)    │         │  (monitoring/)         │
                  │  Users, assessments│         │  Request rate, latency,│
                  └───────────────────┘         │  predictions by tier   │
                                                  └────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                    Orchestration Layer (pipeline/)                        │
│  Prefect flow (runnable locally) — mirrors an Airflow DAG (production)    │
│  generate_data → clean_and_engineer → train_model → track (MLflow) → excel│
└───────────────────────────┬───────────────────────────────────────────────┘
                             ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                       MLOps Layer (mlops/)                                │
│  MLflow experiment tracking · model registry · versioned metrics          │
│  train_with_mlflow.py logs Logistic Regression + Random Forest runs,      │
│  registers the best model as "cardio-risk-model"                          │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                        CI/CD (.github/workflows/)                         │
│  ci.yml              — re-runs the full data + notebook + Excel pipeline  │
│                         and the backend test suite, on every push         │
│  docker-build.yml     — builds the API image, pushes to GHCR, optionally  │
│                         triggers a Render deploy hook                     │
└───────────────────────────────────────────────────────────────────────────┘
```

## Layer-by-layer

### 1. Data & analysis (`data/`, `sql/`, `python_analysis/`, `excel/`)
Unchanged from the original analysis project — synthetic data generation, cleaning,
feature engineering, SQL KPIs, a fully executed Jupyter notebook, and an Excel workbook
with live formulas. This is the foundation everything else is built on.

### 2. Backend API (`backend/`)
A FastAPI service that serves live predictions instead of relying on client-side
JavaScript math. Key pieces:
- `app/ml.py` — loads the trained logistic regression coefficients and serves predictions
- `app/models.py` / `app/database.py` — SQLAlchemy ORM, works with SQLite locally or
  Postgres in production (same code, different `DATABASE_URL`)
- `app/auth.py` — JWT-based authentication so users can optionally create an account and
  save their risk-assessment history
- `app/main.py` — the FastAPI app: `/predict`, `/auth/signup`, `/auth/login`, `/history`,
  `/stats/summary`, `/health`, `/metrics`
- `tests/test_api.py` — pytest suite covering health, prediction, auth, and history
  (6 tests, all passing)

Run it locally:
```bash
cd backend
pip install -r requirements.txt
cp ../model/model_results.json app/model_results.json
uvicorn app.main:app --reload
# → http://localhost:8000/docs for interactive API documentation
```

### 3. Database
SQLite by default (zero setup, good for local dev and demos). `docker-compose.yml` runs a
real Postgres instance for production-like usage — same SQLAlchemy code, just point
`DATABASE_URL` at Postgres instead.

### 4. Orchestration (`pipeline/`)
`prefect_flow.py` automates the entire pipeline: generate data → clean → train → track →
rebuild reports. It's runnable today with `python3 pipeline/prefect_flow.py` — no server
setup required. `dags/cardio_pipeline_dag.py` is the same pipeline expressed as an Airflow
DAG, included because many data teams standardize on Airflow specifically — swap in
whichever orchestrator your environment uses.

### 5. MLOps (`mlops/`)
`train_with_mlflow.py` trains both models, logs every parameter and metric to MLflow, and
registers the best-performing model in MLflow's model registry with a version number. View
the tracked experiments:
```bash
cd mlops
mlflow ui --backend-store-uri sqlite:///mlflow.db
# → http://localhost:5000
```

### 6. Monitoring (`monitoring/`)
The API exposes Prometheus-format metrics at `/metrics` — request counts, latency
histograms, and predictions-by-risk-tier counters. `docker-compose.yml` wires up
Prometheus (scrapes the API) and Grafana (visualizes it) automatically.

### 7. CI/CD (`.github/workflows/`)
- `ci.yml` — runs the full data pipeline and the backend test suite on every push, so a
  green checkmark actually means something
- `docker-build.yml` — builds and publishes the API as a Docker image to GitHub Container
  Registry, with an optional webhook to trigger a Render redeploy

### 8. Deployment
See [`CLOUD_DEPLOY.md`](./CLOUD_DEPLOY.md) for taking the backend live on Render, Railway,
or AWS, and [`DEPLOYMENT.md`](./DEPLOYMENT.md) for the GitHub + GitHub Pages setup for the
static dashboard.

## Running everything at once

```bash
docker-compose up --build
```
This starts the API (port 8000), Postgres (port 5432), Prometheus (port 9090), and Grafana
(port 3000) together, all wired to talk to each other.
