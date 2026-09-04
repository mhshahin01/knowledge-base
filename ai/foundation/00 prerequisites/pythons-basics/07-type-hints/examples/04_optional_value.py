def find_model(requested: str, available: list[str]) -> str | None:
    for model in available:
        if model == requested:
            return model

    return None


models: list[str] = ["small-model", "medium-model"]

found_model = find_model("medium-model", models)
missing_model = find_model("large-model", models)

print(f"Found: {found_model}")
print(f"Missing model: {missing_model}")

