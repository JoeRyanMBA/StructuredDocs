# Multi-stage Dockerfile for reliable builds
# Force rebuild: 2025-09-02
# Stage 1: Build frontend
FROM node:22-alpine as frontend-builder

WORKDIR /app

# Copy package files first for better caching (works with or without lockfile)
COPY frontend/package*.json ./frontend/

# Install dependencies (use npm ci if lockfile exists, otherwise npm install)
WORKDIR /app/frontend
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy the rest of the frontend source
WORKDIR /app
COPY frontend/ ./frontend/

# Build the application
WORKDIR /app/frontend
RUN npm run build

# Verify build output exists
RUN test -d dist && test -f dist/index.html && echo "Build successful" || (echo "Build failed" && exit 1)

# Stage 2: Python application
FROM python:3.11-slim as backend

# Build metadata args (optional; provided by CI)
ARG APP_VERSION
ARG GIT_COMMIT
ARG BUILD_TIME
ENV APP_VERSION=${APP_VERSION} \
    GIT_COMMIT=${GIT_COMMIT} \
    BUILD_TIME=${BUILD_TIME}

# Install system dependencies including pandoc for document conversion
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend ./backend
COPY start.sh ./start.sh
COPY .enable_blueprints ./
COPY run_migrations_production.py ./run_migrations_production.py
RUN chmod +x ./start.sh

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

EXPOSE 8080
CMD ["./start.sh"]
