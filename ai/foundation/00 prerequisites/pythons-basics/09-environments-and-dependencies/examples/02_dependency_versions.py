from importlib.metadata import version


distributions = ["pydantic", "pydantic-ai", "httpx"]

for distribution in distributions:
    print(f"{distribution}: {version(distribution)}")
