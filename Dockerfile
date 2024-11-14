FROM python:3.11.7-slim

WORKDIR /workspace

# Install only essential system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

EXPOSE 8181

# Use explicit host and port binding
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181"]