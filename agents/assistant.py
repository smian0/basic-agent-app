from textwrap import dedent
from typing import Optional
import os

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.storage.agent.postgres import PostgresAgentStorage
from ollama import AsyncClient as OllamaAsyncClient

from db.session import db_url


def get_assistant(
    model_id: Optional[str] = None,  # Not used - always uses gpt-oss:120b
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    additional_context = ""
    if user_id:
        additional_context += "<context>"
        additional_context += f"You are interacting with the user: {user_id}"
        additional_context += "</context>"

    # Get Ollama API key from environment
    api_key = os.getenv("OLLAMA_TURBO_API_KEY")
    if not api_key:
        raise ValueError("OLLAMA_TURBO_API_KEY environment variable not set")

    return Agent(
        name="Assistant",
        agent_id="assistant",
        user_id=user_id,
        session_id=session_id,
        model=Ollama(
            id="gpt-oss:120b",
            async_client=OllamaAsyncClient(
                host="https://ollama.com",
                headers={'Authorization': f'Bearer {api_key}'}
            ),
            timeout=900,
        ),
        # No tools for this simple agent
        tools=[],
        # Storage for the agent
        storage=PostgresAgentStorage(table_name="assistant_sessions", db_url=db_url),
        # Description of the agent
        description=dedent("""\
            You are Assistant, a helpful AI that provides clear, accurate, and thoughtful responses.
            You excel at understanding context, answering questions, and engaging in meaningful conversations.
            """),
        # Instructions for the agent
        instructions=dedent("""\
            Provide helpful, accurate, and contextual responses to user queries.
            Be concise yet comprehensive, and maintain a friendly and professional tone.
            When appropriate, ask clarifying questions to better understand the user's needs.
            """),
        additional_context=additional_context,
        # Format responses using markdown
        markdown=True,
        # Add the current date and time to the instructions
        add_datetime_to_instructions=True,
        # Send the last 3 messages from the chat history
        add_history_to_messages=True,
        num_history_responses=3,
        # Show debug logs
        debug_mode=debug_mode,
        # Enable monitoring to track sessions in Agno Playground
        monitoring=True,
    )