# Stage 1: Build frontend assets
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt setup.py setup.cfg README.md ./
COPY backend/ ./backend/

RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir alembic gunicorn

COPY --from=frontend-builder /app/backend/static ./backend/static/

ENV FLASK_APP=backend.app
ENV APP_PROFILE=production
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "backend.app:app"]
