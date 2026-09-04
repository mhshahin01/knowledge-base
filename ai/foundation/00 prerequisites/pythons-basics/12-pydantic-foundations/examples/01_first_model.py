from pydantic import BaseModel


class LearnerProgress(BaseModel):
    name: str
    lessons: int


incoming_data = {"name": "Maya", "lessons": "8"}
progress = LearnerProgress.model_validate(incoming_data)

print(f"{progress.name} completed {progress.lessons} lessons.")
print(f"lessons type: {type(progress.lessons).__name__}")

