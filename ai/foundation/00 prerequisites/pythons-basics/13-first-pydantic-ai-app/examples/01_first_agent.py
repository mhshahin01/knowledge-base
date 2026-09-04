from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel


test_model = TestModel(
    custom_output_text="A function is a reusable block of code."
)
agent = Agent(
    test_model,
    instructions="Teach Python in one clear sentence.",
)

result = agent.run_sync("What is a function?")
print(result.output)

