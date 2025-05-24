FROM python:3.11-slim

WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and install the LiveKit CLI tool
RUN curl -sSL https://get.livekit.io | bash

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY scripts/ ./scripts/
COPY images/ ./images/
COPY README.md .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Make the startup script executable
RUN chmod +x /app/scripts/startup.sh

# Command to run the startup script
CMD ["/app/scripts/startup.sh"]
