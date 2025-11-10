from fastapi import FastAPI
from app.api.routes_predict import router as predict_router

app = FastAPI(title="Fake News Backend")
app.include_router(predict_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
