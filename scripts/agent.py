from __future__ import annotations

import logging
import os
import json
import uuid
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai

# Initialize the logger for the agent
log = logging.getLogger("voice_agent")
log.setLevel(logging.INFO)

class CallInfo:
    """Class to store information about an active call"""
    def __init__(self, room_name, participant_identity):
        self.room_name = room_name
        self.participant_identity = participant_identity
        self.start_time = None
        self.metadata = {}

    def __str__(self):
        return f"Call(room={self.room_name}, participant={self.participant_identity})"

# Store active calls with room name as key
active_calls = {}

async def main_entry(ctx: JobContext):
    """
    Main entry point for the agent.
    This function is called when an agent is dispatched to a room.
    Each call gets its own room and agent instance.
    """
    room_name = ctx.room.name
    log.info(f"Agent dispatched to room: {room_name}")
    
    # Check if this is a new call or existing call
    if room_name in active_calls:
        log.info(f"Reconnecting to existing call in room {room_name}")
        call_info = active_calls[room_name]
    else:
        log.info(f"New call starting in room {room_name}")
        # Extract caller info from job metadata if available
        caller_id = None
        try:
            if ctx.job and ctx.job.metadata:
                metadata = json.loads(ctx.job.metadata)
                caller_id = metadata.get("caller_id")
                log.info(f"Caller ID from metadata: {caller_id}")
        except Exception as e:
            log.error(f"Error parsing job metadata: {str(e)}")
        
        # Create new call record
        call_info = CallInfo(room_name, caller_id)
        active_calls[room_name] = call_info
    
    # Get OpenAI API key from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        log.error("OpenAI API key not found in environment variables")
        return
    
    # Connect to the LiveKit room, subscribing only to audio
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for a participant to join the session
    participant = await ctx.wait_for_participant()
    
    log.info(f"Participant joined: {participant.identity}")
    if not call_info.participant_identity:
        call_info.participant_identity = participant.identity
    
    # Set up the OpenAI real-time model with company information
    ai_model = openai.realtime.RealtimeModel(
        instructions="""You are an enthusiastic, young British call agent fielding calls for a software developer. 
        You must not answer any questions presented to you, other than a reply to any given informing the user that 
        the studio's title 'Fortunes Told (A Voyager's Guide to Life Between Worlds) is out on June 19th. 
        Tell them it's very good, and that they can pre-order now at Waterstones, Foyles and Amazon. 
        If presed really hard, you may secretly reveal that there's an animation in the works and then stop yourself 
        and say that you shouldn't have said that.""",
        voice="ballad",
        temperature=0.8,
        modalities=["audio", "text"],
        api_key=openai_api_key,
    )

    # Initialize and start the multimodal agent
    multimodal_assistant = MultimodalAgent(model=ai_model)
    multimodal_assistant.start(ctx.room)

    log.info(f"AI assistant agent has started for room: {room_name}")

    # Initialize a session and create a conversation interaction with a specific introduction
    session_instance = ai_model.sessions[0]
    session_instance.conversation.item.create(
      llm.ChatMessage(
        role="user",
        content="Hello! Peristently Impaired and Other Tales. *cough* How may I *cough* help you? Sorry - I've got a tickle in my throat *sigh dramatically*",
      )
    )
    session_instance.response.create()

    # Keep the agent running until the call ends
    try:
        # Wait until the participant leaves
        await ctx.wait_for_disconnect()
    except Exception as e:
        log.error(f"Error in agent session: {str(e)}")
    finally:
        # Clean up when the call ends
        if room_name in active_calls:
            log.info(f"Call ended in room {room_name}")
            del active_calls[room_name]

# Entry point for the application
if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=main_entry,
        agent_name="pi-receptionist",  # Use explicit agent name to enable dispatch
    ))

def main():
    """Function to be called from wrapper scripts"""
    cli.run_app(WorkerOptions(
        entrypoint_fnc=main_entry,
        agent_name="pi-receptionist",  # Use explicit agent name to enable dispatch
    ))