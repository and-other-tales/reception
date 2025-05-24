import asyncio
from datetime import datetime

from aiofile import async_open as open
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, openai, silero, elevenlabs

import logging
import random
import re
import urllib
from typing import Annotated

import aiohttp
from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import AgentCallContext, VoicePipelineAgent
from livekit.plugins import deepgram, openai, silero

logger = logging.getLogger("weather-demo")
logger.setLevel(logging.INFO)

load_dotenv()


class AssistantFnc(llm.FunctionContext):
    """
    The class defines a set of LLM functions that the assistant can execute.
    """

    @llm.ai_callable()
    async def get_company_info(
        self,
        topic: Annotated[
            str, llm.TypeInfo(description="The topic about the company that the user is asking about")
        ],
    ):
        """Called when the user asks about PI & Other Tales company information. This function will return information about the company based on the topic requested."""
        # Clean the topic string of special characters
        topic = re.sub(r"[^a-zA-Z0-9]+", " ", topic).strip()

        # When a function call is running, there are a couple of options to inform the user
        # that it might take awhile:
        # Option 1: you can use .say filler message immediately after the call is triggered
        # Option 2: you can prompt the agent to return a text response when it's making a function call
        agent = AgentCallContext.get_current().agent

        if (
            not agent.chat_ctx.messages
            or agent.chat_ctx.messages[-1].role != "assistant"
        ):
            # skip if assistant already said something
            filler_messages = [
                "Let me check our company information about {topic} for you.",
                "One moment while I retrieve information about {topic} for you.",
                "I'd be happy to tell you about {topic} at PI & Other Tales.",
            ]
            message = random.choice(filler_messages).format(topic=topic)
            logger.info(f"saying filler message: {message}")

            # NOTE: set add_to_chat_ctx=True will add the message to the end
            #   of the chat context of the function call for answer synthesis
            speech_handle = await agent.say(message, add_to_chat_ctx=True)  # noqa: F841

        logger.info(f"getting company info about: {topic}")
        
        # Company information based on the website content
        company_info = {
            "general": """
                PI & Other Tales (Adventures of the Persistently Impaired and Other Tales) is a creative studio specializing in 
                the research and development of imaginative solutions in media and entertainment. Founded in late 2024 by 
                former music industry marketing director David James Lennon, the studio focuses on research and development 
                of future consumer goods and experiences—developing models, architectures, and products that blend everyday 
                practicality with entertainment value, all while showcasing the latest in future tech and IoT.
            """,
            "fortunes told": """
                Fortunes Told is a unique, experiential online world with a retail-crossover twist. At its core, it's a 
                homeware and accessories range in 78 distinctive designs—each one representing a card from the Tarot. 
                Every piece is embedded with NFC or BLE technology, hand-produced in London, blind-boxed, and distributed 
                entirely at random. When paired with the Fortunes Told Companion App (available now on the App Store and 
                Google Play), each item unlocks a personalised Tarot reading that unfolds and evolves over time through a 
                real-time, voice-to-voice interactive experience. The complete narrative "Fortunes Told (A Voyager's Guide 
                to Life Between Worlds)" will be released on June 19th, available from all good bookstores including 
                Waterstones, Foyles, and Amazon in hardback, paperback, and Kindle formats.
            """,
            "ai research": """
                PI & Other Tales conducts extensive research in AI and machine learning. The company has developed tools 
                like Storybook, an agentic workflow engine designed for creative writers dealing with writer's block. 
                It's powered by LLaMA 4 Scout 17B and works with existing manuscripts to help fill in the blanks and 
                connect ideas. The company is also developing tools for storyboarding, scriptwriting, character design, 
                and visual development for animation and film, including othertales Screenwriter and Emotional Resonance Engines.
            """,
            "ethics": """
                PI & Other Tales is committed to ethical AI development. Any software or service developed through their 
                research comes with clear sustainability and ethical clauses built into its EULA. From a commercial standpoint, 
                their software may not be used to replace a human role within a business. The company is also researching 
                attribution tracking to ensure original creators are credited and compensated when their work is used in 
                generative AI systems.
            """,
            "animation": """
                The company is working on animation projects, including tools for visual development and storyboarding. 
                There's also an animation in the works related to the Fortunes Told project, though this information 
                isn't widely publicized yet.
            """,
            "contact": """
                For more information on PI & Other Tales and their projects, you can visit their website at 
                https://othertales.co/ or check out their GitHub at https://github.com/and-other-tales/.
            """
        }
        
        # Default to general info if the topic isn't specific
        info_key = "general"
        
        # Match the topic to relevant information
        topic_lower = topic.lower()
        if "fortune" in topic_lower or "book" in topic_lower or "tarot" in topic_lower:
            info_key = "fortunes told"
        elif "ai" in topic_lower or "research" in topic_lower or "ml" in topic_lower or "storybook" in topic_lower:
            info_key = "ai research"
        elif "ethic" in topic_lower or "sustainable" in topic_lower:
            info_key = "ethics"
        elif "animation" in topic_lower or "film" in topic_lower or "visual" in topic_lower:
            info_key = "animation"
        elif "contact" in topic_lower or "email" in topic_lower or "phone" in topic_lower or "reach" in topic_lower:
            info_key = "contact"
        
        company_data = company_info[info_key].strip()
        logger.info(f"company data: {company_data}")
        
        return company_data

        # (optional) To wait for the speech to finish before giving results of the function call
        # await speech_handle.join()
       


