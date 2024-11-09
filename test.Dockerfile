# Use Python 3.9 slim image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt .
COPY test_requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r test_requirements.txt

# Copy source code and tests
COPY src/ src/
COPY tests/ tests/
COPY pyproject.toml .
COPY .pylintrc .

# Create directories for test output
RUN mkdir -p test_output htmlcov

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV TESTING=true

# Set default command to run tests
CMD ["pytest", "-v", "--cov=src", "--cov-report=xml", "--cov-report=html"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
