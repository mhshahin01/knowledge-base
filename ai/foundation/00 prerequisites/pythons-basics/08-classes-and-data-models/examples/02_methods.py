class ModelInfo:
    def __init__(self, name: str, available: bool) -> None:
        self.name = name
        self.available = available

    def describe(self) -> str:
        if self.available:
            status = "available"
        else:
            status = "unavailable"

        return f"{self.name} is {status}."


first_model = ModelInfo("small-model", True)
second_model = ModelInfo("large-model", False)

print(first_model.describe())
print(second_model.describe())

