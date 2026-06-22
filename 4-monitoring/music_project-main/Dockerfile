FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    libffi-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY ./app/ /app/

# Устанавливаем зависимости
RUN uv pip install --no-cache --system -r requirements.txt

CMD ["gunicorn", "main:app", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120"]
