# Все шаги работают
import pandas as pd

# import pickle
from catboost import CatBoostClassifier

# from pathlib import Path
from sklearn.model_selection import train_test_split
from clearml import PipelineController
from sklearn.metrics import average_precision_score

# import joblib
# import os

# import numpy as np
import optuna
import boto3
# import os


# ф-ция загрузки и разделения датасета
def load_and_spitted(dataset_path):

    storage_options = {
        "client_kwargs": {
            "endpoint_url": "https://storage.yandexcloud.net",
            "region_name": "ru-central1",
        }
    }
    df = pd.read_parquet(dataset_path, storage_options=storage_options)

    # Target
    y = df["target"]

    # Features
    feature_cols = [
        "views",
        "purchases",
        "ctr",
        "hour",
        "weekday",
        "categoryid",
        "available",
    ]
    X = df[feature_cols].astype(float)

    splitted_data = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    return {"splitted_data": splitted_data}


# для валидации лучшей модели
def validate_best(model_path, data):

    X_train, X_test, y_train, y_test = data["splitted_data"]

    model = CatBoostClassifier()
    model.load_model(model_path)

    preds = model.predict_proba(X_test)[:, 1]
    pr_auc = average_precision_score(y_test, preds)

    return {"pr_auc": pr_auc}


# оптуна с гиперпараметрами
def optuna_train(data, n_trials=10):
    X_train, X_test, y_train, y_test = data["splitted_data"]

    def objective(trial):
        # задаем параметры
        params = {
            "depth": trial.suggest_int("depth", 3, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2),
            "iterations": trial.suggest_int("iterations", 50, 200),
            "loss_function": "Logloss",
            "verbose": False,
        }

        model = CatBoostClassifier(**params)
        model.fit(X_train, y_train)

        preds = model.predict_proba(X_test)[:, 1]

        return average_precision_score(y_test, preds)

    # тут аналог цикла
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)

    best_params = study.best_params

    best_model = CatBoostClassifier(
        **best_params, loss_function="Logloss", verbose=False
    )

    best_model.fit(X_train, y_train)

    model_path = "/tmp/ranker.pkl"
    best_model.save_model(model_path)

    return model_path


# грузим лучшую модель в s3
def upload_best_model(model_path: str):
    bucket = "r-mlops-bucket-12-1-1-854415502"
    key = "best_model/ranker.pkl"

    session = boto3.session.Session()
    s3 = session.client(
        service_name="s3",
        endpoint_url="https://storage.yandexcloud.net",
        region_name="ru-central1",
    )

    s3.upload_file(model_path, bucket, key)

    return {"s3_path": f"s3://{bucket}/{key}"}


#  Cам пайплайн задаем тут
pipe = PipelineController(
    name="Final_RecSys", project="mlops", version="0.0.1", docker="python:3.12-slim"
)
pipe.set_default_execution_queue("default")

pipe.add_parameter(
    name="data_for_training",
    description="S3 path to processed Uber dataset",
    default="s3://r-mlops-bucket-12-1-1-854415502/transformed_data/data_for_training.parquet",
)

pipe.add_parameter(
    name="model_id",
    description="ID of model to infer",
)

# Подготовка данных
pipe.add_function_step(
    name="load_and_spitted",
    function=load_and_spitted,
    function_kwargs={"dataset_path": "${pipeline.data_for_training}"},
    function_return=["splitted_data"],
    docker="python:3.12-slim",
    packages=[  # список пакетов, которые необходимы в этом шаге
        "clearml[s3]==2.0.2",
        "pandas>=2.3.2",
        "scikit-learn>=1.7.1",
        "s3fs==2025.9.0",
        "fsspec==2025.9.0",
    ],
    task_type="data_processing",
)

pipe.add_function_step(
    name="optuna_training",
    function=optuna_train,
    function_kwargs={"data": "${load_and_spitted.splitted_data}", "n_trials": 10},
    function_return=["model_path"],
    docker="python:3.12-slim",
    task_type="training",
)

pipe.add_function_step(
    name="validate_best_model",
    function=validate_best,
    function_kwargs={
        "model_path": "${optuna_training.model_path}",
        "data": "${load_and_spitted.splitted_data}",
    },
    function_return=["metrics"],
)

pipe.add_function_step(
    name="upload_best_model",
    function=upload_best_model,
    function_kwargs={"model_path": "${optuna_training.model_path}"},
    function_return=["s3_path"],
    docker="python:3.12-slim",
    packages=["boto3"],
)

# для запуска на агенте
pipe.start(queue="default")
# pipe.start_locally(True)
