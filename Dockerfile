FROM ubuntu:22.04

# Install Python and other dependencies
RUN apt-get update && \
    apt-get install -y python3.11 python3-pip curl sqlite3 && \
    rm -rf /var/lib/apt/lists/*

# Set working directory to root where main.py is located
WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy everything to the current directory
COPY . .

# Debug commands (optional, remove in production)
RUN pwd && ls -la

EXPOSE 8181

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181"]