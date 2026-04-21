FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for sentence‑transformers (optional)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory for persistence
RUN mkdir -p /app/data
VOLUME ["/app/data"]

# Environment variables
ENV FACTS_DB_PATH=/app/facts_db.json
ENV CACHE_DB_PATH=/app/cache.db
ENV MEMORY_DIR=/app/memory
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]