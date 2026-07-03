import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DATABASE_URL"] = "sqlite:///./test_cardio.db"

from app.main import app  # noqa: E402

client = TestClient(app)

VALID_PAYLOAD = {
    "age": 50, "gender": 2, "height": 175, "weight": 85,
    "ap_hi": 140, "ap_lo": 90, "cholesterol": 2, "gluc": 1,
    "smoke": 0, "alco": 0, "active": 1,
}

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_predict_returns_valid_risk():
    r = client.post("/predict", json=VALID_PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["predicted_probability"] <= 1
    assert body["risk_tier"] in ["Low", "Medium", "High", "Critical"]
    assert body["bmi"] > 0

def test_predict_rejects_invalid_input():
    bad = dict(VALID_PAYLOAD, age=5)  # below allowed range
    r = client.post("/predict", json=bad)
    assert r.status_code == 422

def test_signup_login_and_history_flow():
    email = "pytest_user@example.com"
    signup = client.post("/auth/signup", json={"email": email, "password": "testpass123"})
    assert signup.status_code in (200, 400)  # 400 if already exists from a prior run

    login = client.post("/auth/login", data={"username": email, "password": "testpass123"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    predict = client.post("/predict", json=VALID_PAYLOAD, headers=headers)
    assert predict.status_code == 200

    history = client.get("/history", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) >= 1

def test_history_requires_auth():
    r = client.get("/history")
    assert r.status_code == 401

def test_stats_summary_is_public():
    r = client.get("/stats/summary")
    assert r.status_code == 200
    assert "total_predictions_served" in r.json()

def teardown_module(module):
    for f in ("test_cardio.db",):
        path = os.path.join(os.path.dirname(__file__), "..", f)
        if os.path.exists(path):
            os.remove(path)
