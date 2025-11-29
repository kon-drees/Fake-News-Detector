from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI

from app.api.routes_predict import router as predict_router
from app.api.routes_highlight import router as highlight_router
from app.core.detector import FakeNewsDetector


model = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    model["detector"] = FakeNewsDetector()
    yield {"detector": model["detector"]}
    model.clear()


app = FastAPI(title="Fake News Backend", lifespan=lifespan)
app.include_router(predict_router, prefix="/api")
app.include_router(highlight_router, prefix="/api")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
