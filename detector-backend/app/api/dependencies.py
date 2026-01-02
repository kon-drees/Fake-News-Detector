from fastapi import HTTPException, Request
from app.services.article_extractor import ArticleExtractor


def get_detector(req: Request):
    detector = getattr(req.state, "detector", None) or getattr(
        req.app.state, "detector", None
    )
    if detector is None:
        raise HTTPException(
            status_code=503, detail="Detector service is not available right now."
        )
    return detector


def get_fact_checker(req: Request):
    fact_checker = getattr(req.state, "fact_checker", None) or getattr(
        req.app.state, "fact_checker", None
    )
    if fact_checker is None:
        raise HTTPException(
            status_code=503, detail="Fact checker service is not available right now."
        )
    return fact_checker


def get_article_extractor(req: Request) -> ArticleExtractor:
    extractor = getattr(req.state, "article_extractor", None) or getattr(
        req.app.state, "article_extractor", None
    )
    if extractor is None:
        raise HTTPException(
            status_code=503, detail="Article extractor service is not available right now."
        )
    return extractor


def extract_article_text_or_raise(
    extractor: ArticleExtractor, raw_input: str
) -> str:
    """
    Resolves raw input (text or URL) into article text using the extractor.
    """
    try:
        extraction = extractor.process(raw_input)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Article extraction failed: {exc}"
        ) from exc

    if not extraction.get("success"):
        raise HTTPException(
            status_code=400,
            detail=extraction.get("error") or "Article extraction failed.",
        )

    text = extraction.get("text")
    if not text:
        raise HTTPException(
            status_code=422,
            detail="Article extraction did not return any text.",
        )

    return text
