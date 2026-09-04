from pydantic import BaseModel, ValidationError


class ModelSettings(BaseModel):
    temperature: float


try:
    ModelSettings.model_validate({"temperature": "hot"})
except ValidationError as error:
    first_error = error.errors()[0]
    field = ".".join(str(part) for part in first_error["loc"])

    print(f"Field: {field}")
    print(f"Error type: {first_error['type']}")

