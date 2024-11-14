FROM python:3.11-slim

WORKDIR /workspace

# Only copy what's needed
COPY requirements.txt .

# Install dependencies and cleanup in the same layer
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf ~/.cache/pip/*

# Copy only necessary application files
COPY main.py .
COPY app/ app/

EXPOSE 8181

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181"]
