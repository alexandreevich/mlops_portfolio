from pydantic import BaseModel, Field


class PredictPurchaseRequest(BaseModel):
    itemid: int
    hour: int = Field(..., ge=0, le=23)
    weekday: int = Field(..., ge=1, le=7)


class PredictPurchaseResponse(BaseModel):
    itemid: int
    purchase_probability: float


class ErrorResponse(BaseModel):
    error: str
