FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv pip install --system --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.9.1

RUN uv sync --frozen --no-dev --compile-bytecode --link-mode=copy

COPY app ./app
COPY rawdata ./rawdata

ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONPATH="/app"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]