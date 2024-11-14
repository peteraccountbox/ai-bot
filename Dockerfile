FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# Install system and Python dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

EXPOSE 8181

# Use explicit host and port binding
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181"]