from fastapi import APIRouter, HTTPException, Request

from app.schemas import TextRequest, HighlightResponse

router = APIRouter()


@router.post("/highlight", response_model=HighlightResponse)
async def highlight(request: TextRequest, req: Request) -> HighlightResponse:
    detector = req.state.detector

    try:
        result = detector.highlight(request.text)

        return HighlightResponse(highlights=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
