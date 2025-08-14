from enum import Enum
from typing import List, Optional

from agents.sage import get_sage
from agents.scholar import get_scholar
from agents.assistant import get_assistant


class AgentType(Enum):
    SAGE = "sage"  # Kimi-k2 Free with tools
    SCHOLAR = "scholar"  # Kimi-k2 Free with tools
    ASSISTANT = "assistant"  # GPT-OSS:120B without tools


def get_available_agents() -> List[str]:
    """Returns a list of all available agent IDs."""
    return [agent.value for agent in AgentType]


def get_agent(
    model_id: str = "moonshotai/kimi-k2:free",  # Default to Kimi-k2 Free
    agent_id: Optional[AgentType] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
):
    if agent_id == AgentType.SAGE:
        # Sage uses Kimi-k2 Free with tools
        return get_sage(model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode)
    elif agent_id == AgentType.ASSISTANT:
        # Assistant uses GPT-OSS:120B without tools
        return get_assistant(model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode)
    else:
        # Default to Scholar (Kimi-k2 Free with tools)
        return get_scholar(model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode)
