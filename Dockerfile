FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

EXPOSE 8181

# Use explicit host and port binding
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181"]