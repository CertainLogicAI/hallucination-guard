# Alpine-based Docker image for deterministic AI brain
# Target size: <150MB

FROM python:3.11-alpine AS builder

# Install build dependencies (only needed for compilation)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    make \
    libffi-dev \
    openssl-dev

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Switch to non-root user
USER appuser

# Expose port (default FastAPI port)
EXPOSE 8000

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]