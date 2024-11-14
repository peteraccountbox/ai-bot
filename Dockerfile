FROM python:3.11-slim

WORKDIR /workspace

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY app/ app/

EXPOSE 8181

# Use explicit host and port binding
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181", "--reload"]