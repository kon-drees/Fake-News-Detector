from fastapi import APIRouter
from app.schemas import PredictionResponse

router = APIRouter()


@router.get("/predict", response_model=PredictionResponse)
def predict():
    return PredictionResponse(
        label="fake",
        probabilities={"fake": 0.8, "real": 0.2},
    )


@router.get("/highlight")
def highlight():
    return {"status": "ok"}
