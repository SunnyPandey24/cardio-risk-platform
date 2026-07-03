# 🫀 Cardiovascular Disease Risk Analysis — Full Data Platform

A complete data engineering + ML platform built on top of a cardiovascular risk analysis:
ETL pipeline, orchestration, a trained and tracked ML model, a live FastAPI backend with
auth and a database, containerized deployment, CI/CD, and monitoring — plus the original
interactive dashboard as the front end.

**See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full system diagram and how every
layer fits together.**

> **Note on data:** the original repo this was rebuilt from doesn't host a raw dataset
> (only screenshots/PDFs). This project ships a **synthetic 70,000-row dataset** generated
> to match the real Kaggle "Cardiovascular Disease" dataset's schema and statistical
> relationships, so every layer — SQL, notebook, model, API, pipeline — runs end-to-end for
> real. Swap in the real `cardio_train.csv` (same columns) and everything still works
> unchanged.

## What's in this platform

| Layer | What it does | Where |
|---|---|---|
| Data & analysis | Cleaning, feature engineering, SQL KPIs, executed notebook, Excel workbook | `data/`, `sql/`, `python_analysis/`, `excel/` |
| **Backend API** | FastAPI service serving live predictions, JWT auth, history | `backend/` |
| **Database** | SQLite (local) / Postgres (production) via SQLAlchemy | `backend/app/models.py`, `docker-compose.yml` |
| **Orchestration** | Prefect flow (runnable now) + Airflow DAG (production reference) automating the full pipeline | `pipeline/` |
| **MLOps** | MLflow experiment tracking + model registry | `mlops/` |
| **Monitoring** | Prometheus metrics + Grafana dashboards | `monitoring/`, `docker-compose.yml` |
| **CI/CD** | Auto-tests the pipeline and backend; builds/pushes Docker images | `.github/workflows/` |
| **Dashboard** | Interactive frontend with dark mode, patient explorer, model lab, and a risk calculator that can call the live API | `dashboard/`, `docs/` |

## Quick start

```bash
# Everything at once (API + Postgres + Prometheus + Grafana)
docker-compose up --build
# → API: http://localhost:8000/docs
# → Prometheus: http://localhost:9090
# → Grafana: http://localhost:3000 (admin/admin)

# Or just the API, locally, no Docker
cd backend
pip install -r requirements.txt
cp ../model/model_results.json app/model_results.json
uvicorn app.main:app --reload

# Run the full automated pipeline (data -> clean -> train -> track -> report)
cd pipeline
pip install -r requirements.txt
python3 prefect_flow.py

# View tracked ML experiments
cd mlops
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Then open `docs/index.html` (or `dashboard/dashboard.html`), go to the **Risk Calculator**
tab, toggle **"Use live backend API"**, and point it at `http://localhost:8000` — the
dashboard now calls your real backend for predictions instead of computing them in the
browser.

## What's new vs. the original project

| Original project | This rebuild |
|---|---|
| Excel cleaning + static screenshots | Same cleaning logic, **fully scripted & reproducible** |
| SQL KPI queries | Same KPIs, **tested and validated** against real query output |
| Jupyter notebook (EDA + hypothesis tests) | Same tests, **executed with real results and saved charts** |
| Power BI dashboard (static screenshots) | **Interactive HTML dashboard** (works in any browser, no BI license needed) |
| Risk scoring model (rule-based, in Power BI) | Rule-based score **plus a trained Logistic Regression / Random Forest model** (ROC-AUC 0.73) |
| — | **Live risk calculator** — enter your own stats, get an instant ML-predicted risk % |
| — | **Patient Explorer** — searchable, sortable, filterable table of 300 real sampled patients |
| — | **Model Lab** — live ROC curve + an interactive confusion matrix with a draggable decision threshold |
| — | **Radar chart** comparing any calculator profile against the population average, with a "save & compare" mode |
| — | **Age vs. blood-pressure scatter plot** (bubble size = BMI) colored by disease outcome |
| — | **Dark mode**, animated KPI counters, scroll-reveal animations, and a print/export view |
| — | Feature importance & ROC curve analysis |
| — | Data-quality injection + cleaning validation (duplicates, nulls, sign errors, unit errors) |

### Dashboard tabs
1. **Executive Overview** — animated KPIs, age/gender breakdowns, key insights
2. **Clinical Deep Dive** — BP, BMI, cholesterol, lifestyle factors, feature importance
3. **Risk Segmentation** — risk-tier progression, age-vs-BP scatter, model performance summary
4. **Patient Explorer** — search/sort/filter a real 300-patient sample, see model predictions vs. actual outcomes
5. **Model Lab** — live ROC curve + interactive confusion matrix (drag the threshold slider)
6. **Risk Calculator** — live ML-powered estimate with a population-comparison radar chart, profile-save/compare, and a toggle to switch between the in-browser model and your **live FastAPI backend**

## Project structure

