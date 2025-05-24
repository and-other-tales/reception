from __future__ import annotations

import asyncio
import logging
import os
import sys
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("agent_wrapper")
log.setLevel(logging.INFO)

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Start the health check server directly in a separate process
def start_health_check_server():
    import subprocess
    log.info("Starting health check server as a separate process")
    health_process = subprocess.Popen(["python", os.path.join(current_dir, "health_check.py")], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
    return health_process

if __name__ == "__main__":
    # Start the health check server as a separate process
    health_process = start_health_check_server()
    log.info("Health check server started")
    
    # Give the health check server a moment to start
    time.sleep(2)
    
    try:
        # Run the agent
        log.info("Starting agent")
        import agent
        agent.main()
    except Exception as e:
        log.error(f"Error running agent: {e}")
        # Keep the container running for health checks even if agent fails
        log.info("Keeping container alive for health checks...")
        while True:
            time.sleep(60)
