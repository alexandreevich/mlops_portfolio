#!/bin/bash
set -e  # Выход при первой ошибке

# Получаем параметры
CI_PROJECT_NAME="$1"
CI_COMMIT_SHORT_SHA="$2"

echo "Project: $CI_PROJECT_NAME, Commit: $CI_COMMIT_SHORT_SHA"

# deploy.sh - Скрипт развертывания FastAPI приложения

SERVICE_NAME="taxi_recommendation_service"
WORKING_DIR="/projects/taxi_recomendation_service"
VENV_DIR="$WORKING_DIR/.venv"
PYTHON_VERSION="3.12"
APP_MODULE="main:app"
HOST="0.0.0.0"
PORT="8002"

# Абсолютный путь к uv
UV_BIN="/usr/local/bin/uv"

echo "Starting deployment of $SERVICE_NAME"

# Создаем рабочую директорию если не существует
sudo mkdir -p $WORKING_DIR
sudo chown $USER:$USER $WORKING_DIR
cd $WORKING_DIR

# Останавливаем сервис если он запущен
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "Stopping existing service..."
    sudo systemctl stop $SERVICE_NAME
fi

# Удаляем предыдущую версию файлов в директории кроме .venv
echo "Cleaning up old files (except .venv)..."
find . -maxdepth 1 ! -name '.venv' ! -name '.' ! -name '..' -exec rm -rf {} +

# Копируем файлы из временной директории
echo "Copying application files..."
cp /tmp/model.pkl .
cp /tmp/deploy.sh .ss
cp /tmp/requirements.txt .
cp /tmp/main.py .
cp /tmp/schemas.py .
cp /tmp/predictor.py .

# Проверяем наличие uv, если нет — ставим в /usr/local/bin через UV_INSTALL_DIR
if ! command -v uv >/dev/null 2>&1 && [ ! -x "$UV_BIN" ]; then
    echo "Installing uv into /usr/local/bin..."
    curl -LsSf https://astral.sh/uv/install.sh | sudo env UV_INSTALL_DIR="/usr/local/bin" UV_NO_MODIFY_PATH=1 sh
    hash -r || true
fi

# Проверяем, что uv действительно доступен по ожидаемому пути
if [ ! -x "$UV_BIN" ]; then
    echo "Error: uv not found at $UV_BIN after installation! Check the UV_NO_MODIFY_PATH"
    exit 1
fi

# Создаем виртуальное окружение если не существует
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    $UV_BIN venv --python $PYTHON_VERSION $VENV_DIR
fi

# Активируем venv и устанавливаем зависимости
echo "Installing dependencies..."
source $VENV_DIR/bin/activate
$UV_BIN pip install --upgrade pip
$UV_BIN pip install -r requirements.txt

# Создаем systemd service файл
echo "Configuring systemd service..."
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=Music Recommendation Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$WORKING_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/uvicorn $APP_MODULE --host $HOST --port $PORT

Restart=always
RestartSec=3
StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target
EOF

# Даем права на файлы
sudo chown -R $USER:$USER $WORKING_DIR
chmod -R 755 $WORKING_DIR

# Перезагружаем systemd и включаем автозагрузку
echo "Reloading systemd and enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

# Запускаем сервис
echo "Starting service..."
sudo systemctl start $SERVICE_NAME

# Проверяем статус
echo "Checking service status..."
sleep 5

if systemctl is-active --quiet $SERVICE_NAME; then
    echo "Service $SERVICE_NAME is running successfully!"
else
    echo "Service failed to start"
    sudo systemctl status $SERVICE_NAME --no-pager -l
    exit 1
fi

echo "Deployment completed successfully!"
