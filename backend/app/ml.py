import json
import math
import os
from .config import settings

def _load_model():
    path = settings.MODEL_PATH
    candidates = [path, os.path.join(os.path.dirname(__file__), path)]
    for c in candidates:
        if os.path.exists(c):
            with open(c) as f:
                return json.load(f)
    raise FileNotFoundError(f"Could not locate model_results.json (tried {candidates})")

_MODEL = _load_model()
_CALC = _MODEL["calculator_model"]
_COEFS = _CALC["coefficients"]
_INTERCEPT = _CALC["intercept"]
MODEL_VERSION = "logreg_v1_auc" + str(_CALC.get("roc_auc", ""))

def compute_bmi(height_cm: float, weight_kg: float) -> float:
    return weight_kg / ((height_cm / 100) ** 2)

def predict_probability(age, gender, bmi, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active) -> float:
    z = (
        _INTERCEPT
        + _COEFS["age"] * age
        + _COEFS["gender"] * gender
        + _COEFS["bmi"] * bmi
        + _COEFS["ap_hi"] * ap_hi
        + _COEFS["ap_lo"] * ap_lo
        + _COEFS["cholesterol"] * cholesterol
        + _COEFS["gluc"] * gluc
        + _COEFS["smoke"] * smoke
        + _COEFS["alco"] * alco
        + _COEFS["active"] * active
    )
    return 1 / (1 + math.exp(-z))

def risk_tier(prob: float):
    if prob < 0.35:
        return "Low", "Risk factors are largely favorable. Maintain current habits and routine annual checkups."
    if prob < 0.55:
        return "Medium", "Some risk factors are elevated. Consider a clinical check on blood pressure and cholesterol."
    if prob < 0.75:
        return "High", "Multiple risk factors present. A clinical consultation is recommended."
    return "Critical", "Risk factors are strongly elevated. Prompt clinical evaluation is recommended."
