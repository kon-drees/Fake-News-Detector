from fastapi import APIRouter, HTTPException, Request

from app.domain import Label
from app.schemas import PredictionResponse, TextRequest
from app.api.dependencies import get_detector

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: TextRequest, req: Request) -> PredictionResponse:
    """
    Main entry point for BERT-based text classification.
    Analyzes the input text and returns a probability score for both 'REAL' and 'FAKE' labels.
    """
    # Access the detector initialized in the app's lifespan
    detector = get_detector(req)

    try:
        result = detector.predict(request.text)

        fake_score = (
            result.score if result.label == Label.FAKE else round(1 - result.score, 4)
        )
        real_score = result.score if result.label == Label.REAL else 1 - result.score

        return PredictionResponse(
            prediction_result=result,
            confidence_fake=fake_score,
            confidence_real=real_score,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
