import onnxruntime as ort
import numpy as np
import time
import json
import pandas as pd
import joblib
from pathlib import Path
from typing import Tuple

# Дефотные признаки, все как в задании
DEFAULT_FEATURES = [
    "pickup_latitude",
    "pickup_longitude",
    "dropoff_latitude",
    "dropoff_longitude",
    "passenger_count",
]
DEFAULT_TARGET = "fare_amount"


# Функция подготовки данных
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



# Функция оценки скорости для onnx, ничего не трогал 
def benchmark_onnx(model_path: str, X: pd.DataFrame, num_runs: int = 1000):
    # Загружаем модель
    sess = ort.InferenceSession(model_path)

    # Тестовые данные
    test_inputs = {}

    for input_info in sess.get_inputs():
        tensor_type = input_info.type
        if tensor_type == "tensor(float)":
            test_inputs[input_info.name] = (
                X[input_info.name].values.reshape(-1, 1).astype(np.float32)
            )
        elif tensor_type == "tensor(int64)":
            test_inputs[input_info.name] = (
                X[input_info.name].values.reshape(-1, 1).astype(np.int64)
            )

    # Тестирование
    latencies = []
    for i in range(num_runs):
        start = time.perf_counter()
        result = sess.run(None, test_inputs)
        end = time.perf_counter()
        latencies.append((end - start) * 1000)

    # Результаты
    latencies.sort()
    results = {
        "runs": num_runs,
        "min_s": np.round(min(latencies), 3),
        "mean_s": np.round((sum(latencies) / len(latencies)), 3),
        "p50_s": np.round(np.percentile(latencies, 50), 3),
        "p95_s": np.round(np.percentile(latencies, 95), 3),
        "p99_s": np.round(np.percentile(latencies, 99), 3),
        "max_s": np.round(max(latencies), 3),
    }

    return results

# Функция оценки скорости для sklearn, ничего не трогал 
def benchmark_sklearn(model_path: str, X: pd.DataFrame, num_runs: int = 1000):
    # Загружаем модель
    clf = joblib.load(model_path)

    # Тестирование
    latencies = []
    for i in range(num_runs):
        start = time.perf_counter()
        predicts = clf.predict(X)
        end = time.perf_counter()
        latencies.append((end - start) * 1000)

    # Результаты
    latencies.sort()
    results = {
        "runs": num_runs,
        "min_s": np.round(min(latencies), 3),
        "mean_s": np.round((sum(latencies) / len(latencies)), 3),
        "p50_s": np.round(np.percentile(latencies, 50), 3),
        "p95_s": np.round(np.percentile(latencies, 95), 3),
        "p99_s": np.round(np.percentile(latencies, 99), 3),
        "max_s": np.round(max(latencies), 3),
    }

    return results


# Запуск
# Добаивил вывод Runs
if __name__ == "__main__":
    dataset_path = "uber.csv"
    X, y = load_dataset(dataset_path,DEFAULT_FEATURES,DEFAULT_TARGET)

    model_path = "service/model.onnx"
    results = benchmark_onnx(model_path, X)

    # Вывод
    print(f"\nLatency for onnx (s):")
    print(f"  Runs:  {results['runs']:.0f}")
    print(f"  Min:  {results['min_s']:.3f}")
    print(f"  Mean: {results['mean_s']:.3f}")
    print(f"  P50:  {results['p50_s']:.3f}")
    print(f"  P95:  {results['p95_s']:.3f}")
    print(f"  P99:  {results['p99_s']:.3f}")
    print(f"  Max:  {results['max_s']:.3f}")

    model_path = "service/model.pkl"
    results = benchmark_sklearn(model_path, X)

    # Вывод
    print(f"\nLatency for sklearn(s):")
    print(f"  Runs:  {results['runs']:.0f}")
    print(f"  Min:  {results['min_s']:.3f}")
    print(f"  Mean: {results['mean_s']:.3f}")
    print(f"  P50:  {results['p50_s']:.3f}")
    print(f"  P95:  {results['p95_s']:.3f}")
    print(f"  P99:  {results['p99_s']:.3f}")
    print(f"  Max:  {results['max_s']:.3f}")