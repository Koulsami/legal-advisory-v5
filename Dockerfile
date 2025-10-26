# Legal Advisory System v5.0 - Production Dockerfile
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

# Create non-root user
RUN useradd -m -u 1000 legaladvisor && \
    mkdir -p /app && \
    chown -R legaladvisor:legaladvisor /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder --chown=legaladvisor:legaladvisor /root/.local /home/legaladvisor/.local

# Copy application code
COPY --chown=legaladvisor:legaladvisor backend ./backend
COPY --chown=legaladvisor:legaladvisor tests ./tests
COPY --chown=legaladvisor:legaladvisor demo ./demo
COPY --chown=legaladvisor:legaladvisor examples ./examples

# Copy documentation (optional, for reference)
COPY --chown=legaladvisor:legaladvisor *.md ./

# Switch to non-root user
USER legaladvisor

# Add local Python packages to PATH
ENV PATH=/home/legaladvisor/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT}/health').raise_for_status()" || exit 1

# Expose port
EXPOSE ${PORT}

# Run the application
CMD ["uvicorn", "backend.api.routes:app", "--host", "0.0.0.0", "--port", "8000"]
