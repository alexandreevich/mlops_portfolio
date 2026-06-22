
from pathlib import Path
from typing import Tuple
import numpy as np
import pandas as pd


# Целевой и входящие признаки
DEFAULT_FEATURES = [
    "pickup_latitude",
    "pickup_longitude",
    "dropoff_latitude",
    "dropoff_longitude",
    "passenger_count",
]
DEFAULT_TARGET = "fare_amount"

# функцию берем из задания, все ок
def load_dataset(csv_path: Path, features: list[str], target: str) -> Tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(csv_path)

    missing_columns = [col for col in features + [target] if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"В датасете отсутствуют необходимые колонки: {missing_columns}.\n"
            f"Найдены колонки: {list(df.columns)}"
        )

    # Базовая очистка
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=features + [target])

    X = df[features].copy()
    y = df[target].astype(float).copy()
    
    return X, y

# задаю место расположения датасета
dataset_path = "uber.csv"

# Пришлось почитать, что это стандартный способ показать: 
# "это значение возвращается, но в данном месте программы оно мне не нужно".
X, _ = load_dataset(dataset_path,DEFAULT_FEATURES,DEFAULT_TARGET)
# Смотрим типы данных и на основаниях вывода
# Будем делать файл конвертации - 2convert.py
print(X.dtypes) 
