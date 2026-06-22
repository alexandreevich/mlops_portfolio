import joblib
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType, Int64TensorType
import logging

# загружаем модель
model = joblib.load("model.pkl")
print(f"Загружена модель: {type(model)}")
print(f"Pipeline steps: {model.steps}")

# На основании вывода скрипта 1type_of_features.py
# Настраваем типы признаков для конвертации
initial_types = [
    ("pickup_latitude", FloatTensorType([None, 1])),
    ("pickup_longitude", FloatTensorType([None, 1])),
    ("dropoff_latitude", FloatTensorType([None, 1])),
    ("dropoff_longitude", FloatTensorType([None, 1])),
    ("passenger_count", Int64TensorType([None, 1]))
]

print("Конвертируем Pipeline в ONNX...")

onnx_model = convert_sklearn(
    model, initial_types=initial_types, name="popularity_prediction_model"
)

# Сохраняем
with open("model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

print("Модель успешно конвертирована в model.onnx")