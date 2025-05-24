#!/bin/bash
# This script runs trunk.py first and then agent.py with a health check server

# Start the health check server in the background
echo "Starting health check server..."
python -c "from scripts.health_check import run_health_server; run_health_server()" &
health_pid=$!
echo "Health check server started with PID: $health_pid"

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
            python scripts/agent_wrapper.py
            exit 0
        fi
    fi
fi

echo "LiveKit CLI found at: $(which lk)"
echo "Starting Trunk.py..."
python scripts/trunk.py
trunk_exit=$?
if [ $trunk_exit -ne 0 ]; then
    echo "Error: trunk.py failed with exit code $trunk_exit"
    echo "Continuing with agent.py anyway..."
fi

echo "trunk.py completed or skipped."
echo "Starting agent with health check..."
# Run agent_wrapper.py in the foreground
python scripts/agent_wrapper.py