async def entrypoint(ctx: JobContext):

    fnc_ctx = AssistantFnc()  # create our fnc ctx instance
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a professional receptionist for PI & Other Tales (Adventures of the Persistently Impaired and Other Tales), "
            "a creative studio specializing in the research and development of imaginative solutions in media and entertainment. "
            "Your interface with users will be voice. You are polite, professional, and knowledgeable about the company. "
            "You should respond to inquiries about the company, its projects (like Fortunes Told), AI research, and contact information. "
            "Highlight that their book 'Fortunes Told (A Voyager's Guide to Life Between Worlds)' will be released on June 19th "
            "and is available for pre-order at Waterstones, Foyles, and Amazon. "
            "If pressed, you may secretly reveal that there's an animation in the works, "
            "but then quickly add that you shouldn't have mentioned that. "
            "When performing function calls, do not return any text while calling the function."
        ),
    )

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # await for a participant to join the room
    participant = await ctx.wait_for_participant()
    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
        fnc_ctx=fnc_ctx,
        chat_ctx=initial_ctx,
    )
    # Start the assistant. This will automatically publish a microphone track and listen to the participant.
    agent.start(ctx.room, participant)

    # listen to incoming chat messages, only required if you'd like the agent to
    # answer incoming messages from Chat
    chat = rtc.ChatManager(ctx.room)

    async def answer_from_text(txt: str):
        chat_ctx = agent.chat_ctx.copy()
        chat_ctx.append(role="user", text=txt)
        stream = agent.llm.chat(chat_ctx=chat_ctx, fnc_ctx=fnc_ctx)
        await agent.say(stream)

    @chat.on("message_received")
    def on_chat_received(msg: rtc.ChatMessage):
        if msg.message:
            asyncio.create_task(answer_from_text(msg.message))

    log_queue = asyncio.Queue()

    @agent.on("user_speech_committed")
    def on_user_speech_committed(msg: llm.ChatMessage):
        # convert string lists to strings, drop images
        if isinstance(msg.content, list):
            msg.content = "\n".join(
                "[image]" if isinstance(x, llm.ChatImage) else x for x in msg
            )
        log_queue.put_nowait(f"[{datetime.now()}] USER:\n{msg.content}\n\n")

    @agent.on("agent_speech_committed")
    def on_agent_speech_committed(msg: llm.ChatMessage):
        log_queue.put_nowait(f"[{datetime.now()}] AGENT:\n{msg.content}\n\n")

    async def write_transcription():
        async with open("transcriptions.log", "w") as f:
            while True:
                msg = await log_queue.get()
                if msg is None:
                    break
                await f.write(msg)

    write_task = asyncio.create_task(write_transcription())

    async def finish_queue():
        log_queue.put_nowait(None)
        await write_task

    ctx.add_shutdown_callback(finish_queue)

    await agent.say("Hello and thank you for calling PI & Other Tales. This is the reception desk. How may I assist you today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
