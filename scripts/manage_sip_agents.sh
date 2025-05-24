#!/bin/bash
# filepath: c:\Users\DavidJamesLennon\Documents\GitHub\livekit-voice-ai-agent-setup\scripts\manage_sip_agents.sh

set -e

# Load environment variables
if [ -f .env ]; then
  source .env
elif [ -f .env.local ]; then
  source .env.local
fi

# Check if required environment variables are set
if [ -z "$LIVEKIT_URL" ] || [ -z "$LIVEKIT_API_KEY" ] || [ -z "$LIVEKIT_API_SECRET" ]; then
  echo "Error: LiveKit environment variables not set. Please check your .env or .env.local file."
  exit 1
fi

# Function to display usage information
usage() {
  echo "Usage: $0 [command]"
  echo ""
  echo "Commands:"
  echo "  setup-trunk              Setup SIP trunk and dispatch rule"
  echo "  list-calls               List all active calls"
  echo "  end-call [room_name]     End a specific call by room name"
  echo "  start-agent              Start the agent worker"
  echo "  help                     Show this help message"
  echo ""
}

# Setup SIP trunk and dispatch rule
setup_trunk() {
  echo "Setting up SIP trunk and dispatch rule..."
  python3 scripts/trunk.py
}

# List active calls
list_calls() {
  echo "Listing active calls..."
  python3 scripts/manage_calls.py list
}

# End a specific call
end_call() {
  if [ -z "$1" ]; then
    echo "Error: Room name is required for the end-call command."
    exit 1
  fi
  echo "Ending call in room: $1"
  python3 scripts/manage_calls.py end --room "$1"
}

# Start the agent worker
start_agent() {
  echo "Starting the agent worker..."
  python3 scripts/agent.py start
}

# Main command processing
if [ $# -eq 0 ]; then
  usage
  exit 0
fi

case "$1" in
  setup-trunk)
    setup_trunk
    ;;
  list-calls)
    list_calls
    ;;
  end-call)
    end_call "$2"
    ;;
  start-agent)
    start_agent
    ;;
  help)
    usage
    ;;
  *)
    echo "Error: Unknown command '$1'"
    usage
    exit 1
    ;;
esac
