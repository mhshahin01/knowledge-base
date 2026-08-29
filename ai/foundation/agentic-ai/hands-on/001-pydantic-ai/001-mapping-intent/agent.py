"""agent.py - the ONE brain that the web playground will reuse.

Uses a real LLM if OPENAI_API_KEY is set; otherwise falls back to Pydantic AI's
built-in TestModel so you can learn the mechanics with zero cost and no API key.
"""
import os

from dotenv import load_dotenv  
load_dotenv() #.evn has the API key for the model 
from pydantic_ai import Agent

if os.getenv("OPENAI_API_KEY"):
    MODEL = "openai:gpt-5"        # any real model string works: 'anthropic:claude-sonnet-4-6', ...
    print("Using real model")
else:
    from pydantic_ai.models.test import TestModel
    MODEL = TestModel()           # free fake model for learning/testing


agent = Agent(
    MODEL,
    system_prompt="You are a friendly study-buddy agent for beginners. Keep answers short and encouraging. if you got an intent that does not match the existing ones, tell the requestor swiftly that you can't do that & list what you can",
)

# --- Tools configuration: plain Python functions the agent is allowed to call ---
@agent.tool_plain
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@agent.tool_plain
def word_count(text: str) -> int:
    """Count how many words are in a text."""
    return len(text.split())
