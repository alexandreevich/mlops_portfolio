# Рабочие команды для awscli: 
## Установить через uv awscli:
uv pip install awscli~=1.42.16
## Сначала закинуть переменные окружения: 
export AWS_ACCESS_KEY_ID=***
export AWS_SECRET_ACCESS_KEY=***
export S3_BUCKET_NAME=r-mlops-bucket-12-1-1-854415502
export S3_ENDPOINT_URL=https://storage.yandexcloud.net

# Далее работать в формате : 
uv run aws s3 ls s3://$S3_BUCKET_NAME/raw_data/ --endpoint-url $S3_ENDPOINT_URL


# Как подтянуть конфиг clearml:
export CLEARML_CONFIG_FILE=$(pwd)/clearml.conf

uv run clearml-init

### пример команды 
aws s3 cp train.csv\
       s3://$S3_BUCKET_NAME/raw_data/train.csv\
       --endpoint-url $S3_ENDPOINT_URL