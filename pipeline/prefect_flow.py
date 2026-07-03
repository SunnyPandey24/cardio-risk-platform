import subprocess
import sys
from pathlib import Path
from prefect import flow, task

ROOT = Path(__file__).resolve().parent.parent

def run_script(relative_dir: str, script: str):
    cwd = ROOT / relative_dir
    result = subprocess.run([sys.executable, script], cwd=cwd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"{script} failed with exit code {result.returncode}")
    return result.stdout

@task(retries=1, retry_delay_seconds=10, log_prints=True)
def generate_data():
    print("Generating synthetic patient data...")
    return run_script("data", "generate_data.py")

@task(retries=1, retry_delay_seconds=10, log_prints=True)
def clean_and_engineer():
    print("Cleaning data and engineering features...")
    return run_script("data", "clean_and_engineer.py")

@task(log_prints=True)
def train_baseline_model():
    print("Training baseline Logistic Regression / Random Forest...")
    return run_script("model", "train_model.py")

@task(log_prints=True)
def train_with_tracking():
    print("Training with MLflow experiment tracking + model registry...")
    return run_script("mlops", "train_with_mlflow.py")

@task(log_prints=True)
def rebuild_excel_report():
    print("Rebuilding the Excel KPI workbook...")
    return run_script("excel", "build_excel.py")

@flow(name="cardio-risk-etl-and-retrain", log_prints=True)
def cardio_pipeline():
    """
    End-to-end pipeline: ingest -> clean -> feature engineer -> train -> track -> report.
    Run manually with `python prefect_flow.py`, or deploy on a schedule with Prefect Cloud/Server.
    """
    generate_data()
    clean_and_engineer()
    train_baseline_model()
    train_with_tracking()
    rebuild_excel_report()
    print("Pipeline complete: data refreshed, models retrained and tracked, reports rebuilt.")

if __name__ == "__main__":
    cardio_pipeline()
