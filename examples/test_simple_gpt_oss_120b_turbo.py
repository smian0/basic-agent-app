#!/usr/bin/env python3
"""Test Ollama Turbo 120b Model"""

import asyncio
import os
from agno.agent import Agent
from agno.models.ollama import Ollama
from ollama import AsyncClient as OllamaAsyncClient


async def test_120b():
    """Test 120b model with complex analysis."""
    api_key = os.getenv("OLLAMA_TURBO_API_KEY")
    if not api_key:
        raise ValueError("OLLAMA_TURBO_API_KEY environment variable not set")
    
    agent = Agent(
        model=Ollama(
            # id="qwen3:30b",
            # async_client=OllamaAsyncClient(
            #     host="https://mb-metadata-doctors-helen.trycloudflare.com",
            #     headers={'Authorization': f'Bearer sk-ollama-C6TpKZAXQchte4rWbaPt5JWuWfh8jdDq5zdofDeDs2Q'}
            # ),
            id="gpt-oss:120b",
            async_client=OllamaAsyncClient(
                host="https://ollama.com",
                headers={'Authorization': f'Bearer {api_key}'}
            ),
            timeout=900,
            
        ),
        show_tool_calls=True,
        debug_mode=True,
    )
    
    await agent.aprint_response("""Analyze this fictional stock scenario:

Stock: ACME Corp (fictional)
Current Price: $150
52-week Range: $120-$180
P/E Ratio: 22
Revenue Growth: 15% YoY
Recent News: New product launch, expanding to Asia markets
Industry: Technology Software

Provide: 1) Technical outlook, 2) Fundamental analysis, 3) Risk factors, 4) Recommendation with target price.""", 
    markdown=True,stream=False)


if __name__ == "__main__":
    asyncio.run(test_120b())