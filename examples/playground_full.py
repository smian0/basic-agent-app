from dotenv import load_dotenv
from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.tools.newspaper4k import Newspaper4kTools

# Load environment variables from .env file
load_dotenv()

# Storage configuration
agent_storage: str = "tmp/agents.db"

# Sage Agent - Knowledge Agent with web search
sage_agent = Agent(
    name="Sage",
    agent_id="sage",
    model=OpenAIChat(id="gpt-4o-mini", temperature=0.7),
    tools=[DuckDuckGoTools()],
    storage=SqliteStorage(table_name="sage_sessions", db_file=agent_storage),
    description=dedent("""\
        You are Sage, an advanced Knowledge Agent designed to deliver accurate, context-rich, engaging responses.
        You have access to a knowledge base full of user-provided information and the capability to search the web if needed.
    """),
    instructions=[
        "Always provide accurate, context-rich responses",
        "Use your knowledge base when available",
        "Search the web for current information when needed",
        "Engage with thoughtful analysis and examples"
    ],
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    monitoring=True,
)

# Scholar Agent - Academic Research Agent
scholar_agent = Agent(
    name="Scholar",
    agent_id="scholar",
    model=OpenAIChat(id="gpt-4o-mini", temperature=0.7),
    tools=[DuckDuckGoTools(), Newspaper4kTools()],
    storage=SqliteStorage(table_name="scholar_sessions", db_file=agent_storage),
    description=dedent("""\
        You are Scholar, a cutting-edge Answer Engine built to deliver precise, context-rich, and engaging responses.
        You specialize in academic research and detailed analysis.
    """),
    instructions=[
        "Deliver precise, context-rich responses",
        "Provide detailed analysis with supporting evidence",
        "Include illustrative examples and clarifications",
        "Cite sources when providing information",
        "Engage with follow-up questions"
    ],
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    monitoring=True,
)

# Web Agent - General web search agent
web_agent = Agent(
    name="Web Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions=["Always include sources", "Provide current information"],
    storage=SqliteStorage(table_name="web_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    monitoring=True,
)

# Finance Agent - Financial analysis agent
finance_agent = Agent(
    name="Finance Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            company_info=True,
            company_news=True,
        )
    ],
    instructions=[
        "Always use tables to display financial data",
        "Provide comprehensive financial analysis",
        "Include relevant metrics and ratios",
        "Explain financial terms clearly"
    ],
    storage=SqliteStorage(table_name="finance_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    monitoring=True,
)

# News Agent - News and current events specialist
news_agent = Agent(
    name="News Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools(), Newspaper4kTools()],
    instructions=[
        "Focus on current events and news",
        "Provide balanced perspectives",
        "Include multiple sources",
        "Summarize key points clearly"
    ],
    storage=SqliteStorage(table_name="news_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    monitoring=True,
)

# Create the playground with all agents
playground_app = Playground(
    agents=[sage_agent, scholar_agent, web_agent, finance_agent, news_agent]
)
app = playground_app.get_app()

if __name__ == "__main__":
    # Print available endpoints for debugging
    print("\n" + "="*60)
    print("🚀 Agno Playground - Full Agent Suite")
    print("="*60)
    print("\n📋 Available Agents:")
    for agent in [sage_agent, scholar_agent, web_agent, finance_agent, news_agent]:
        print(f"  • {agent.name}: {agent.agent_id}")
    print("\n🔧 Configuration:")
    print(f"  • Model: gpt-4o-mini")
    print(f"  • Storage: SQLite ({agent_storage})")
    print(f"  • Monitoring: Enabled")
    print("\n🌐 Access Points:")
    print(f"  • Local API: http://localhost:7777/v1")
    print(f"  • Playground: https://app.agno.com/playground?endpoint=localhost:7777/v1")
    print(f"  • API Docs: http://localhost:7777/docs")
    print("\n" + "="*60 + "\n")
    
    playground_app.serve("playground_full:app", reload=True)