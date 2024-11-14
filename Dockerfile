FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# Verify and update apt sources
RUN echo "Verifying apt sources..." && \
    cat /etc/apt/sources.list && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/lib/apt/lists/partial && \
    apt-get update -o Acquire::CompressionTypes::Order::=gz

# Install Python and dependencies
RUN apt-get install -y \
    python3.10 \
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
