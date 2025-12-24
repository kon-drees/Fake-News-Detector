from fastapi import APIRouter, HTTPException, Request

from app.schemas import TextRequest, FactCheckResponse

router = APIRouter()


@router.post("/fact-check", response_model=FactCheckResponse)
async def fact_check(request: TextRequest, req: Request) -> FactCheckResponse:
    fact_checker = req.state.fact_checker

    try:
        result = await fact_checker.run_fact_check(request)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
