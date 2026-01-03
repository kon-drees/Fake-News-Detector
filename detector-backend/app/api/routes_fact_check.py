from fastapi import APIRouter, HTTPException, Request

from app.schemas import TextRequest, FactCheckResponse
from app.api.dependencies import (
    extract_article_text_or_raise,
    get_article_extractor,
    get_fact_checker,
)
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/fact-check", response_model=FactCheckResponse)
async def fact_check(request: TextRequest, req: Request) -> FactCheckResponse:
    """
    Performs a linguistic and factual analysis of the provided text.
    The analysis is performed by GPT-5-nano
    """
    # Access the agent initialized in the app's lifespan
    fact_checker = get_fact_checker(req)
    article_extractor = get_article_extractor(req)

    article_text = extract_article_text_or_raise(article_extractor, request.text)

    try:
        result = await fact_checker.run_fact_check(article_text)

        return result
    except Exception as e:
        logger.exception("Fact check failed")
        raise HTTPException(status_code=500, detail=str(e))
