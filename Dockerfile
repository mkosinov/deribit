FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --system --frozen --no-dev --no-install-project

COPY src/price_ticker ./src/price_ticker

WORKDIR /app/src/price_ticker
