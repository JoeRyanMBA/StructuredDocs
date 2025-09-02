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

# Copy critical files first
COPY .enable_blueprints ./

# Copy entire frontend dist directory first
COPY frontend/dist ./frontend/dist

# Check what was actually copied
RUN echo "=== What was copied to frontend/dist ===" && \
    ls -la ./frontend/dist/ && \
    echo "=== Assets directory contents ===" && \
    ls -la ./frontend/dist/assets/ | wc -l && \
    ls -la ./frontend/dist/assets/ | head -10

# Verify critical files exist
RUN echo "=== Critical Files Check ===" && \
    ls -la .enable_blueprints && \
    ls -la ./frontend/dist/index.html && \
    ls -la ./frontend/dist/favicon.ico && \
    echo "=== Assets Check ===" && \
    ls -la ./frontend/dist/assets/ | grep -E "\.(js|css)$" | wc -l && \
    ls -la ./frontend/dist/assets/ | grep index && \
    echo "JS/CSS files found"

# Expose port used by Gunicorn
EXPOSE 8080

# Default command
CMD ["./start.sh"]
