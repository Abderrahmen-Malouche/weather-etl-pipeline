from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
import sys

sys.path.append('/opt/airflow/api-request')
from insert_records import main

default_args = {
    "description": "A DAG to orchestrate weather data",
    "start_date": datetime(2025, 7, 11),
    "catchup": False
}

dag = DAG(
    dag_id="weather-api-orchestrator",
    default_args=default_args,
    schedule=timedelta(minutes=5)
)

with dag:
    task1 = PythonOperator(
        task_id="ingest_data_task",
        python_callable=main
    )
