import os

from pydantic_ai import Agent


model_name = os.getenv("PYDANTIC_AI_MODEL")

if model_name is None:
    print("Set PYDANTIC_AI_MODEL before running a real model.")
else:
    agent = Agent(
        model_name,
        instructions="Teach Python clearly and briefly.",
    )
    result = agent.run_sync("Explain a Python function in one sentence.")
    print(result.output)
