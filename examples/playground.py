from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

# Load environment variables from .env file
load_dotenv()

agent_storage: str = "tmp/agents.db"

web_agent = Agent(
    name="Web Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions=["Always include sources"],
    # Store the agent sessions in a sqlite database
    storage=SqliteStorage(table_name="web_agent", db_file=agent_storage),
    # Adds the current date and time to the instructions
    add_datetime_to_instructions=True,
    # Adds the history of the conversation to the messages
    add_history_to_messages=True,
    # Number of history responses to add to the messages
    num_history_responses=5,
    # Adds markdown formatting to the messages
    markdown=True,
    # Enable monitoring to track sessions
    monitoring=True,
    # Enable debug mode for detailed logs
    debug_mode=False,
)

finance_agent = Agent(
    name="Finance Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)],
    instructions=["Always use tables to display data"],
    storage=SqliteStorage(table_name="finance_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    # Enable monitoring to track sessions
    monitoring=True,
    # Enable debug mode for detailed logs
    debug_mode=False,
)

playground_app = Playground(agents=[web_agent, finance_agent])
app = playground_app.get_app()

if __name__ == "__main__":
    # Print available routes for debugging
    print("\nAvailable endpoints:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.path}")
    
    playground_app.serve("playground:app", reload=True)