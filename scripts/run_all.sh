#!/bin/bash
# This script runs both the health check server and the agent

# Run the Flask health check server in the background
cd /app/scripts
gunicorn flask_health:app --bind 0.0.0.0:$PORT --daemon

# Wait a moment for the health check server to start
sleep 2

# Run the trunk setup 
/app/scripts/startup.sh

# Keep the container alive while the agent(s) run in the background
echo "The voice agent service is running. Check the logs for details."
tail -f /dev/null
