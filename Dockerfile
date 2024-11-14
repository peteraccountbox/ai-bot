FROM python:3.11-slim

WORKDIR /workspace

# Copy only requirements first to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY main.py .
COPY app/ app/

EXPOSE 8181

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181"]