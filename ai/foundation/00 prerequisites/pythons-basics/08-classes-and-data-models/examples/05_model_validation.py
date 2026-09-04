from dataclasses import dataclass


@dataclass
class ModelSettings:
    temperature: float
    max_tokens: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 1.0:
            raise ValueError("temperature must be between 0.0 and 1.0")

        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero")


valid_settings = ModelSettings(temperature=0.2, max_tokens=200)
print(f"Valid temperature: {valid_settings.temperature}")

try:
    ModelSettings(temperature=1.4, max_tokens=200)
except ValueError as error:
    print(f"Invalid settings: {error}")
