FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies first for better Docker layer caching
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

# Copy application
COPY backend ./backend
COPY migrations ./migrations
COPY alembic.ini ./

# Don't create __pycache__ files
ENV PYTHONDONTWRITEBYTECODE=1

# Make Python output appear immediately in Docker logs
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["sh", "-c", "uv run --no-sync alembic upgrade head && uv run --no-sync uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 2"]