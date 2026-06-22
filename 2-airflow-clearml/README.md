# Итоговое задание по модулю № 7

## Шаги исполнения
- Подготовка инфраструктуры
- Создание пайплайна в Airflow
-  Создание пайплайна в ClearML


## Шаг 1. Подготовка инфраструктуры

#### Примечание:
Так как оба приложения работают на порту 8080 и в боевой среде врядли когда-либо будут развернуты на одной ВМ, то в рамках бережливого производства, а так же здравого смысла, сначала был поднят airflow. Далее были выполнены все задачи на нем и обработанный датасет отправился в S3 хранилище.
Далее airflow был выключен, поднят ClearML, настроен агент и пайплайн загружал уже ранее обработанный датасет и обучал модели на наем. 

### Airflow 
- Установлен по инструкции из урока 
- Файл [docker-compose.yaml](https://mlops.gitlab.yandexcloud.net/s14151511/module-7-final-simonov/-/blob/main/airflow/docker-compose.yml)


 ### ClearML
 - Установлен по инструкции из урока
 - Файл [docker-compose.yaml](https://mlops.gitlab.yandexcloud.net/s14151511/module-7-final-simonov/-/blob/main/clearml/docker-compose.yaml?ref_type=heads)
 - Файл [clearml-secret-sdk.yaml](https://mlops.gitlab.yandexcloud.net/s14151511/module-7-final-simonov/-/blob/main/clearml-secret-sdk.yaml)
 - Файл для ckearml-agent [values.yaml](https://mlops.gitlab.yandexcloud.net/s14151511/module-7-final-simonov/-/blob/main/clearml/values.yaml)
 
 - Разворачивание агента через Helm-чарт:

![alt text](<Снимок экрана — 2026-05-16 в 18.15.16.png>)

 - Скриншоты с UI и агентом:

![alt text](<Снимок экрана — 2026-05-16 в 18.15.59.png>)

 ![alt text](<Снимок экрана — 2026-05-18 в 20.46.22.png>)

 - Скриншот с агентом из CLI:

 ![alt text](<Снимок экрана — 2026-05-16 в 18.15.45.png>)



**Инфраструктура готова. Можем приступать к выполнению задач**

## Шаг 2. Создание пайплайна в Airflow
- Данные загружены в s3 через cli:

![alt text](<Снимок экрана — 2026-05-17 в 12.02.46.png>)

- файл пайплайна, который лежит в /airflow/dags/ - [final_s3.py](https://mlops.gitlab.yandexcloud.net/s14151511/module-7-final-simonov/-/blob/main/airflow/dags/final_s3.py)
- файл со схемой валидации pandera, взят из одноименного урока, [taxi_schema.py](https://mlops.gitlab.yandexcloud.net/s14151511/module-7-final-simonov/-/blob/main/airflow/dags/taxi_schema.py)

- Скриншот успешно отработавшего пайплайна:

![alt text](<Снимок экрана — 2026-05-18 в 17.17.32.png>)

- Отображение обработанных данных через cli:

![alt text](<Снимок экрана — 2026-05-18 в 17.13.54.png>)


## Шаг 3. Создание пайплайна в ClearML

- Файл с пайплайном где паралелельно обучаются 4 модели(2 линейной / 2 дерева решений) с разными гиперпараметрами:
- сам файл  [pipeline_with4_model.py](https://mlops.gitlab.yandexcloud.net/s14151511/module-7-final-simonov/-/blob/main/clearml/pipelines/pipeline_with4_model.py)
- Отработал частично успешно, но не хватило квот:

![alt text](<Снимок экрана — 2026-05-20 в 21.26.14.png>)

- Логи с нехваткой квот: 

![alt text](<Снимок экрана — 2026-05-20 в 21.26.45.png>)

- Локально отрабатывавал штатно(Macbook M4 Pro): 

![alt text](<Снимок экрана — 2026-05-20 в 20.40.45.png>)


- Далее было принято решение уменьшит количество моделей до 2х:
- Файл с пайплайном [pipeline_finall.py](https://mlops.gitlab.yandexcloud.net/s14151511/module-7-final-simonov/-/blob/main/clearml/pipelines/pipeline_finall.py)
- Успешная отработка: 

![alt text](<Снимок экрана — 2026-05-21 в 10.22.25.png>)

- Сохранение лучшей модели в S3: 

![alt text](<Снимок экрана — 2026-05-21 в 11.08.45.png>)



#### Примечание:

Я потратил более 3х дней на то, что бы найти рабочий вариант пайплайна. 
Я 3 дня терзал нейросети, перепробовал кучу вариантов, сносил и ставил все несколько раз с нуля, пробовал на железе для учебы и на железе для проекта, но ни один не отрабатывал через агентов. 
Решение нашлось случайно, стало отрабатывать, если в ф-цию добавить гиперпараметры. Никакой информации не нашел на этот счет, поэтому это мой миниресеч. 

Сделанный по анналогии с примером из учебы, не отрабатывал, падал по ошибке:
- Сам файл пайплайна [pipeline_like_example.py](https://mlops.gitlab.yandexcloud.net/s14151511/module-7-final-simonov/-/blob/main/clearml/pipelines/pipeline_like_example.py)
- Скриншот с ошибкой: 

![alt text](<Снимок экрана — 2026-05-21 в 11.12.10.png>)

- Менял по разному: 

![alt text](<Снимок экрана — 2026-05-21 в 11.21.13.png>)
