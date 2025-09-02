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

# Create frontend directory structure
RUN mkdir -p ./frontend/dist/assets

# Copy frontend files explicitly
COPY frontend/dist/index.html ./frontend/dist/
COPY frontend/dist/favicon.ico ./frontend/dist/
COPY frontend/dist/assets/ ./frontend/dist/assets/

# Ensure assets directory has all files
RUN echo "=== Assets directory before verification ===" && \
    ls -la ./frontend/dist/assets/ && \
    echo "=== Checking for index files ===" && \
    ls -la ./frontend/dist/assets/ | grep index || echo "No index files found"

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
