from contextlib import asynccontextmanager
import os
from typing import Dict

from fastapi import FastAPI

from app.api.routes_predict import router as predict_router
from app.api.routes_highlight import router as highlight_router
from app.api.routes_fact_check import router as fact_check_router
from app.core.detector import FakeNewsDetector
from app.core.fact_check_agent import FactCheckAgent


os.environ["TOKENIZERS_PARALLELISM"] = "false"
model = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    detector = FakeNewsDetector()
    fact_checker = FactCheckAgent()

    model["detector"] = detector
    model["fact_checker"] = fact_checker

    app.state.detector = detector
    app.state.fact_checker = fact_checker

    try:
        yield {"detector": detector, "fact_checker": fact_checker}
    finally:
        model.clear()


app = FastAPI(title="Fake News Backend", lifespan=lifespan)
app.include_router(predict_router, prefix="/api")
app.include_router(highlight_router, prefix="/api")
app.include_router(fact_check_router, prefix="/api")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
