# Retail Recommendation System

Мини-рекомендательная система для e-commerce. 

# Мой итоговый проект

## Выполненные этапы:

### Локально работа модели

- Проект успешно собирается локально 

![alt text](<Снимок экрана — 2026-06-17 в 12.11.30.png>)

- Запросы корректно отрабатывают

![alt text](<Снимок экрана — 2026-06-17 в 12.11.40.png>)

### CI/CD 
- Далее был написан CI / CD [пайплайн](https://mlops.gitlab.yandexcloud.net/s14151511/mlops_final_simonov/-/blob/main/.gitlab-ci.yml), который впоследствии был доработан. Скриншот с успешными первыми джобами: 

![alt text](<Снимок экрана — 2026-06-21 в 16.44.44.png>)

### Обработка данных | Airflow
 
- Далее скрипт обработки данных был перенесен в Airflow - [скрипт](https://mlops.gitlab.yandexcloud.net/s14151511/mlops_final_simonov/-/blob/main/mlops/airflow/preprocessing_data.py) 


- Успешно отрабатывал: 

![alt text](<Снимок экрана — 2026-06-17 в 15.41.16.png>)


- Наличие постобработанных данных в S3 

![alt text](<Снимок экрана — 2026-06-21 в 21.23.19.png>)

### Обучение модели | ClearML

- Далее скрипт по обучению модели был доработан для работы с ClearML - [final.py](https://mlops.gitlab.yandexcloud.net/s14151511/mlops_final_simonov/-/blob/main/mlops/clearml/finall.py)

- Успешная отработка в ClearML :

- ![alt text](<Снимок экрана — 2026-06-21 в 21.20.53.png>)


- Смотрим наличие лучшей модели в S3

![alt text](<Снимок экрана — 2026-06-21 в 21.22.03.png>)

### Deploy | K8S

- Деплоить было решено в K8S, были написаны манифесты: 
- секрет для s3 - [secret.yaml](https://mlops.gitlab.yandexcloud.net/s14151511/mlops_final_simonov/-/blob/main/mlops/deploy/k8s/secret_simonov.yaml)
- сервисный аккаунт с доступом к секреты - [sa-simonov](https://mlops.gitlab.yandexcloud.net/s14151511/mlops_final_simonov/-/blob/main/mlops/deploy/k8s/sa_simonov.yaml)
- Инференс модели KServe - [inference-simonov.yaml](https://mlops.gitlab.yandexcloud.net/s14151511/mlops_final_simonov/-/blob/main/mlops/deploy/k8s/inference-simonov.yaml)

#### И это не заработало, потому что kserve не работает с этим типом моделей. 

- Было решено грузить модель в образ, образ в registry  и оттуда деплоить в k8s.

- В базовый [gitlab-ci.yaml](https://mlops.gitlab.yandexcloud.net/s14151511/mlops_final_simonov/-/blob/main/.gitlab-ci.yml) добавил [блок](https://mlops.gitlab.yandexcloud.net/s14151511/mlops_final_simonov/-/blame/main/.gitlab-ci.yml#L93) загрузки лучшей модели из S3, что бы потом внести ее в свой образ. 
 
- успешно отработваший pipelint: 

![alt text](<Снимок экрана — 2026-06-21 в 22.24.07.png>)

- Добавил токен для работы - [gitlab-regcred](https://mlops.gitlab.yandexcloud.net/s14151511/mlops_final_simonov/-/blob/main/mlops/deploy/k8s/secret_token.yaml)
- Сам [deployment](https://mlops.gitlab.yandexcloud.net/s14151511/mlops_final_simonov/-/blob/main/mlops/deploy/k8s/deployment.yaml)
- Для направления трафика -[Service](https://mlops.gitlab.yandexcloud.net/s14151511/mlops_final_simonov/-/blob/main/mlops/deploy/k8s/service.yaml) 
- Поды / сервис / сервисные аккаунты / секреты, все на месте: 

- ![alt text](<Снимок экрана — 2026-06-21 в 21.53.10.png>)

- Делаем проброс порта и смотрим что все работает: 

- ![alt text](<Снимок экрана — 2026-06-19 в 11.43.34.png>)

- ![alt text](<Снимок экрана — 2026-06-19 в 11.44.02.png>)


### Мониторинг  | Grafana / Prometheus / cAdvisor

- Хотел задеплоить helm-chart с мониторингом, но квот на это нет

- ![alt text](<Снимок экрана — 2026-06-21 в 21.56.13.png>)

- Чтож, изобретать еще один велосипед не хотелось, поэтому я задеплоил через [docker-compose.yaml]() на ВМ.

- Рабочий cAdvisor: 

- ![alt text](<Снимок экрана — 2026-06-19 в 13.09.22.png>)

- prometheus 

- ![alt text](<Снимок экрана — 2026-06-19 в 13.09.27.png>)

- Grafana 

- ![alt text](<Снимок экрана — 2026-06-21 в 16.18.42.png>)



### Небольшое послесловие 

- Честно говоря, проект вышел немгого неоднородным - часть там логики там, часть там, часть еще где-то. И как то это пахнет несовершенством. Но с другой стороны, я показал что овладел всеми инструментами, и в условиях рынка РФ в неоднорондных ИТ-ландшафтах РФ Фин/Биг-техов найду примерение этим навыкам. 








## Чек-лист подсказок для выполнения проекта

Переходите по пунктам и отмечайте выполненные задачи!

- [x] **.gitlab-ci.yml**  
      ➡️ Проверьте конфигурацию CI/CD. Настройте автоматическую сборку и тестирование, чтобы всё работало без сбоев.

- [x] **pyproject.toml**  
      ➡️ Настройте этот файл: пропишите параметры для проверки качества кода (`ruff`), тестирования (`pytest`) и статической типизации (`mypy`).

- [x] **Unit-тесты**  
      ➡️ Напишите хотя бы несколько базовых unit-тестов, чтобы проверить, что ключевые части вашего кода работают корректно.

- [x] **Ruff & Code style**  
      ➡️ Проверьте код с помощью `ruff`. Исправьте все ошибки форматирования и приведите стиль к требованиям PEP8 и стандарту `black`.

- [x] **mypy & Аннотации типов**  
      ➡️ Запустите `mypy` и исправьте все ошибки. Проверьте, что типы данных явно указаны во всех функциях, где это требуется.

- [x] **Работа с данными**  
      ➡️ Если ваши данные сейчас хранятся в проекте (например, `.csv` или `.parquet`), перепишите код так, чтобы использовать внешнее хранилище (например, S3).  
      ⚠️ _Данные не должны лежать в репозитории!_

- [x] **Docker: подготовка к деплою**  
      ➡️ Напишите `Dockerfile` для сборки Docker-образа вашего приложения.

- [x] **docker-compose.yaml (если деплой на ВМ)**  
      ➡️ Для развертывания приложения на виртуальной машине добавьте файл `docker-compose.yaml`.

- [x] **Конфигурации для мониторинга и k8s**  
      ➡️ Для интеграции с Grafana, Prometheus или развёртывания в k8s подготовьте необходимые конфиги.

---