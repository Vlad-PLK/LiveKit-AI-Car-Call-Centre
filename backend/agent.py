from __future__ import annotations
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from dotenv import load_dotenv
from api import AssistantFnc
from prompts import WELCOME_MESSAGE, INSTRUCTIONS, LOOKUP_BOOKING_MESSAGE
import os

load_dotenv()

async def entrypoint(ctx: JobContext):
    # add the e2ee to connect function 
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()
    
    model = openai.realtime.RealtimeModel(
        instructions=INSTRUCTIONS,
        voice="ballad",
        temperature=0.8,
        modalities=["audio", "text"]
    )
    assistant_fnc = AssistantFnc()
    assistant = MultimodalAgent(model=model, fnc_ctx=assistant_fnc)
    assistant.start(ctx.room)
    
    session = model.sessions[0]
    session.conversation.item.create(
        llm.ChatMessage(
            role="assistant",
            content=WELCOME_MESSAGE
        )
    )
    session.response.create()
    
    @session.on("user_speech_committed")
    def on_user_speech_committed(msg: llm.ChatMessage):
        # If the content is a list, normalize it by joining items
        debug_mode = False
        if isinstance(msg.content, list):
            msg.content = "\n".join("[image]" if isinstance(x, llm.ChatImage) else x for x in msg)

        # Convert the content to a lower-case, stripped string for command checks
        user_input = msg.content.strip().lower()

        # Toggle debug mode commands:
        if user_input == "debug mode":
            debug_mode = True
            session.conversation.item.create(
                llm.ChatMessage(
                    role="system",
                    content="Debug mode activated: responses will now be simplified."
                )
            )
            session.response.create()
            return
        elif user_input == "normal mode":
            debug_mode = False
            session.conversation.item.create(
                llm.ChatMessage(
                    role="system",
                    content="Normal mode activated: full responses will be provided."
                )
            )
            session.response.create()
            return

        # Route the query based on the debug flag and booking status
        if debug_mode == True:
            debug_handle_query(msg)
        else:
            if assistant_fnc.has_booking():
                handle_query(msg)
            else:
                find_profile(msg)


    def debug_handle_query(msg: llm.ChatMessage):
        # In debug mode, use a minimal prompt to conserve API tokens.
        debug_prompt = (
            "You are in debug mode. Provide only the crucial information "
            "in a concise format. For example, for room prices reply as: "
            "Type1: Price1, Type2: Price2."
        )
        # Combine the debug prompt with the user's query
        combined_content = f"{debug_prompt}\nUser Query: {msg.content}"

        # Create a new conversation item for the simplified query
        session.conversation.item.create(
            llm.ChatMessage(
                role="user",
                content=combined_content
            )
        )
        session.response.create()


    def find_profile(msg: llm.ChatMessage):
        session.conversation.item.create(
            llm.ChatMessage(
                role="system",
                content=LOOKUP_BOOKING_MESSAGE(msg)
            )
        )
        session.response.create()


    def handle_query(msg: llm.ChatMessage):
        session.conversation.item.create(
            llm.ChatMessage(
                role="user",
                content=msg.content
            )
        )
        session.response.create()
 
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))