```
cardio/
├── .github/workflows/
│   ├── ci.yml                        # tests the full pipeline + backend on every push
│   └── docker-build.yml              # builds & pushes the API image to GHCR
├── data/
│   ├── generate_data.py              # synthetic data generator (70,000 records)
│   ├── clean_and_engineer.py         # cleaning + feature engineering (BMI, risk score, etc.)
│   ├── cardio_raw.csv                # raw data (with intentional messiness)
│   └── excel_cleaned_cardio_data.csv # cleaned, feature-engineered dataset
├── sql/
│   ├── schema.sql                    # table schema + indexes
│   └── kpi_queries.sql               # 11 KPI/analysis queries (validated)
├── python_analysis/
│   ├── build_notebook.py             # generates the notebook programmatically
│   ├── Cardio_Statistical_Analysis.ipynb   # EXECUTED notebook: EDA, hypothesis tests, ANOVA, ML
│   └── bmi_outliers.png, eda_age_bp.png, correlation_heatmap.png, roc_curve.png, feature_importance.png
├── model/
│   ├── train_model.py                # trains Logistic Regression + Random Forest
│   └── model_results.json            # metrics + portable coefficients
├── excel/
│   ├── build_excel.py
│   └── cardio_project.xlsx           # KPI Dashboard, Age-Group pivot, charts — all live formulas
├── backend/                          # FastAPI service: live predictions, auth, history
│   ├── app/ (main.py, models.py, schemas.py, auth.py, ml.py, database.py, config.py)
│   ├── tests/test_api.py             # 6 passing pytest tests
│   ├── Dockerfile
│   └── requirements.txt
├── pipeline/                         # orchestration
│   ├── prefect_flow.py               # runnable now — automates the full pipeline
│   ├── dags/cardio_pipeline_dag.py   # Airflow DAG reference for production
│   └── requirements.txt
├── mlops/                            # experiment tracking + model registry
│   ├── train_with_mlflow.py
│   └── requirements.txt
├── monitoring/
│   └── prometheus.yml                # scrape config for the API's /metrics
├── dashboard/dashboard.html          # interactive dashboard (works standalone)
├── docs/index.html                   # same dashboard, served by GitHub Pages
├── docker-compose.yml                # API + Postgres + Prometheus + Grafana, all wired together
├── render.yaml                       # one-click cloud deploy config
├── requirements.txt                  # data science pipeline dependencies
├── ARCHITECTURE.md                   # full system diagram and explanation
├── CLOUD_DEPLOY.md                   # deploying the API to Render / Railway / AWS
├── DEPLOYMENT.md                     # hosting the dashboard on GitHub Pages
└── README.md
```

## How to reproduce

```bash
# Core data + analysis pipeline
cd data && python3 generate_data.py && python3 clean_and_engineer.py
cd ../model && python3 train_model.py
cd ../python_analysis && python3 build_notebook.py && \
  jupyter nbconvert --to notebook --execute --inplace Cardio_Statistical_Analysis.ipynb
cd ../excel && python3 build_excel.py

# Or run the whole thing as one orchestrated pipeline
cd ../pipeline && pip install -r requirements.txt && python3 prefect_flow.py

# Backend API
cd ../backend && pip install -r requirements.txt
cp ../model/model_results.json app/model_results.json
uvicorn app.main:app --reload

# Everything containerized
docker-compose up --build
```

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for what each layer does and how they connect.

## Key findings (validated against the generated dataset, n=70,001)

- **Overall disease rate: 51.2%**
- **Blood pressure is the strongest predictor** — Hypertensive Crisis patients: 93% disease
  rate vs. 32% for Normal BP; confirmed by Random Forest feature importance (ap_hi = 34%,
  ap_lo = 23% of total importance).
- **Age matters a lot**: disease rate rises from 26.7% (under 40) to 65.9% (60+).
- **BMI compounds risk**: Severely Obese patients show 69.8% disease rate vs. 30.9% for
  Underweight.
- **Risk-tier scoring works**: the composite score cleanly separates patients into
  Low (25.8%) → Medium (54.1%) → High (77.7%) → Critical (90.5%) disease rates.
- **Statistical significance confirmed**: t-test on systolic BP (p < 0.001), ANOVA on risk
  score across BMI categories (p < 0.001), Chi-square on cholesterol vs. disease (p < 0.001).
- **ML model performance**: Logistic Regression and Random Forest both reach **ROC-AUC ≈ 0.73**,
  in line with published results on the real Kaggle dataset (typical range 0.72–0.80).

## Recommendations

- Prioritize blood-pressure screening, especially for patients 50+
- Flag and closely monitor the combined BP + high-cholesterol risk group
- Promote weight-management programs — BMI is the #3 predictor
- Use the risk-tier score to triage outreach: re-screen High/Critical tier patients quarterly

## Using your own data

Everything downstream of `excel_cleaned_cardio_data.csv` only depends on these 13 raw columns:
`age (days), gender (1/2), height (cm), weight (kg), ap_hi, ap_lo, cholesterol (1-3), gluc (1-3),
smoke (0/1), alco (0/1), active (0/1), cardio (0/1)` — exactly the Kaggle
`cardio_train.csv` schema. Replace `data/cardio_raw.csv` with the real file (or point
`clean_and_engineer.py` at it) and re-run the pipeline; the notebook, SQL, Excel workbook and
dashboard all update automatically.

## Disclaimer

This is an analytics/demo project, not a medical device. The risk calculator gives a
statistical estimate from a model trained on synthetic data — it is not a diagnosis.

## Deploying this project

See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for a full step-by-step guide to pushing this to
GitHub and hosting the live dashboard for free with GitHub Pages.
