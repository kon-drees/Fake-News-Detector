from fastapi import APIRouter, HTTPException, Request

from app.domain import Label
from app.schemas import PredictionResponse, TextRequest
from app.api.dependencies import (
    extract_article_text_or_raise,
    get_article_extractor,
    get_detector,
)
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: TextRequest, req: Request) -> PredictionResponse:
    """
    Main entry point for BERT-based text classification.
    Analyzes the input text and returns a probability score for both 'REAL' and 'FAKE' labels.
    """
    # Access the detector initialized in the app's lifespan
    detector = get_detector(req)
    article_extractor = get_article_extractor(req)

    article_text = extract_article_text_or_raise(article_extractor, request.text)

    try:
        result = detector.predict(article_text)

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
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e))
