from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.providers.ssh.hooks.ssh import SSHHook
from datetime import datetime, timedelta
from taxi_schema import taxi_schema
import os
import pandas as pd
import pandera as pa
from pandera import DataFrameSchema, Column
from pandera.errors import SchemaErrors
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

BUCKET_NAME = "r-mlops-bucket-8-1-11-854415502"
RAW_DATA_PREFIX = "raw_data"
TRANSFORMED_DATA_PREFIX = "transformed_data"


def process_s3_data(**context):
    local_dir = "/tmp/worker_data"
    os.makedirs(local_dir, exist_ok=True)
    s3_hook = S3Hook(aws_conn_id='aws_default')

    for file_name in ["uber.csv"]:
        content = s3_hook.read_key(f"{RAW_DATA_PREFIX}/{file_name}", bucket_name=BUCKET_NAME)
        local_path = os.path.join(local_dir, file_name)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(content)

    # Читаем и валидируем
    df = pd.read_csv(local_path)
    df = df[taxi_schema.columns.keys()]
    df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], format="%Y-%m-%d %H:%M:%S UTC", errors="coerce")
    df = df.dropna(subset=["pickup_datetime"])

    # Очистка
    df['pickup_longitude'] = df['pickup_longitude'].clip(-180, 180)
    df['dropoff_longitude'] = df['dropoff_longitude'].clip(-180, 180)
    df['pickup_latitude'] = df['pickup_latitude'].clip(-180, 180)
    df['dropoff_latitude'] = df['dropoff_latitude'].clip(-180, 180)
    df['fare_amount'] = df['fare_amount'].clip(0, 100)
    df['passenger_count'] = df['passenger_count'].clip(1, 9)

    # Валидация
    try:
        taxi_schema.validate(df, lazy=True)
    except SchemaErrors as e:
        e.failure_cases.to_csv(os.path.join(local_dir, "dq_failures.csv"), index=False)

    # Сохраняем
    processed_path = os.path.join(local_dir, "processed_uber.csv")
    df.to_csv(processed_path, index=False)
    s3_hook.load_file(
        filename=processed_path,
        key=f"{TRANSFORMED_DATA_PREFIX}/processed_uber.csv",
        bucket_name=BUCKET_NAME,
        replace=True
    )
with DAG(
    'MyS3Task',
    start_date=datetime(2025, 9, 11),
    schedule="@hourly",
    tags=['SimonovAlexander'],
    catchup=False) as dag:

    # Шаг 1. Проверка существования файлов для обработки
    check_uber_csv = S3KeySensor(
        task_id='check_uber_csv',
        bucket_name=BUCKET_NAME,
        bucket_key=f"{RAW_DATA_PREFIX}/uber.csv",
        aws_conn_id='aws_default'
    )

    # Шаг 2. Обработка данных и сохранение на ВМ.
    process_s3_task = PythonOperator(
        task_id='process_s3_task',
        python_callable=process_s3_data,
    )



    # Шаг 3. Проверка существования файлов после обработки
    check_transformed_uber = S3KeySensor(
        task_id='check_transformed_uber',
        bucket_name=BUCKET_NAME,
        bucket_key=f"{TRANSFORMED_DATA_PREFIX}/processed_uber.csv",
        aws_conn_id='aws_default'
    )

# Dependencies
    check_uber_csv >> process_s3_task >> check_transformed_uber