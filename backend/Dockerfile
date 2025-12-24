# PCG Arena Backend Dockerfile
# Protocol: arena/v0

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./

# Copy test files (for running tests in container)
COPY tests/ ./tests/
COPY pytest.ini ./

# Create data directory (will be overwritten by volume mount)
RUN mkdir -p /data

# Environment defaults (can be overridden)
ENV ARENA_DB_PATH=/data/arena.sqlite
ENV ARENA_HOST=0.0.0.0
ENV ARENA_PORT=8080
ENV ARENA_MIGRATIONS_PATH=/migrations
ENV ARENA_SEED_PATH=/seed
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]

