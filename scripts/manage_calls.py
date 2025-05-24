# filepath: c:\Users\DavidJamesLennon\Documents\GitHub\livekit-voice-ai-agent-setup\scripts\manage_calls.py

import argparse
import json
import os
import sys
import logging
from dotenv import load_dotenv
import subprocess
from datetime import datetime, timezone

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("call_manager")

def get_active_rooms(livekit_url, livekit_api_key, livekit_api_secret):
    """Get all active rooms from LiveKit"""
    try:
        # Use lk CLI to list active rooms
        result = subprocess.run(
            [
                'lk', 'room', 'list', 
                '--url', livekit_url.replace("wss", "https"), 
                '--api-key', livekit_api_key, 
                '--api-secret', livekit_api_secret,
                '--json'
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logging.error(f"Error executing room list command: {result.stderr}")
            return []
        
        # Parse the JSON output
        try:
            rooms = json.loads(result.stdout)
            # Filter for call rooms (those starting with "call-")
            call_rooms = [room for room in rooms if room.get('name', '').startswith('call-')]
            return call_rooms
        except json.JSONDecodeError:
            logging.error(f"Failed to parse room list output: {result.stdout}")
            return []
            
    except Exception as e:
        logging.error(f"Error getting active rooms: {str(e)}")
        return []

def get_room_participants(room_name, livekit_url, livekit_api_key, livekit_api_secret):
    """Get participants in a specific room"""
    try:
        # Use lk CLI to list participants in the room
        result = subprocess.run(
            [
                'lk', 'room', 'list-participants', 
                '--room', room_name,
                '--url', livekit_url.replace("wss", "https"), 
                '--api-key', livekit_api_key, 
                '--api-secret', livekit_api_secret,
                '--json'
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logging.error(f"Error getting participants for room {room_name}: {result.stderr}")
            return []
        
        # Parse the JSON output
        try:
            participants = json.loads(result.stdout)
            return participants
        except json.JSONDecodeError:
            logging.error(f"Failed to parse participant list output: {result.stdout}")
            return []
            
    except Exception as e:
        logging.error(f"Error getting room participants: {str(e)}")
        return []

def end_call(room_name, livekit_url, livekit_api_key, livekit_api_secret):
    """End a call by deleting the room"""
    try:
        # Use lk CLI to delete the room
        result = subprocess.run(
            [
                'lk', 'room', 'delete', 
                '--room', room_name,
                '--url', livekit_url.replace("wss", "https"), 
                '--api-key', livekit_api_key, 
                '--api-secret', livekit_api_secret
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logging.error(f"Error ending call in room {room_name}: {result.stderr}")
            return False
        
        logging.info(f"Successfully ended call in room {room_name}")
        return True
            
    except Exception as e:
        logging.error(f"Error ending call: {str(e)}")
        return False

def list_active_calls(livekit_url, livekit_api_key, livekit_api_secret):
    """List all active calls"""
    logger = logging.getLogger("call_manager")
    rooms = get_active_rooms(livekit_url, livekit_api_key, livekit_api_secret)
    
    if not rooms:
        logger.info("No active calls found")
        return
    
    logger.info(f"Found {len(rooms)} active calls:")
    for i, room in enumerate(rooms):
        room_name = room.get('name')
        created_at = room.get('created_at')
        
        # Get participants
        participants = get_room_participants(room_name, livekit_url, livekit_api_key, livekit_api_secret)
        participant_count = len(participants)
        
        # Format created time
        try:
            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            time_str = created_time.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            time_str = "Unknown"
        
        logger.info(f"{i+1}. Room: {room_name}")
        logger.info(f"   Created: {time_str}")
        logger.info(f"   Participants: {participant_count}")
        
        # Show participant details
        for p in participants:
            identity = p.get('identity', 'Unknown')
            joined_at = p.get('joined_at', 'Unknown')
            
            # Format joined time
            try:
                joined_time = datetime.fromisoformat(joined_at.replace('Z', '+00:00'))
                joined_str = joined_time.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, AttributeError):
                joined_str = "Unknown"
                
            logger.info(f"   - {identity} (joined: {joined_str})")
        
        logger.info("---")

def main():
    """Main entry point for the call management script"""
    load_dotenv()
    logger = setup_logging()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Manage LiveKit voice agent calls')
    parser.add_argument('action', choices=['list', 'end'], help='Action to perform (list or end calls)')
    parser.add_argument('--room', help='Room name for the "end" action')
    
    args = parser.parse_args()
    
    # Get LiveKit credentials from environment
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not all([livekit_url, livekit_api_key, livekit_api_secret]):
        logger.error("Missing LiveKit credentials in environment variables")
        sys.exit(1)
        
    # Execute the requested action
    if args.action == 'list':
        list_active_calls(livekit_url, livekit_api_key, livekit_api_secret)
    elif args.action == 'end':
        if not args.room:
            logger.error("Room name is required for 'end' action")
            sys.exit(1)
        
        success = end_call(args.room, livekit_url, livekit_api_key, livekit_api_secret)
        if success:
            logger.info(f"Successfully ended call in room {args.room}")
        else:
            logger.error(f"Failed to end call in room {args.room}")
            sys.exit(1)

if __name__ == "__main__":
    main()
