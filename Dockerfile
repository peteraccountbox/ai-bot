FROM ubuntu:22.04

# Install Python and other dependencies
RUN apt-get update && \
    apt-get install -y python3.11 python3-pip curl sqlite3 && \
    rm -rf /var/lib/apt/lists/*

# Set working directory to the parent folder that contains both main.py and app/
WORKDIR /workspace

COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy everything to the workspace
COPY . .

COPY app/main.py .

EXPOSE 8181

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181"]