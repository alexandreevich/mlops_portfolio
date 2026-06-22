# Настройка проекта с нуля

 - Я устал каждый раз лазить по курсу, поэтому соберу все тут.

 ### Как настроить
#### Сначала проверим есть ли это говно на моей тачке: 
 - uv --version
#### Инициируем проект и фиксируем змея:  
 - uv init -p 3.12
 - uv add numpy==1.23.2
 - uv add "clearml[s3]==2.0.2"
 - uv add pandas==2.3.2 ruff==0.12.11 scikit-learn==1.7.1
 - uv add fsspec==2025.9.0 s3fs==2025.9.0 

#### Переходим на тачку, где развернем ClearML
- sudo -i 
##### Создаем дирректории
- mkdir -p /opt/clearml/data/elastic_7  
- mkdir -p /opt/clearml/data/mongo_4/db  
- mkdir -p /opt/clearml/data/mongo_4/configdb  
- mkdir -p /opt/clearml/data/redis  
- mkdir -p /opt/clearml/logs  
- mkdir -p /opt/clearml/config  
- mkdir -p /opt/clearml/data/fileserver

##### Шарим права
- chown -R 1000:1000 /opt/clearml
-chown -R 1000:1000 /opt/clearml

##### добавляем docker-compose.yaml
- docker compose -f docker-compose.yaml up -d

#### Поднянуть конфиг после инициализации 
export CLEARML_CONFIG_FILE=$(pwd)/clearml.conf
uv run clearml-init

#### Поменять контекст в k8s 
- кладем его в new-cluster-config.yaml
##### Запускаем 
- KUBECONFIG=~/.kube/config:new-cluster-config.yaml \
kubectl config view --flatten > ~/.kube/config-merged

- mv ~/.kube/config-merged ~/.kube/config

- kubectl config get-contexts

- kubectl config use-context mlops-cluster

- kubectl config current-context
