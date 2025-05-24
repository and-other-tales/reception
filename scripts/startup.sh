#!/bin/bash
# This script runs trunk.py first and then agent.py with a health check server

# Start the health check server in the background
echo "Starting health check server..."
python -c "from scripts.health_check import run_health_server; run_health_server()" &
health_pid=$!
echo "Health check server started with PID: $health_pid"

echo "Starting Trunk.py..."
python scripts/trunk.py
if [ $? -ne 0 ]; then
    echo "Error: trunk.py failed with exit code $?"
    exit 1
fi

echo "trunk.py completed successfully."
echo "Starting agent with health check..."
# Run agent_wrapper.py in the foreground
python scripts/agent_wrapper.py
