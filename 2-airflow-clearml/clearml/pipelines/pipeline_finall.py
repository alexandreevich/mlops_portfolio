# pipeline_minimal.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import linear_model, tree
from sklearn.metrics import mean_squared_error
from clearml import PipelineController, OutputModel, Task
import joblib


# Подготовка данных
def prepare_data(dataset_path):
    storage_options = {
        "client_kwargs": {
            "endpoint_url": "https://storage.yandexcloud.net",
            "region_name": "ru-central1",
        }
    }
    df = pd.read_csv(dataset_path, storage_options=storage_options)
    for col in ["pickup_latitude","pickup_longitude","dropoff_latitude",
                "dropoff_longitude","passenger_count","fare_amount"]:
        df[col] = df[col].fillna(df[col].median())
    X = df[["pickup_latitude","pickup_longitude","dropoff_latitude",
            "dropoff_longitude","passenger_count"]].values
    y = df["fare_amount"].values
    splitted_data = train_test_split(X, y, test_size=0.2, random_state=42)
    return {"splitted_data": splitted_data}



# Обучение моделей
def train_tree_model(data):
    X_train, X_test, y_train, y_test = data["splitted_data"]
    model = tree.DecisionTreeRegressor(max_depth=5, min_samples_split=2)
    model.fit(X_train, y_train)
    return model

def train_lr_model(data):
    X_train, X_test, y_train, y_test = data["splitted_data"]
    model = linear_model.LinearRegression(fit_intercept=True)
    model.fit(X_train, y_train)
    return model


# Валидация модели
def validate_model(model, data):
    X_train, X_test, y_train, y_test = data["splitted_data"]
    y_pred = model.predict(X_test)
    mse = float(mean_squared_error(y_test, y_pred))
    return model, {"mean_squared_error": mse}


# Выбор лучшей модели
def select_best(tree_model, lr_model, tree_results, lr_results):
    task = Task.current_task()
    all_models = [
        (tree_model, tree_results, "tree_model"),
        (lr_model, lr_results, "lr_model")
    ]
    best_model, best_results, best_name = min(all_models, key=lambda x: x[1]["mean_squared_error"])
    output_model = OutputModel(
        task=task,
        framework="ScikitLearn",
        name=best_name,
        comment=f"Best model selected ({best_name})",
        tags=["best_model"]
    )
    joblib.dump(best_model, f"{best_name}.pkl", compress=True)
    output_model.update_weights(f"{best_name}.pkl")


# Создание пайплайна
pipe = PipelineController(
    name="Uber_Pipeline_Minimal",
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
prepare_step = pipe.add_function_step(
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


# Обучение моделей 
tree_step = pipe.add_function_step(
    name="train_tree_model",
    function=train_tree_model,
    function_kwargs={"data": "${prepare_data.splitted_data}"},
    function_return=["tree_model"],
    docker="python:3.12-slim",
)

lr_step = pipe.add_function_step(
    name="train_lr_model",
    function=train_lr_model,
    function_kwargs={"data": "${prepare_data.splitted_data}"},
    function_return=["lr_model"],
    docker="python:3.12-slim",
)


# Валидация
validate_tree = pipe.add_function_step(
    name="validate_tree_model",
    function=validate_model,
    function_kwargs={"model": "${train_tree_model.tree_model}", "data": "${prepare_data.splitted_data}"},
    function_return=["tree_model", "tree_results"],
    docker="python:3.12-slim"
)
validate_lr = pipe.add_function_step(
    name="validate_lr_model",
    function=validate_model,
    function_kwargs={"model": "${train_lr_model.lr_model}", "data": "${prepare_data.splitted_data}"},
    function_return=["lr_model", "lr_results"],
    docker="python:3.12-slim"
)


# Выбор лучшей модели
pipe.add_function_step(
    name="select_best_model",
    function=select_best,
    function_kwargs={
        "tree_model": "${validate_tree_model.tree_model}",
        "lr_model": "${validate_lr_model.lr_model}",
        "tree_results": "${validate_tree_model.tree_results}",
        "lr_results": "${validate_lr_model.lr_results}",
    },
    docker="python:3.12-slim"
)


# Запуск
# pipe.start_locally(True)
pipe.start(queue="default")