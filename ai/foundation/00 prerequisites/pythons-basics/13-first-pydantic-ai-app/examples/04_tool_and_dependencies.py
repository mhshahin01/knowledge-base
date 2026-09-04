from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel


@dataclass
class CourseProgress:
    learner: str
    completed_lessons: int


test_model = TestModel(
    custom_output_text="Maya has completed 8 lessons."
)
agent = Agent(test_model, deps_type=CourseProgress)


@agent.tool
def get_completed_lessons(ctx: RunContext[CourseProgress]) -> int:
    """Return the learner's number of completed lessons."""
    progress = ctx.deps
    print(
        f"Tool read: {progress.learner} completed "
        f"{progress.completed_lessons} lessons."
    )
    return progress.completed_lessons


course_progress = CourseProgress(learner="Maya", completed_lessons=8)
result = agent.run_sync(
    "How many lessons has Maya completed?",
    deps=course_progress,
)

print(result.output)

