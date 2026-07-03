import time
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from .database import Base, engine, get_db
from . import models, schemas, auth, ml
from .config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cardiovascular Risk API",
    description="Live ML-powered cardiovascular risk prediction service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUEST_COUNT = Counter("api_requests_total", "Total API requests", ["endpoint", "method", "status"])
REQUEST_LATENCY = Histogram("api_request_latency_seconds", "Request latency", ["endpoint"])
PREDICTIONS_BY_TIER = Counter("predictions_by_tier_total", "Predictions issued by risk tier", ["tier"])

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(elapsed)
    REQUEST_COUNT.labels(endpoint=request.url.path, method=request.method, status=response.status_code).inc()
    return response

@app.get("/health", tags=["ops"])
def health():
    return {"status": "ok", "model_version": ml.MODEL_VERSION}

@app.get("/metrics", tags=["ops"])
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ---------------- Auth ----------------

@app.post("/auth/signup", response_model=schemas.UserOut, tags=["auth"])
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(email=payload.email, hashed_password=auth.hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=schemas.Token, tags=["auth"])
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.UserOut, tags=["auth"])
def me(user=Depends(auth.require_user)):
    return user

# ---------------- Risk prediction ----------------

@app.post("/predict", response_model=schemas.RiskOutput, tags=["risk"])
def predict(payload: schemas.RiskInput, db: Session = Depends(get_db), user=Depends(auth.get_current_user)):
    bmi = ml.compute_bmi(payload.height, payload.weight)
    prob = ml.predict_probability(
        payload.age, payload.gender, bmi, payload.ap_hi, payload.ap_lo,
        payload.cholesterol, payload.gluc, payload.smoke, payload.alco, payload.active,
    )
    tier, recommendation = ml.risk_tier(prob)
    PREDICTIONS_BY_TIER.labels(tier=tier).inc()

    record = models.RiskAssessment(
        user_id=user.id if user else None,
        age=payload.age, gender=payload.gender, height=payload.height, weight=payload.weight, bmi=round(bmi, 1),
        ap_hi=payload.ap_hi, ap_lo=payload.ap_lo, cholesterol=payload.cholesterol, gluc=payload.gluc,
        smoke=payload.smoke, alco=payload.alco, active=payload.active,
        predicted_probability=round(prob, 4), risk_tier=tier, model_version=ml.MODEL_VERSION,
    )
    db.add(record)
    db.commit()

    return schemas.RiskOutput(
        predicted_probability=round(prob, 4),
        risk_percent=round(prob * 100, 1),
        risk_tier=tier,
        bmi=round(bmi, 1),
        model_version=ml.MODEL_VERSION,
        recommendation=recommendation,
    )

@app.get("/history", response_model=List[schemas.AssessmentHistoryItem], tags=["risk"])
def history(user=Depends(auth.require_user), db: Session = Depends(get_db)):
    return (
        db.query(models.RiskAssessment)
        .filter(models.RiskAssessment.user_id == user.id)
        .order_by(models.RiskAssessment.created_at.desc())
        .limit(50)
        .all()
    )

@app.get("/stats/summary", tags=["risk"])
def stats_summary(db: Session = Depends(get_db)):
    total = db.query(func.count(models.RiskAssessment.id)).scalar() or 0
    by_tier = (
        db.query(models.RiskAssessment.risk_tier, func.count(models.RiskAssessment.id))
        .group_by(models.RiskAssessment.risk_tier)
        .all()
    )
    return {"total_predictions_served": total, "by_tier": {t: c for t, c in by_tier}}
