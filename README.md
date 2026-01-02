# Fake News Detector

A fullstack Fake News Detector using FastAPI as backend and Svelte as frontend for scoring news, highlighting token contributions, and a fact-checking agent. 


## Features
- Transformer classifier (EN/DE) using a BERT model. The model is trained with real Data.
- Word highlighting.
- Fact-check agent using `pydantic-ai` 
- Svelte with per Word highlighting, classifications, and fact-checks.
- Docker setup with Nginx 
- Optional Mongo pipelines and dataset URLs for data ingestion and training.

## Repository layout
- `detector-backend/`: FastAPI app (`app/main.py`) plus classifier, fact-check agent, pipelines, and tests.
- `detector-frontend/`: Svelte single-page UI; Nginx config proxies `/api` to the backend.
- `docker-compose.yml`: Local stack (frontend, backend, Mongo).
- `docker-compose.prod.yml`: prebuilt GHCR images.


## Quick start with Docker
The default compose file builds everything locally and exposes the frontend on port 80 and backend on port 8000.

1) Clone the repo. 

2) Start the stack:
   ```bash
   docker compose up --build
   ```
3) Open `http://localhost` for the UI. The backend API is at `http://localhost:8000`.


The prod compose file uses prebuilt GHCR images




## Local development
### Backend 
- Requirements: Python 3.13, optionally MongoDB if you use the data pipelines.
- Install deps and run:
  ```bash
  cd detector-backend
  uv sync
  uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```


### Frontend 
- Requirements: Node 20+
- Install and run dev server:
  ```bash
  cd detector-frontend
  npm install
  VITE_API_URL=http://localhost:8000/api npm run dev -- --host
  ```
- Build/preview: `npm run build && npm run preview`

## API overview
Base URL `/api`.

- `POST /predict` body: `{ "text": "..." }`  classifier label (`fake`|`real`) with confidence.
- `POST /highlight` body: `{ "text": "..." }` token list with SHAP scores (`score_normalized` for heatmap).
- `POST /fact-check`  body: `{ "text": "..." }`  structured fact-check (`fake_score`, `summary_analysis`, `checked_claims`).
- `GET /health`  simple `{ "status": "ok" }`.

Example:
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"Example news paragraph"}'
```


## Deployment notes
- `docker-compose.prod.yml` uses published images (`ghcr.io/kon-drees/fake-news-detector-{backend,frontend}:latest`).
- For fact checking enter a `OPENAI_API_KEY` on the backend service.
