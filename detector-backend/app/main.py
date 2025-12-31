from contextlib import asynccontextmanager
import os
from typing import Dict

from fastapi import FastAPI, Request

from app.api.routes_predict import router as predict_router
from app.api.routes_highlight import router as highlight_router
from app.api.routes_fact_check import router as fact_check_router
from app.core.detector import FakeNewsDetector
from app.core.fact_check_agent import FactCheckAgent
from app.core.logging_config import configure_logging


# Disabling parallelism prevents deadlocks on macOS/Linux when
# the process forks during the LLM agent call.
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# Global storage for heavy model instances to avoid re-loading them on every request.
model = {}
logger = configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading detector and fact checker")
    detector = FakeNewsDetector()
    fact_checker = FactCheckAgent()
    logger.info("Detector and fact checker loaded")

    model["detector"] = detector
    model["fact_checker"] = fact_checker

    app.state.detector = detector
    app.state.fact_checker = fact_checker

    try:
        yield {"detector": detector, "fact_checker": fact_checker}
    finally:
        logger.info("Shutting down application state")
        model.clear()


app = FastAPI(title="Fake News Backend", lifespan=lifespan)
# Route Registration
app.include_router(predict_router, prefix="/api")
app.include_router(highlight_router, prefix="/api")
app.include_router(fact_check_router, prefix="/api")


@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception:
        logger.exception(
            "Unhandled error during %s %s", request.method, request.url.path
        )
        raise


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
