# Stage 1: Build frontend assets
FROM node:20-alpine AS frontend-builder

ARG VITE_BASE_PATH=/
ENV VITE_BASE_PATH=${VITE_BASE_PATH}

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
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 app \
    && useradd --uid 10001 --gid 10001 -m app

COPY requirements.txt setup.py setup.cfg README.md ./
COPY backend/ ./backend/
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN pip install --no-cache-dir -r requirements.txt \
    && chmod 755 /docker-entrypoint.sh

COPY --from=frontend-builder /app/backend/static ./backend/static/

ENV FLASK_APP=backend.app
ENV APP_PROFILE=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=5000
ENV HEALTHCHECK_PATH=/api/health

EXPOSE 5000

# /app stays root-owned and read-only for UID 10001. Logs go to stdout.
# Any named data volume is owned on the VPS (10001:10001). Do not chown it here.
USER 10001:10001

ENTRYPOINT ["/docker-entrypoint.sh"]
# Entrypoint builds the full gunicorn command from PORT (no access log).
CMD ["gunicorn"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "/app/backend/container_healthcheck.py"]

# Bake the git SHA last so earlier layers stay cached across commits.
ARG GIT_SHA
ENV APP_VERSION=$GIT_SHA
