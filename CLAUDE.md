# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Agno-based agent application that provides a production-grade agentic system with:
- Multiple AI agents (Sage, Scholar) with specialized capabilities
- Teams of agents for collaborative tasks (Finance Research, Multi-Language)
- Workflows for complex content generation (Blog Post Generator, Investment Report Generator)
- FastAPI backend for API endpoints
- Streamlit frontend for user interaction
- PostgreSQL with pgvector for knowledge storage

## Development Commands

### Environment Setup
```bash
# Install dependencies (first time setup)
./scripts/dev_setup.sh

# Activate virtual environment
source .venv/bin/activate
```

### Running the Application
```bash
# Start all services (Streamlit on :8501, FastAPI on :8000, Postgres on :5432)
ag ws up

# Stop all services
ag ws down
```

### Code Quality
```bash
# Format code using ruff
./scripts/format.sh

# Validate code (ruff linting + mypy type checking)
./scripts/validate.sh

# Run tests
./scripts/test.sh
# Run specific test
pytest path/to/test_file.py::test_function_name
```

## Architecture

### Core Components

**Agents** (`agents/`):
- `sage.py`: Knowledge agent with web search and knowledge base capabilities
- `scholar.py`: Academic research agent
- `operator.py`: Agent orchestration and routing
- All agents use PostgresAgentStorage for session persistence

**Teams** (`teams/`):
- `finance_researcher.py`: Financial analysis team
- `multi_language.py`: Multi-language content team
- Teams coordinate multiple agents for complex tasks

**Workflows** (`workflows/`):
- `blog_post_generator.py`: Multi-agent workflow for researching and writing blog posts
- `investment_report_generator.py`: Financial report generation workflow
- Workflows orchestrate agents with caching and state management

**API** (`api/`):
- FastAPI application with versioned routes (`/v1`)
- Endpoints for agents, teams, and playground functionality
- CORS middleware configured for cross-origin requests

**UI** (`ui/`):
- Streamlit application with multiple pages for different agents/teams
- Session management and streaming response handling
- Custom CSS styling in `css.py`

**Database** (`db/`):
- PostgreSQL with pgvector extension for vector storage
- Alembic migrations for schema management
- SQLAlchemy models and session management

### Key Patterns

**Agent Creation**:
- All agents use `agno.agent.Agent` base class
- Configure with model (OpenAI), tools, storage, and knowledge base
- Support streaming responses and session persistence

**Tool Integration**:
- DuckDuckGo for web search
- Newspaper4k for article scraping
- Exa for advanced search
- YFinance for financial data

**State Management**:
- PostgresStorage for workflow state persistence
- Session-based caching for search results and scraped content
- Knowledge base with hybrid search (vector + keyword)

**Response Streaming**:
- Agents support streaming via `stream=True` parameter
- UI handles streaming with `RunEvent` types
- Proper cleanup and error handling for interrupted streams

## Environment Variables

Required:
- `OPENAI_API_KEY`: OpenAI API key for model access

Optional:
- `EXA_API_KEY`: Exa search API key
- `AGNO_API_KEY`: Agno monitoring API key
- `AGNO_MONITOR`: Enable monitoring (set to "True")

## Database

The application uses PostgreSQL with pgvector extension:
- Automatic migrations on startup when `MIGRATE_DB=True`
- Vector storage for knowledge base with hybrid search
- Session storage for agent conversations
- Workflow state persistence

## Docker Development

The workspace uses Docker Compose for local development:
- `workspace/dev_resources.py`: Defines development containers
- `workspace/prd_resources.py`: Production ECS configuration
- Automatic database initialization and migration
- Volume mounting for hot-reload during development

## Testing

Tests should be placed in `tests/` directory and follow pytest conventions:
- Use fixtures for common setup
- Mock external API calls
- Test agents, teams, and workflows independently
- Validate streaming responses and state management