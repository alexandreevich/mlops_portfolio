import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from loaded_models import ranker, item_features
import sсhemas


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

APP_VERSION = "0.0.1"

app = FastAPI(
    title="Retail Recommendation API",
    version=APP_VERSION,
    description="API для выдачи рекомендаций и вероятностей покупки.",
)


@app.get("/health", tags=["system"])
def health_check():
    """
    Проверка состояния сервиса и доступности моделей.
    """
    ok = {
        "ranker_loaded": ranker is not None,
        "items_in_feature_store": len(item_features),
    }
    logger.info(f"Health check: {ok}")
    return {"status": "ok", "details": ok}


@app.get("/version", tags=["system"])
def version():
    return {"version": APP_VERSION, "service": "retail_recsys"}


@app.get("/", tags=["system"])
def root():
    return {"message": "Retail recommender API running", "version": APP_VERSION}


@app.get(
    "/predict_purchase",
    response_model=sсhemas.PredictPurchaseResponse,
    responses={404: {"model": sсhemas.ErrorResponse}},
)
def predict_purchase(itemid: int = 98113, hour: int = 12, weekday: int = 3):
    """Предсказываем вероятность покупки товара"""
    row = item_features[item_features["itemid"] == itemid].copy()
    if row.empty:
        return JSONResponse(status_code=404, content={"error": "item not found"})

    row["hour"] = hour
    row["weekday"] = weekday

    x = row[
        ["views", "purchases", "ctr", "hour", "weekday", "categoryid", "available"]
    ].astype(float)

    prob = float(ranker.predict_proba(x)[0][1])
    return {"itemid": itemid, "purchase_probability": prob}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=32000, workers=1)
