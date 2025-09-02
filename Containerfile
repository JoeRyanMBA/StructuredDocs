# Containerfile for Podman (alternative to Dockerfile)
FROM docker.io/python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python requirements first (for better caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend ./backend
COPY start.sh ./start.sh
COPY .enable_blueprints ./
RUN chmod +x ./start.sh

# Copy frontend with verification
COPY frontend/dist ./frontend/dist

# Verify copy
RUN ls -la ./frontend/dist/assets/ | grep -E "\.(js|css)$" | wc -l

EXPOSE 8080
CMD ["./start.sh"]
