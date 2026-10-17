# Multi-architecture Dockerfile compatible with IBM Z (s390x) and x86_64
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    CLEANCONNECT_DATABASE=/app/cleanconnect.db

WORKDIR /app

# Install minimal OS dependencies required for native builds on IBM Z (s390x) & Linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    python3-dev \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY cleanconnect.db ./cleanconnect.db
COPY .env* ./

# Expose server port
EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command to run FastAPI uvicorn server on IBM Z
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
