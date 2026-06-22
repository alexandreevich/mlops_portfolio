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

COPY ./requirements.txt .

RUN uv pip install --no-cache --system -r requirements.txt

COPY src/ .
COPY ranker.pkl item_features.parquet .

EXPOSE 32000
ENTRYPOINT ["python3", "main.py"]