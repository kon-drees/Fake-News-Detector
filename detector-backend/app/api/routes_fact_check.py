from fastapi import APIRouter, HTTPException, Request

from app.schemas import TextRequest, FactCheckResponse
from app.api.dependencies import get_fact_checker

router = APIRouter()


@router.post("/fact-check", response_model=FactCheckResponse)
async def fact_check(request: TextRequest, req: Request) -> FactCheckResponse:
    fact_checker = get_fact_checker(req)

    try:
        result = await fact_checker.run_fact_check(request)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
