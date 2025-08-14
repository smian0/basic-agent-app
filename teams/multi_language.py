from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.openrouter import OpenRouter
from agno.storage.postgres import PostgresStorage
from agno.team.team import Team

from db.session import db_url
from teams.settings import team_settings

japanese_agent = Agent(
    name="Japanese Agent",
    agent_id="japanese-agent",
    role="You only answer in Japanese",
    model=OpenRouter(
        id="moonshotai/kimi-k2:free",
    ),
    monitoring=True,
)
chinese_agent = Agent(
    name="Chinese Agent",
    agent_id="chinese-agent",
    role="You only answer in Chinese",
    model=OpenRouter(
        id="moonshotai/kimi-k2:free",
    ),
    monitoring=True,
)
spanish_agent = Agent(
    name="Spanish Agent",
    agent_id="spanish-agent",
    role="You only answer in Spanish",
    model=OpenRouter(
        id="moonshotai/kimi-k2:free",
    ),
    monitoring=True,
)
french_agent = Agent(
    name="French Agent",
    agent_id="french-agent",
    role="You only answer in French",
    model=OpenRouter(
        id="moonshotai/kimi-k2:free",
    ),
    monitoring=True,
)
german_agent = Agent(
    name="German Agent",
    agent_id="german-agent",
    role="You only answer in German",
    model=OpenRouter(
        id="moonshotai/kimi-k2:free",
    ),
    monitoring=True,
)


def get_multi_language_team(
    model_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Team:
    # Default to Kimi-k2 Free model
    model_id = model_id or "moonshotai/kimi-k2:free"

    return Team(
        name="Multi Language Team",
        mode="route",
        team_id="multi-language-team",
        model=OpenRouter(
            id=model_id,
        ),
        members=[
            spanish_agent,
            japanese_agent,
            french_agent,
            german_agent,
            chinese_agent,
        ],
        description="You are a language router that directs questions to the appropriate language agent.",
        instructions=[
            "Identify the language of the user's question and direct it to the appropriate language agent.",
            "Let the language agent answer the question in the language of the user's question.",
            "The the user asks a question in English, respond directly in English with:",
            "If the user asks in a language that is not English or your don't have a member agent for that language, respond in English with:",
            "'I only answer in the following languages: English, Spanish, Japanese, Chinese, French and German. Please ask your question in one of these languages.'",
            "Always check the language of the user's input before routing to an agent.",
            "For unsupported languages like Italian, respond in English with the above message.",
        ],
        session_id=session_id,
        user_id=user_id,
        markdown=True,
        show_tool_calls=True,
        show_members_responses=True,
        storage=PostgresStorage(
            table_name="multi_language_team",
            db_url=db_url,
            mode="team",
            auto_upgrade_schema=True,
        ),
        debug_mode=debug_mode,
        monitoring=True,
    )
