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

# Download and install the LiveKit CLI tool and add it to PATH
RUN curl -sSL https://get.livekit.io | bash && \
    echo 'export PATH=$PATH:/root/.livekit/bin' >> /root/.bashrc && \
    mkdir -p /usr/local/bin && \
    if [ -f /root/.livekit/bin/lk ]; then \
        ln -sf /root/.livekit/bin/lk /usr/local/bin/lk; \
    fi

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY scripts/ ./scripts/
COPY README.md .
COPY Procfile .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV PATH="/root/.livekit/bin:${PATH}"
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Make all scripts executable
RUN chmod +x /app/scripts/*.sh && \
    chmod +x /app/scripts/*.py

# Make sure run_all.sh is executable
RUN chmod +x /app/scripts/run_all.sh

# Set the entry point to run_all.sh
CMD ["/app/scripts/run_all.sh"]
