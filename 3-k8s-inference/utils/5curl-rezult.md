# Ввод Curl в соседнем терминале (в предидущем port-forward) и его вывод
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
*   Trying 127.0.0.1:8080...
* Connected to 127.0.0.1 (127.0.0.1) port 8080
> POST /v2/models/simonov-inference/infer HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/8.7.1
> Accept: */*
> Content-Type: application/json
> Content-Length: 729
>
* upload completely sent off: 729 bytes
< HTTP/1.1 200 OK
< date: Fri, 29 May 2026 13:50:37 GMT
< server: uvicorn
< content-length: 225
< content-type: application/json
<
* Connection #0 to host 127.0.0.1 left intact
{"model_name":"simonov-inference","model_version":null,"id":"48e7ff12-8f98-4739-9c59-935e996d9d2f","parameters":null,"outputs":[{"name":"output-0","shape":[1],"datatype":"FP64","parameters":null,"data":[11.362126271319786]}]}%
```