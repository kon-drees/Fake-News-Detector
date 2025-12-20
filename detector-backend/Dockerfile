FROM ghcr.io/astral-sh/uv:python3.13-slim

WORKDIR /app


COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --compile-bytecode --link-mode=copy

COPY app ./app
COPY models ./models
COPY rawdata ./rawdata

ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONPATH="/app"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
