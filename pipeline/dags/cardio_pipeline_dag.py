"""
Airflow DAG for the cardiovascular risk pipeline.

This mirrors pipeline/prefect_flow.py but in Airflow's DAG format, since many data
engineering teams standardize on Airflow specifically. To run it:

1. pip install apache-airflow
2. airflow db init
3. Copy this file into your $AIRFLOW_HOME/dags/ folder
4. airflow webserver & airflow scheduler
5. Trigger 'cardio_risk_pipeline' from the Airflow UI (http://localhost:8080)

Or run entirely locally with the lighter-weight pipeline/prefect_flow.py, which does
not require the Airflow metadata database / webserver / scheduler setup.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_ROOT = "/opt/cardio"  # update to your deployment path

default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

with DAG(
    dag_id="cardio_risk_pipeline",
    description="Ingest -> clean -> feature engineer -> train -> track -> report",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["cardio", "ml", "etl"],
) as dag:

    generate_data = BashOperator(
        task_id="generate_data",
        bash_command=f"cd {PROJECT_ROOT}/data && python3 generate_data.py",
    )

    clean_and_engineer = BashOperator(
        task_id="clean_and_engineer",
        bash_command=f"cd {PROJECT_ROOT}/data && python3 clean_and_engineer.py",
    )

    train_baseline_model = BashOperator(
        task_id="train_baseline_model",
        bash_command=f"cd {PROJECT_ROOT}/model && python3 train_model.py",
    )

    train_with_mlflow = BashOperator(
        task_id="train_with_mlflow_tracking",
        bash_command=f"cd {PROJECT_ROOT}/mlops && python3 train_with_mlflow.py",
    )

    rebuild_excel_report = BashOperator(
        task_id="rebuild_excel_report",
        bash_command=f"cd {PROJECT_ROOT}/excel && python3 build_excel.py",
    )

    generate_data >> clean_and_engineer >> train_baseline_model >> train_with_mlflow >> rebuild_excel_report
