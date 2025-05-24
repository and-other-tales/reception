#!/bin/bash
# This script runs trunk.py first and then agent.py

echo "Starting Trunk.py..."
python scripts/trunk.py
if [ $? -ne 0 ]; then
    echo "Error: trunk.py failed with exit code $?"
    exit 1
fi

echo "trunk.py completed successfully."
echo "Starting agent.py..."
python scripts/agent.py
