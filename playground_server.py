#!/usr/bin/env python3
"""
Standalone Agno Playground server for connecting to the hosted playground.
Run this script to make your agents available at http://app.agno.com/playground
"""

from agno.playground import Playground, serve_playground_app

# Import your agents and teams
from agents.sage import get_sage
from agents.scholar import get_scholar
from teams.finance_researcher import get_finance_researcher_team
from teams.multi_language import get_multi_language_team

# Initialize agents and teams
sage_agent = get_sage(debug_mode=True)
scholar_agent = get_scholar(debug_mode=True)
finance_researcher_team = get_finance_researcher_team(debug_mode=True)
multi_language_team = get_multi_language_team(debug_mode=True)

# Create playground instance
playground = Playground(
    agents=[sage_agent, scholar_agent],
    teams=[finance_researcher_team, multi_language_team],
    name="Agent App Playground",
    description="Production-grade agentic system with Sage, Scholar, and Teams",
    app_id="agent-app-playground"
)

# Get the FastAPI app
app = playground.get_app()

if __name__ == "__main__":
    # This will start a server on port 7777 by default
    # The hosted playground at http://app.agno.com/playground will connect to this
    print("Starting Agno Playground server on http://localhost:7777")
    print("Connect from http://app.agno.com/playground using 'localhost:7777' as the endpoint")
    playground.serve(app="playground_server:app", reload=True, port=7777)