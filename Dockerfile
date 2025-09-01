# Dockerfile for Flask API
# Builds and runs the backend service using the existing start.sh
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and startup script
COPY backend ./backend
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

# Expose port used by Gunicorn
EXPOSE 8080

# Default command
CMD ["./start.sh"]
