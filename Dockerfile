# Deterministic AI Brain - Production container
# Target: <150MB

FROM python:3.11-alpine AS builder

RUN apk add --no-cache gcc musl-dev libffi-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-alpine

RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

WORKDIR /app
COPY --from=builder /install /usr/local

# Copy application modules
COPY main.py .
COPY token_reduction_engine.py .
COPY deterministic_memory_search.py .
COPY hallucination_detector.py .
COPY hybrid_ai_router.py .
COPY facts_db.json .

# Create directories for runtime data
RUN mkdir -p /app/memory /app/audit && chown -R appuser:appgroup /app

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
