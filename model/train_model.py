import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

df = pd.read_csv("../data/excel_cleaned_cardio_data.csv")

features = ["age", "gender", "bmi", "ap_hi", "ap_lo", "cholesterol", "gluc", "smoke", "alco", "active"]
X = df[features]
y = df["cardio"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

log_reg = LogisticRegression(max_iter=1000)
log_reg.fit(X_train_s, y_train)
lr_proba = log_reg.predict_proba(X_test_s)[:, 1]
lr_pred = (lr_proba >= 0.5).astype(int)

rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
rf_proba = rf.predict_proba(X_test)[:, 1]
rf_pred = (rf_proba >= 0.5).astype(int)

def metrics(y_true, pred, proba):
    return {
        "accuracy": round(accuracy_score(y_true, pred), 4),
        "precision": round(precision_score(y_true, pred), 4),
        "recall": round(recall_score(y_true, pred), 4),
        "f1": round(f1_score(y_true, pred), 4),
        "roc_auc": round(roc_auc_score(y_true, proba), 4),
        "confusion_matrix": confusion_matrix(y_true, pred).tolist(),
    }

results = {
    "logistic_regression": metrics(y_test, lr_pred, lr_proba),
    "random_forest": metrics(y_test, rf_pred, rf_proba),
}

feature_importance = dict(zip(features, rf.feature_importances_.round(4).tolist()))

# Portable logistic-regression coefficients (raw-scale, no external scaler needed)
# Refit a plain-scale logistic regression so the browser calculator can use it directly
log_reg_raw = LogisticRegression(max_iter=1000)
log_reg_raw.fit(X_train, y_train)
raw_coefs = dict(zip(features, log_reg_raw.coef_[0].round(6).tolist()))
raw_intercept = round(float(log_reg_raw.intercept_[0]), 6)
raw_proba = log_reg_raw.predict_proba(X_test)[:, 1]
raw_auc = round(roc_auc_score(y_test, raw_proba), 4)

output = {
    "results": results,
    "feature_importance": feature_importance,
    "calculator_model": {
        "type": "logistic_regression_raw_scale",
        "intercept": raw_intercept,
        "coefficients": raw_coefs,
        "roc_auc": raw_auc,
        "feature_order": features,
    },
}

with open("model_results.json", "w") as f:
    json.dump(output, f, indent=2)

print(json.dumps(results, indent=2))
print("Feature importance:", feature_importance)
print("Calculator AUC:", raw_auc)
