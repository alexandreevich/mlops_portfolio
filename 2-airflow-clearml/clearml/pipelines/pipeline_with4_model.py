# pipeline_simple.py Работает даже с агентом
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import linear_model, tree
from sklearn.metrics import mean_squared_error
from clearml import PipelineController, OutputModel, Task
import joblib
import os
import numpy as np

# Функция подготовки данных
def prepare_data(dataset_path):
    storage_options = {
        "client_kwargs": {
            "endpoint_url": "https://storage.yandexcloud.net",
            "region_name": "ru-central1",
        }
    }
    df = pd.read_csv(dataset_path, storage_options=storage_options)

    X = df[["pickup_latitude","pickup_longitude","dropoff_latitude","dropoff_longitude","passenger_count"]].values
    y = df["fare_amount"].values
    splitted_data = train_test_split(X, y, test_size=0.2, random_state=42)
    return {"splitted_data": splitted_data}




# Обучение моделей

def train_tree_model(data, max_depth, min_samples_split):
    X_train, X_test, y_train, y_test = data["splitted_data"]
    model = tree.DecisionTreeRegressor(max_depth=max_depth, min_samples_split=min_samples_split)
    model.fit(X_train, y_train)
    return model

def train_lr_model(data, fit_intercept):
    X_train, X_test, y_train, y_test = data["splitted_data"]
    model = linear_model.LinearRegression(fit_intercept=fit_intercept)
    model.fit(X_train, y_train)
    return model

def validate_model(model, data):
    X_train, X_test, y_train, y_test = data["splitted_data"]
    y_pred = model.predict(X_test)
    mse = float(mean_squared_error(y_test, y_pred))
    return model, {"mean_squared_error": mse}
# выбор лучшей модели
def select_best(tree_model_0, tree_model_1, lr_model_0, lr_model_1,
                tree_results_0, tree_results_1, lr_results_0, lr_results_1):
    task = Task.current_task()
    all_models = [
        (tree_model_0, tree_results_0),
        (tree_model_1, tree_results_1),
        (lr_model_0, lr_results_0),
        (lr_model_1, lr_results_1)
    ]
    best_model, best_results = min(all_models, key=lambda x: x[1]["mean_squared_error"])
    output_model = OutputModel(
        task=task,
        framework="ScikitLearn",
        name="Best_model",
        comment="Best model selected from 2x2 parameter sweep",
        tags=["best_model"]
    )
    joblib.dump(best_model, "best_model.pkl", compress=True)
    output_model.update_weights("best_model.pkl")


# Задаем пайп

pipe = PipelineController(
    name="Uber_Pipeline_Simple",
    project="mlops",
    version="0.0.1",
    docker="python:3.12-slim"
)
pipe.set_default_execution_queue("default")

pipe.add_parameter(
    name="uber_path",
    description="S3 path to processed Uber dataset",
    default="s3://r-mlops-bucket-8-1-11-854415502/transformed_data/processed_uber.csv"
)

# Подготовка данных
pipe.add_function_step(
    name="prepare_data",
    function=prepare_data,
    function_kwargs={"dataset_path": "${pipeline.uber_path}"},
    function_return=["splitted_data"],
    docker="python:3.12-slim",
    packages=[  # список пакетов, которые необходимы в этом шаге
        "clearml[s3]==2.0.2",
        "pandas>=2.3.2",
        "scikit-learn>=1.7.1",
        "s3fs==2025.9.0",
        "fsspec==2025.9.0",
    ]
)

# Дерево решений: 2 варианта
pipe.add_function_step(
    name="train_tree_model_0",
    function=train_tree_model,
    function_kwargs={"data": "${prepare_data.splitted_data}", "max_depth":5, "min_samples_split":2},
    function_return=["tree_model_0"],
    docker="python:3.12-slim"
)
pipe.add_function_step(
    name="train_tree_model_1",
    function=train_tree_model,
    function_kwargs={"data": "${prepare_data.splitted_data}", "max_depth":10, "min_samples_split":4},
    function_return=["tree_model_1"],
    docker="python:3.12-slim"
)

# Линейная регрессия: 2 варианта
pipe.add_function_step(
    name="train_lr_model_0",
    function=train_lr_model,
    function_kwargs={"data": "${prepare_data.splitted_data}", "fit_intercept":True},
    function_return=["lr_model_0"],
    docker="python:3.12-slim"
)
pipe.add_function_step(
    name="train_lr_model_1",
    function=train_lr_model,
    function_kwargs={"data": "${prepare_data.splitted_data}", "fit_intercept":False},
    function_return=["lr_model_1"],
    docker="python:3.12-slim"
)

# Валидация
pipe.add_function_step(
    name="validate_tree_model_0",
    function=validate_model,
    function_kwargs={"model": "${train_tree_model_0.tree_model_0}", "data": "${prepare_data.splitted_data}"},
    function_return=["tree_model_0", "tree_results_0"],
    docker="python:3.12-slim"
)
pipe.add_function_step(
    name="validate_tree_model_1",
    function=validate_model,
    function_kwargs={"model": "${train_tree_model_1.tree_model_1}", "data": "${prepare_data.splitted_data}"},
    function_return=["tree_model_1", "tree_results_1"],
    docker="python:3.12-slim"
)
pipe.add_function_step(
    name="validate_lr_model_0",
    function=validate_model,
    function_kwargs={"model": "${train_lr_model_0.lr_model_0}", "data": "${prepare_data.splitted_data}"},
    function_return=["lr_model_0", "lr_results_0"],
    docker="python:3.12-slim"
)
pipe.add_function_step(
    name="validate_lr_model_1",
    function=validate_model,
    function_kwargs={"model": "${train_lr_model_1.lr_model_1}", "data": "${prepare_data.splitted_data}"},
    function_return=["lr_model_1", "lr_results_1"],
    docker="python:3.12-slim"
)

# Выбор лучшей модели
pipe.add_function_step(
    name="select_best_model",
    function=select_best,
    function_kwargs={
        "tree_model_0": "${validate_tree_model_0.tree_model_0}",
        "tree_model_1": "${validate_tree_model_1.tree_model_1}",
        "lr_model_0": "${validate_lr_model_0.lr_model_0}",
        "lr_model_1": "${validate_lr_model_1.lr_model_1}",
        "tree_results_0": "${validate_tree_model_0.tree_results_0}",
        "tree_results_1": "${validate_tree_model_1.tree_results_1}",
        "lr_results_0": "${validate_lr_model_0.lr_results_0}",
        "lr_results_1": "${validate_lr_model_1.lr_results_1}",
    },
    docker="python:3.12-slim"
)

# Локальный запуск для теста
# pipe.start_locally(True)

pipe.start(queue="default")  