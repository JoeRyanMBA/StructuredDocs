# Dockerfile for Flask API
# Builds and runs the backend service using the existing start.sh
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and startup script
COPY backend ./backend
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

# Copy frontend files with verification
RUN mkdir -p ./frontend/dist/assets
COPY frontend/dist/index.html ./frontend/dist/
COPY frontend/dist/assets/ ./frontend/dist/assets/
COPY .enable_blueprints ./

# List contents to verify copy
RUN echo "=== Frontend dist contents ===" && ls -la ./frontend/dist/ && \
    echo "=== Assets contents ===" && ls -la ./frontend/dist/assets/ | grep -E "\.(js|css)$" | head -5

# Expose port used by Gunicorn
EXPOSE 8080

# Default command
CMD ["./start.sh"]
