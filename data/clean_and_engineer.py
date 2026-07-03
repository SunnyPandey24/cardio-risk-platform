import numpy as np
import pandas as pd

raw = pd.read_csv("cardio_raw.csv")
df = raw.copy()

df = df.drop_duplicates(subset=[c for c in df.columns if c != "id"])
df["ap_hi"] = df["ap_hi"].abs()
df["ap_lo"] = df["ap_lo"].abs()
df.loc[df["ap_lo"] > 200, "ap_lo"] = df.loc[df["ap_lo"] > 200, "ap_lo"] / 10
df.loc[df["height"] < 120, "height"] = np.nan
df["weight"] = df["weight"].fillna(df["weight"].median())
df["height"] = df["height"].fillna(df["height"].median())

df = df[(df["ap_hi"] >= 80) & (df["ap_hi"] <= 220)]
df = df[(df["ap_lo"] >= 50) & (df["ap_lo"] <= 160)]
df = df[df["ap_hi"] >= df["ap_lo"]]
df = df[(df["height"] >= 140) & (df["height"] <= 210)]
df = df[(df["weight"] >= 35) & (df["weight"] <= 180)]

df["age_years"] = (df["age"] / 365.25).round(1)
df["age_group"] = pd.cut(
    df["age_years"], bins=[0, 40, 45, 50, 55, 60, 100],
    labels=["<40", "40-45", "45-50", "50-55", "55-60", "60+"]
)
df["bmi"] = (df["weight"] / (df["height"] / 100) ** 2).round(1)
df["bmi_category"] = pd.cut(
    df["bmi"], bins=[0, 18.5, 25, 30, 35, 100],
    labels=["Underweight", "Normal", "Overweight", "Obese", "Severely Obese"]
)

def bp_category(row):
    if row.ap_hi < 120 and row.ap_lo < 80:
        return "Normal"
    if row.ap_hi < 130 and row.ap_lo < 80:
        return "Elevated"
    if row.ap_hi < 140 or row.ap_lo < 90:
        return "Hypertension Stage 1"
    if row.ap_hi < 180 or row.ap_lo < 120:
        return "Hypertension Stage 2"
    return "Hypertensive Crisis"

df["bp_category"] = df.apply(bp_category, axis=1)
df["pulse_pressure"] = df["ap_hi"] - df["ap_lo"]
df["gender_label"] = df["gender"].map({1: "Female", 2: "Male"})
df["cholesterol_label"] = df["cholesterol"].map({1: "Normal", 2: "Above Normal", 3: "Well Above Normal"})
df["gluc_label"] = df["gluc"].map({1: "Normal", 2: "Above Normal", 3: "Well Above Normal"})

lifestyle_score = df["smoke"] + df["alco"] + (1 - df["active"])
clinical_score = (df["cholesterol"] - 1) + (df["gluc"] - 1) + (df["bp_category"].map({
    "Normal": 0, "Elevated": 1, "Hypertension Stage 1": 2, "Hypertension Stage 2": 3, "Hypertensive Crisis": 4
}))
age_score = pd.cut(df["age_years"], bins=[0, 45, 55, 65, 100], labels=[0, 1, 2, 3]).astype(int)
bmi_score = pd.cut(df["bmi"], bins=[0, 25, 30, 35, 100], labels=[0, 1, 2, 3]).astype(int)

raw_risk = lifestyle_score + clinical_score + age_score + bmi_score
df["risk_score"] = (raw_risk / raw_risk.max() * 100).round(1)
df["risk_tier"] = pd.cut(
    df["risk_score"], bins=[-1, 25, 50, 75, 101],
    labels=["Low", "Medium", "High", "Critical"]
)

df = df.drop(columns=["age"]).rename(columns={"age_years": "age"})
df.to_csv("excel_cleaned_cardio_data.csv", index=False)
print(df.shape)
print(df["risk_tier"].value_counts(normalize=True).round(3))
print(df.groupby("risk_tier")["cardio"].mean().round(3))
