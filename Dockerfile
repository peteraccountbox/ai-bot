FROM python:3.11-slim

WORKDIR /workspace

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

EXPOSE 8181

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181"]