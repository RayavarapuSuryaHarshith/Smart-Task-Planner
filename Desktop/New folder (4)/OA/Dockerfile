# Multi-stage Dockerfile
# 1) Build frontend with Node and Vite
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend

# Copy frontend sources and install
COPY frontend/package*.json ./
COPY frontend/vite.config.js ./
COPY frontend/ ./
RUN npm ci && npm run build

# 2) Python runtime image
FROM python:3.11-slim
WORKDIR /app

# Install minimal OS deps (if needed) and Python deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy built frontend static files from the frontend-build stage.
# Vite config writes build to ../app/static when running inside /app/frontend,
# so the build output will be at /app/app/static in the frontend stage.
COPY --from=frontend-build /app/app/static ./app/static

# Copy the rest of the application
COPY . .

ENV PORT=8000
EXPOSE 8000

# Run uvicorn directly. For production you can replace this with Gunicorn + Uvicorn workers.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
