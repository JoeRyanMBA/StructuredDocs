# Multi-stage Dockerfile for reliable builds
# Stage 1: Build frontend
FROM node:22-alpine as frontend-builder

WORKDIR /app

# Copy frontend directory
COPY frontend/ ./frontend/

# Install dependencies and build
WORKDIR /app/frontend
RUN npm ci
RUN npm run build

# Verify build output
RUN ls -la dist/ && \
    ls -la dist/assets/ | head -5 && \
    echo "Build verification: $(ls dist/assets/ | wc -l) files"

# Stage 2: Python application
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend ./backend
COPY start.sh ./start.sh
COPY .enable_blueprints ./
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
