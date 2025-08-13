from os import getenv

from agno.playground import Playground

from agents.sage import get_sage
from agents.scholar import get_scholar
from teams.finance_researcher import get_finance_researcher_team
from teams.multi_language import get_multi_language_team
from workflows.blog_post_generator import get_blog_post_generator
from workflows.investment_report_generator import get_investment_report_generator
from workspace.dev_resources import dev_fastapi

######################################################
## Router for the Playground Interface
######################################################

sage_agent = get_sage(debug_mode=True)
scholar_agent = get_scholar(debug_mode=True)
finance_researcher_team = get_finance_researcher_team(debug_mode=True)
multi_language_team = get_multi_language_team(debug_mode=True)
blog_post_workflow = get_blog_post_generator(debug_mode=True)
investment_report_workflow = get_investment_report_generator(debug_mode=True)

# Create a playground instance
playground = Playground(
    agents=[sage_agent, scholar_agent], 
    teams=[finance_researcher_team, multi_language_team],
    workflows=[blog_post_workflow, investment_report_workflow]
)

# Register the endpoint with Agno Playground
# This allows the hosted playground at http://app.agno.com/playground to connect
# Note: We use get_async_router() instead of serve() since we're integrating with FastAPI
if getenv("RUNTIME_ENV") == "dev":
    # For local development, the playground will be accessible at http://localhost:8000
    # Connect from http://app.agno.com/playground using this URL
    playground_endpoint = f"http://localhost:{dev_fastapi.port_number}"
    # Note: playground.serve() would start its own server, so we use the router instead
    
playground_router = playground.get_async_router()
