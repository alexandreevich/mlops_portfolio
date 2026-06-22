# Необходимо настроить port-forward, что бы можно было посмотреть ответ модели
### Для начала задаем навание сервиса

```
- ISVC=simonov-inference # Название сервиса из InferenceService
```

### Далее используем команду для получения пода

```
POD_NAME=$(kubectl get pods \
  -l "serving.knative.dev/service=${ISVC}-predictor" \
  --field-selector=status.phase=Running \
  -o jsonpath='{.items[*].metadata.name}' | awk '{print $1}')
echo "$POD_NAME"
``` 

### Получаем вывод: 
#### Output:

```
- simonov-inference-predictor-00001-deployment-6bd8fd8f56-d9jzj
```

### Проброс портов

```
- kubectl port-forward pod/$POD_NAME 8080:8080
```

### Сделаем curl с входящими признаками 

```
curl -v \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "content_type": "pd"
    },
    "inputs": [
      {
        "name": "pickup_latitude",
        "datatype": "FP32",
        "shape": [1],
        "data": [40.761432]
      },
      {
        "name": "pickup_longitude",
        "datatype": "FP32",
        "shape": [1],
        "data": [-73.979815]
      },
      {
        "name": "dropoff_latitude",
        "datatype": "FP32",
        "shape": [1],
        "data": [40.748817]
      },
      {
        "name": "dropoff_longitude",
        "datatype": "FP32",
        "shape": [1],
        "data": [-73.985428]
      },
      {
        "name": "passenger_count",
        "datatype": "INT64",
        "shape": [1],
        "data": [2]
      }
    ]
  }' \
  http://127.0.0.1:8080/v2/models/simonov-inference/infer
```
