from pydantic import BaseModel, ConfigDict, Field


class ModelSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(min_length=1)
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(gt=0)


settings = ModelSettings(
    model="example-model",
    temperature=0.2,
    max_tokens=200,
)

print(settings)

