FROM python:3.12-slim AS builder

ARG POETRY_VERSION=1.7.1
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR="/var/cache/pypoetry" \
    PATH="$POETRY_HOME/bin:$PATH"


RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential libpq-dev netcat-openbsd libpq5 && \
    curl -sSL https://install.python-poetry.org | python3 - --version "$POETRY_VERSION" && \
    ln -s "${POETRY_HOME}/bin/poetry" /usr/local/bin/poetry

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --no-dev

COPY . .

FROM python:3.12-slim AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd libpq5 && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/poetry.lock /app/
COPY --from=builder /app/config /app/config
COPY --from=builder /app/data /app/data

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
EXPOSE 8080 7860

CMD ["sh", "-c", "exec python -m src.main"]
