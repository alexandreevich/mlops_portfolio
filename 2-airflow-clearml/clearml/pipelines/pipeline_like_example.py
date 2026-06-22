import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn import linear_model, tree
from sklearn.metrics import mean_squared_error
from clearml import PipelineController
import joblib
from clearml import OutputModel, Task
import os


def prepare_data(dataset_path):
    storage_options = {
        "client_kwargs": {
            "endpoint_url": "https://storage.yandexcloud.net",
            "region_name": "ru-central1",
        }
    }
    
    df = pd.read_csv(dataset_path,storage_options=storage_options)

    X = df[
        [
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "passenger_count",
        ]
    ]
    y = df["fare_amount"]
    
    # Разделение на train/test
    splitted_data = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return splitted_data
    
# Древо
def train_tree_model(data):
    X_train, X_test, y_train, y_test = data

    tree_model = tree.DecisionTreeRegressor()
    tree_model.fit(X_train, y_train)

    return tree_model

#  Линейная
def train_lr_model(data):
    X_train, X_test, y_train, y_test = data

    lr = linear_model.LinearRegression()
    lr.fit(X_train, y_train)

    return lr

# Функция валидации моделей
def validate_model(model, data):
    X_train, X_test, y_train, y_test = data
    y_pred = model.predict(X_test)
    mse = np.round(mean_squared_error(y_test, y_pred), 5).item()

    results = {"mean_squared_error": mse}

    return model, results


# Валидация моделей 
def select_best(lr_model, tree_model, lr_model_results, tree_model_results):
    task = Task.current_task()

    if (
        lr_model_results["mean_squared_error"]
        < tree_model_results["mean_squared_error"]
    ):
        print("LR model produces better metrics")
        ### ---- Создание объекта OutputModel ---- ####
        output_model = OutputModel(
            task=task,
            framework="ScikitLearn",
            name="LinearRegression",  # Задаём имя модели
            comment="linear regression model",  # Ставим дополнительный комментарий
            tags=["lr_model"],  # Ставим теги для упрощения поиска модели
        )
        joblib.dump(lr_model, "lr_model.pkl", compress=True)
        output_model.update_weights("lr_model.pkl")
    else:
        print("Tree model produces better metrics")
        ### ---- Создание объекта OutputModel ---- ####
        output_model = OutputModel(
            task=task,
            framework="ScikitLearn",
            name="DecisionTreeRegressor",  # Задаём имя модели
            comment="Tree regression model",  # Ставим дополнительный комментарий
            tags=["tree_reg_model"],  # Ставим теги для упрощения поиска модели
        )
        joblib.dump(tree_model, "tree_model.pkl", compress=True)
        output_model.update_weights("tree_model.pkl")


# Задаем пайплайн
pipe = PipelineController(
    name="Train recommend model",
    project="mlops",
    version="0.0.1",
    docker="python:3.12-slim", # образ докера, в котором будет исполняться контроллер
) 

pipe.set_default_execution_queue(default_execution_queue="default")

# Указываем откуда взять датасет
pipe.add_parameter(
        name="uber_path",
        description="path to dataset.csv",
        default="s3://r-mlops-bucket-8-1-11-854415502/transformed_data/processed_uber.csv",
)

# Разделение датасета на выборки
pipe.add_function_step(
    name="prepare_data",
    function=prepare_data,
    function_kwargs=dict(
        dataset_path="${pipeline.uber_path}"
    ),
    function_return=["splitted_data"],
    docker="python:3.12-slim",  # Задаём образ докера, в котором будет исполняться шаг
    packages=[  # список пакетов, которые необходимы в этом шаге
        "clearml[s3]==2.0.2",
        "pandas>=2.3.2",
        "scikit-learn>=1.7.1",
        "s3fs==2025.9.0",
        "fsspec==2025.9.0",
    ],
)


# Модель дерева решений
pipe.add_function_step(
    name="train_tree_model",
    function=train_tree_model,
    function_kwargs=dict(data="${prepare_data.splitted_data}"),
    function_return=["tree_model"],
    docker="python:3.12-slim" # образ докера, который будем использовать
) 

# Модель линейной регрессии
pipe.add_function_step(
    name="train_lr_model",
    function=train_lr_model,
    function_kwargs=dict(data="${prepare_data.splitted_data}"),
    function_return=["lr_model"],
    docker="python:3.12-slim" # образ докера, который будем использовать
) 

#Валидация модели древа
pipe.add_function_step(
    name="validate_tree_model",
    function=validate_model,
    function_kwargs=dict(
        model="${train_tree_model.tree_model}", data="${prepare_data.splitted_data}"
    ),
    function_return=["model", "results"],
    docker="python:3.12-slim",
)

# Создаём шаг валидации модели линейной регресии, в который
# передаём данные для валидации и саму модель
pipe.add_function_step(
    name="validate_lr_model",
    function=validate_model,
    function_kwargs=dict(
        model="${train_lr_model.lr_model}", data="${prepare_data.splitted_data}"
    ),
    function_return=["model", "results"],
    docker="python:3.12-slim",
)

# Создаём шаг выбора лучшей модели
pipe.add_function_step(
    name="select_best_model",
    function=select_best,
    function_kwargs=dict(
        lr_model="${validate_lr_model.model}",
        tree_model="${validate_tree_model.model}",
        lr_model_results="${validate_lr_model.results}",
        tree_model_results="${validate_tree_model.results}",
    ),
    docker="python:3.12-slim",
)

# Задаём имя очереди, в которой будет выполняться пайплайн-контроллер
pipe.start(queue="default")  

