from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel


class LessonPlan(BaseModel):
    title: str
    minutes: int = Field(gt=0)
    topics: list[str]


test_model = TestModel(
    custom_output_args={
        "title": "Functions",
        "minutes": 20,
        "topics": ["parameters", "return values"],
    }
)
agent = Agent(test_model, output_type=LessonPlan)

result = agent.run_sync("Create a short lesson about functions.")
plan = result.output

print(f"Plan type: {type(plan).__name__}")
print(f"Title: {plan.title}")
print(f"Minutes: {plan.minutes}")
print(f"Topics: {', '.join(plan.topics)}")

