import asyncio

from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel


test_model = TestModel(
    custom_output_text="Async agents can wait without blocking other async work."
)
agent = Agent(test_model, instructions="Explain async Python simply.")


async def main() -> None:
    result = await agent.run("Why use an async agent?")
    print(result.output)


asyncio.run(main())

