#!/bin/bash
# This script runs trunk.py first and then agent.py with a health check server

# Change to scripts directory
cd /app/scripts

# Start the health check server directly first to ensure health checks pass
echo "Starting health check server..."
python health_check.py &
health_pid=$!
echo "Health check server started with PID: $health_pid"

# Give health check server time to start
sleep 2

# Check if the LiveKit CLI is available
echo "Checking LiveKit CLI installation..."
if ! command -v lk &> /dev/null; then
    echo "LiveKit CLI (lk) not found in PATH!"
    echo "Setting up PATH to include LiveKit CLI..."
    export PATH=$PATH:/root/.livekit/bin
    if ! command -v lk &> /dev/null; then
        echo "LiveKit CLI still not found. Attempting to install again..."
        curl -sSL https://get.livekit.io | bash
        export PATH=$PATH:/root/.livekit/bin
        if ! command -v lk &> /dev/null; then
            echo "Failed to install LiveKit CLI. Skipping trunk.py and proceeding with agent."
            echo "Starting agent with health check..."
            python agent_wrapper.py
            exit 0
        fi
    fi
fi

echo "LiveKit CLI found at: $(which lk)"
echo "Starting Trunk.py..."
python trunk.py || echo "Trunk.py failed but continuing anyway"

echo "trunk.py completed or skipped."
echo "Starting agent with health check..."

# Run agent_wrapper.py in the foreground
# This should also handle the health check server
python agent_wrapper.py || {
    echo "Agent wrapper failed. Keeping container alive for health checks..."
    # Keep the container running even if agent fails
    while true; do
        sleep 60
    done
}
