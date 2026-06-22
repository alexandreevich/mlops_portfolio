import time
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from recommender import load_model, recommend_songs
from schemas import RecommendationResponse

# --- Инициализация FastAPI ---
app = FastAPI(
    title="Spotify Recommender API",
    description="Получи рекомендации похожих песен по названию трека на основе косинусного сходства.",
    version="1.0.0",
    contact={
        "name": "Your Name",
        "email": "your_email@example.com",
    },
)

# --- Загрузка модели ---
model = load_model()

# --- Prometheus метрики ---
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Общее количество запросов к приложению",
    ["endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Задержка обработки запроса в секундах",
    ["endpoint"]
)
IN_PROGRESS = Gauge(
    "app_inprogress_requests",
    "Количество одновременно обрабатываемых запросов"
)

# --- Endpoints ---

@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "🎶 Spotify Recommender is running! Check this out!"}


@app.get("/metrics")
def metrics():
    """Endpoint для Prometheus"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get(
    "/api/recommend/",
    response_model=RecommendationResponse,
    summary="Получить рекомендации по песне",
    tags=["Recommendations"],
)
def get_recommendations(
    track_title: str = Query(..., description="Название песни для поиска"),
    N: int = Query(5, alias="n", ge=1, le=20, description="Количество рекомендаций"),
):
    start_time = time.time()
    IN_PROGRESS.inc()  # начало обработки
    try:
        recommendations = recommend_songs(model, track_title, N)
        if not recommendations:
            REQUEST_COUNT.labels(endpoint="/api/recommend/", http_status=404).inc()
            raise HTTPException(
                status_code=404,
                detail=f"Трек '{track_title}' не найден в базе данных."
            )

        REQUEST_COUNT.labels(endpoint="/api/recommend/", http_status=200).inc()
        return {
            "requested_track": track_title,
            "recommendations": recommendations[0],
            "similarity_scores": recommendations[1],
        }
    finally:
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint="/api/recommend/").observe(latency)
        IN_PROGRESS.dec()  # конец обработки


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=32000, workers=1)