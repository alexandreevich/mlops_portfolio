#  Module 8 Сервис рекомендации цен на поездку такси

# Часть 1
## В первой части необходимо было обучить модель, ковертировать в ONNX формат и провести базовый тест производительности модели, а результаты сохранить. 

### Обучение модели

Как видно в скриншоте, модель успешно обучена. 

![alt text](<Снимок экрана — 2026-05-29 в 09.24.14.png>)

### Конвертация модели

- Для успешной ковертации модели, сначала необходимо определить тип данных входящих признаков. 
- Для этого был сделан скрипт - [1type_of_features.py](https://mlops.gitlab.yandexcloud.net/s14151511/module-8-final-simonov/-/blob/main/utils/1type_of_features.py)
- По его итогам был написан скрипт для конвертации [2convert.py](https://mlops.gitlab.yandexcloud.net/s14151511/module-8-final-simonov/-/blob/main/utils/2convert.py)


### Замер скорости

- Для замера был использован и адаптирован скрипт из учебного примера - [3zamer.py](https://mlops.gitlab.yandexcloud.net/s14151511/module-8-final-simonov/-/blob/main/utils/3zamer.py)
- Данные сохранены в файле [profile_onnx_AlexandrSimonv.json](https://mlops.gitlab.yandexcloud.net/s14151511/module-8-final-simonov/-/blob/main/profile_onnx_AlexandrSimonv.json)
- Скриншот отработки скрипта: 

![alt text](<Снимок экрана — 2026-05-29 в 16.16.55.png>)

### Сохранение в S3

- [Модель](https://mlops.gitlab.yandexcloud.net/s14151511/module-8-final-simonov/-/blob/main/model.pkl) была успешно сохранена в S3 хранилище: 

![alt text](<Снимок экрана — 2026-05-29 в 16.21.53.png>)

# Часть 2

## Во второй части, неободимо было задеплоить модель в выделенный namespace k8s.

### Для деплоя были собраны манифесты: 

- [secret-simonov.yaml](https://mlops.gitlab.yandexcloud.net/s14151511/module-8-final-simonov/-/blob/main/k8s/secret_simonov.yaml) - в нем хранятся ключи для подключения модели к S3 
- [sa-simonov.yaml](https://mlops.gitlab.yandexcloud.net/s14151511/module-8-final-simonov/-/blob/main/k8s/sa_simonov.yaml) - в нем мы задаеим сервисный акк с доступам к предидущему секрету
- [inference-simonov.yaml](https://mlops.gitlab.yandexcloud.net/s14151511/module-8-final-simonov/-/blob/main/k8s/inference-simonov.yaml) - основной файл деплоя, где мы описываем как будет развернута модель и при какой нагрузке произойдет автоскелинг. 

### Скриншоты с деплоем / curl 

-  Все манифесты были успешно задеплоены: 

![alt text](<Снимок экрана — 2026-05-29 в 16.53.11.png>)

- Для обращения к модели был использован файл: [4curl.md](https://mlops.gitlab.yandexcloud.net/s14151511/module-8-final-simonov/-/blob/main/utils/4curl.md)

![alt text](<Снимок экрана — 2026-05-29 в 16.50.47.png>)

- Результат был зарегистрирован в файле:  [5curl-rezult.md](https://mlops.gitlab.yandexcloud.net/s14151511/module-8-final-simonov/-/blob/main/utils/5curl-rezult.md)

![alt text](<Снимок экрана — 2026-05-29 в 16.50.55.png>)

