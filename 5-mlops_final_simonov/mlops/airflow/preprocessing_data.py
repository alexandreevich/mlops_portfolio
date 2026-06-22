from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime
from pathlib import Path
import os

# Задаем бакет / где сырые / обработанные данные и место для их хранения при обработке
BUCKET_NAME = "r-mlops-bucket-12-1-1-854415502"
RAW_DATA_PREFIX = "raw_data"

LOCAL_DIR = "/tmp/mlops_raw"
TRANSFORMED_DATA_PREFIX = "transformed_data"


# Был косяк с созданием дирректорий
#  поэтому добавил ф-цию очистки
def clean_tmp(**context):
    import shutil

    shutil.rmtree("/tmp/mlops_raw", ignore_errors=True)


# Грузим первый датасет
def download_events(**context):
    hook = S3Hook(aws_conn_id="aws_default")

    Path(LOCAL_DIR).mkdir(parents=True, exist_ok=True)

    content = hook.read_key(
        key=f"{RAW_DATA_PREFIX}/events.csv", bucket_name=BUCKET_NAME
    )

    path = os.path.join(LOCAL_DIR, "events.csv")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


#  Второй туда же
def download_item_props(**context):
    hook = S3Hook(aws_conn_id="aws_default")

    content = hook.read_key(
        key=f"{RAW_DATA_PREFIX}/item_properties_part1.csv", bucket_name=BUCKET_NAME
    )

    path = os.path.join(LOCAL_DIR, "item_properties_part1.csv")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


#  Импортим скрипт из примера и просто запускаем
def run_prepare(**context):
    from prepare_features import prepare

    prepare(
        events_path=f"{LOCAL_DIR}/events.csv",
        item_props_path=f"{LOCAL_DIR}/item_properties_part1.csv",
        out_item_feats_path=f"{LOCAL_DIR}/item_features.parquet",
        out_train_path=f"{LOCAL_DIR}/data_for_training.parquet",
        window_hours=24,
    )


# Грузим оба получившихся файла в s3
def upload_to_s3(**context):
    hook = S3Hook(aws_conn_id="aws_default")

    local_dir = "/tmp/mlops_raw"

    files = [
        "item_features.parquet",
        "data_for_training.parquet",
    ]

    for file_name in files:
        local_path = os.path.join(local_dir, file_name)

        hook.load_file(
            filename=local_path,
            bucket_name=BUCKET_NAME,
            key=f"{TRANSFORMED_DATA_PREFIX}/{file_name}",
            replace=True,
        )


# Сами таски дага и в конце последовательность
with DAG(
    dag_id="mlops_etl_pipeline_v2",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    tags=["SimonovAlexander"],
    catchup=False,
) as dag:
    clean_task = PythonOperator(
        task_id="clean_tmp",
        python_callable=clean_tmp,
    )

    download_events_task = PythonOperator(
        task_id="download_events",
        python_callable=download_events,
    )

    download_item_props_task = PythonOperator(
        task_id="download_item_props",
        python_callable=download_item_props,
    )

    prepare_task = PythonOperator(
        task_id="prepare_features",
        python_callable=run_prepare,
    )

    upload_task = PythonOperator(
        task_id="upload_to_s3",
        python_callable=upload_to_s3,
    )


(
    clean_task
    >> [download_events_task, download_item_props_task]
    >> prepare_task
    >> upload_task
)
