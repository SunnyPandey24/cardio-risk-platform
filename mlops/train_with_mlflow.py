import json
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("cardio-risk-prediction")

df = pd.read_csv("../data/excel_cleaned_cardio_data.csv")
features = ["age", "gender", "bmi", "ap_hi", "ap_lo", "cholesterol", "gluc", "smoke", "alco", "active"]
X, y = df[features], df["cardio"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

def log_run(model_name, model, X_tr, X_te, params):
    with mlflow.start_run(run_name=model_name):
        mlflow.log_params(params)
        model.fit(X_tr, y_train)
        proba = model.predict_proba(X_te)[:, 1]
        pred = (proba >= 0.5).astype(int)

        metrics = {
            "accuracy": accuracy_score(y_test, pred),
            "precision": precision_score(y_test, pred),
            "recall": recall_score(y_test, pred),
            "f1": f1_score(y_test, pred),
            "roc_auc": roc_auc_score(y_test, proba),
        }
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, name="model", input_example=X_tr.head(3))
        print(f"{model_name}: {metrics}")
        return metrics, mlflow.active_run().info.run_id

# Logistic Regression run (scaled features)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)
lr_metrics, lr_run_id = log_run(
    "logistic_regression",
    LogisticRegression(max_iter=1000),
    pd.DataFrame(X_train_s, columns=features),
    pd.DataFrame(X_test_s, columns=features),
    {"model_type": "LogisticRegression", "max_iter": 1000, "scaled": True},
)

# Random Forest run
rf_metrics, rf_run_id = log_run(
    "random_forest",
    RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1),
    X_train, X_test,
    {"model_type": "RandomForestClassifier", "n_estimators": 200, "max_depth": 8},
)

# Pick the best run by ROC-AUC and register it
best_name, best_metrics, best_run_id = (
    ("logistic_regression", lr_metrics, lr_run_id) if lr_metrics["roc_auc"] >= rf_metrics["roc_auc"]
    else ("random_forest", rf_metrics, rf_run_id)
)
model_uri = f"runs:/{best_run_id}/model"
registered = mlflow.register_model(model_uri, "cardio-risk-model")
print(f"\nBest model: {best_name} (ROC-AUC {best_metrics['roc_auc']:.4f})")
print(f"Registered as 'cardio-risk-model' version {registered.version}")

with open("mlops_summary.json", "w") as f:
    json.dump({
        "logistic_regression": lr_metrics,
        "random_forest": rf_metrics,
        "best_model": best_name,
        "registered_version": registered.version,
    }, f, indent=2, default=str)
