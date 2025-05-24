from __future__ import annotations

import asyncio
import logging
import os
import scripts.agent as agent_module
from scripts.health_check import run_health_server

# Initialize the logger
log = logging.getLogger("agent_wrapper")
log.setLevel(logging.INFO)

if __name__ == "__main__":
    # Start the health check server
    health_thread = run_health_server()
    log.info("Health check server started")
    
    # Run the agent
    log.info("Starting agent")
    agent_module.main()
