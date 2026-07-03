"""
Generates a synthetic 70,000-row dataset that replicates the structure,
value ranges and feature-target relationships of the Kaggle
'Cardiovascular Disease' dataset used in the original project.
"""
import numpy as np
import pandas as pd

np.random.seed(42)
N = 70000

age_years = np.clip(np.random.normal(53, 6.7, N), 29, 65)
age_days = (age_years * 365.25).astype(int)

gender = np.random.choice([1, 2], N, p=[0.65, 0.35])  # 1=female,2=male

height = np.where(
    gender == 2,
    np.random.normal(169, 6.5, N),
    np.random.normal(161.5, 6.0, N),
)
weight = np.clip(np.random.normal(74, 14.3, N) + (age_years - 53) * 0.15, 40, 180)
height = np.clip(height, 140, 200)

bmi_base = weight / ((height / 100) ** 2)
ap_hi = np.clip(np.random.normal(120 + (age_years - 45) * 0.6 + (bmi_base - 25) * 1.1, 16, N), 90, 220)
ap_lo = np.clip(ap_hi * np.random.normal(0.64, 0.06, N), 60, 140)

chol_p = np.clip(0.05 + (age_years - 29) / 90 + (bmi_base - 22) * 0.01, 0.02, 0.55)
cholesterol = np.array([
    np.random.choice([1, 2, 3], p=[1 - 2 * p if 1 - 2 * p > 0.4 else 0.4,
                                     p, max(0.02, 1 - (1 - 2 * p if 1 - 2 * p > 0.4 else 0.4) - p)])
    for p in chol_p
])

gluc_p = np.clip(0.03 + (bmi_base - 22) * 0.008, 0.01, 0.4)
gluc = np.array([
    np.random.choice([1, 2, 3], p=[1 - 2 * p if 1 - 2 * p > 0.5 else 0.5,
                                    p, max(0.01, 1 - (1 - 2 * p if 1 - 2 * p > 0.5 else 0.5) - p)])
    for p in gluc_p
])

smoke = np.where(gender == 2, np.random.binomial(1, 0.18, N), np.random.binomial(1, 0.04, N))
alco = np.where(gender == 2, np.random.binomial(1, 0.10, N), np.random.binomial(1, 0.025, N))
active = np.random.binomial(1, 0.80, N)

logit = (
    -8.25
    + 0.055 * age_years
    + 0.028 * ap_hi
    + 0.018 * ap_lo
    + 0.55 * (cholesterol - 1)
    + 0.25 * (gluc - 1)
    + 0.05 * (bmi_base - 25)
    + 0.30 * smoke
    - 0.35 * active
    + np.random.normal(0, 0.9, N)
)
prob = 1 / (1 + np.exp(-logit))
cardio = np.random.binomial(1, prob)

df = pd.DataFrame({
    "id": np.arange(1, N + 1),
    "age": age_days,
    "gender": gender,
    "height": height.round(1),
    "weight": weight.round(1),
    "ap_hi": ap_hi.round(0).astype(int),
    "ap_lo": ap_lo.round(0).astype(int),
    "cholesterol": cholesterol,
    "gluc": gluc,
    "smoke": smoke,
    "alco": alco,
    "active": active,
    "cardio": cardio,
})

# inject a small amount of real-world messiness for the "raw" file
raw = df.copy()
dirty_idx = np.random.choice(N, 400, replace=False)
raw.loc[dirty_idx[:100], "ap_hi"] = -raw.loc[dirty_idx[:100], "ap_hi"]
raw.loc[dirty_idx[100:180], "ap_lo"] = raw.loc[dirty_idx[100:180], "ap_lo"] * 10
raw.loc[dirty_idx[180:260], "height"] = np.random.uniform(55, 90, 80)
dup_rows = raw.sample(150, random_state=1)
raw = pd.concat([raw, dup_rows], ignore_index=True)
null_idx = np.random.choice(raw.index, 200, replace=False)
raw.loc[null_idx, "weight"] = np.nan

raw.to_csv("cardio_raw.csv", index=False)
df.to_csv("final_cardio_dataset.csv", index=False)
print("raw:", raw.shape, "clean:", df.shape, "cardio rate:", df.cardio.mean().round(4))
