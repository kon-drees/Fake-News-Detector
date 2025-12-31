from fastapi import APIRouter, HTTPException, Request

from app.schemas import TextRequest, HighlightResponse
from app.api.dependencies import get_detector

router = APIRouter()


@router.post("/highlight", response_model=HighlightResponse)
async def highlight(request: TextRequest, req: Request) -> HighlightResponse:
    """
    Uses the local BERT model to perform token-level classification.
    Returning the weight of the contribution for each token.
    Positive values represent tokens, which contribute to a Fake News classification.
    """
    # Access the detector initialized in the app's lifespan
    detector = get_detector(req)

    try:
        result = detector.highlight(request.text)

        return HighlightResponse(highlights=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
