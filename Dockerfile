# Railway-Optimized Dockerfile for Legal Advisory System v5.0
# Simplified for Railway deployment reliability

FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies FIRST (better caching)
# Cache bust: 2025-01-26-anthropic
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Copy application code
COPY backend ./backend
COPY tests ./tests
COPY demo ./demo
COPY examples ./examples
COPY *.md ./

# Create non-root user for security
RUN useradd -m -u 1000 legaladvisor && \
    chown -R legaladvisor:legaladvisor /app

USER legaladvisor

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["./start.sh"]
