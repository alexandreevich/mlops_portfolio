import pandas as pd
import os
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression


def train_and_save_model(data_path: str, model_path: str = "model.pkl"):
    """
    Функция обучает линейную модель на датасете Uber,
    сохраняет модель в файл и выводит метрики качества.
    """

    # ------------------ Загрузка данных ------------------
    df = pd.read_csv(data_path)

    # ------------------ Предобработка ------------------
    df = df.dropna()

    target_column = "fare_amount"
    # берём только числовые колонки
    X = df.select_dtypes(include=["int64", "float64"]).copy()
    if target_column in X.columns:
        X = X.drop(columns=[target_column])
    y = df[target_column]

    # ------------------ Разделение выборок ------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ------------------ Обучение модели ------------------
    model = LinearRegression()
    model.fit(X_train, y_train)

    # ------------------ Предсказания и метрики ------------------
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # ------------------ Сохранение модели ------------------
    joblib.dump(model, model_path)

    print(
        f"Эксперимент завершён. Метрики модели: RMSE={rmse:.3f}, MAE={mae:.3f}, R2={r2:.3f}"
    )


# ------------------ Запуск скрипта ------------------
if __name__ == "__main__":
    # Берём путь к датасету из переменной окружения, fallback на локальный
    data_path = os.getenv("UBER_DATA_PATH", "../uber.csv")  # str
    train_and_save_model(data_path=data_path)  # передаём str
