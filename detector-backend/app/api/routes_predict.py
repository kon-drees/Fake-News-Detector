from fastapi import FastAPI

app = FastAPI()

@app.get("/predict")
def health():
    return {"status": "ok"}


@app.get("/highlight")
def health():
    return {"status": "ok"}