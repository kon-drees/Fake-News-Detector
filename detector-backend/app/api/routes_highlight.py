from fastapi import APIRouter, HTTPException, Request

from app.schemas import TextRequest, HighlightResponse
from app.api.dependencies import (
    extract_article_text_or_raise,
    get_article_extractor,
    get_detector,
)
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/highlight", response_model=HighlightResponse)
async def highlight(request: TextRequest, req: Request) -> HighlightResponse:
    """
    Uses the local BERT model to perform token-level classification.
    Returning the weight of the contribution for each token.
    Positive values represent tokens, which contribute to a Fake News classification.
    """
    # Access the detector initialized in the app's lifespan
    detector = get_detector(req)
    article_extractor = get_article_extractor(req)

    article_text = extract_article_text_or_raise(article_extractor, request.text)

    try:
        result = detector.highlight(article_text)

        return HighlightResponse(highlights=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Highlight generation failed")
        raise HTTPException(status_code=500, detail=str(e))
