def build_greeting(name: str) -> str:
    return f"Welcome, {name}!"


learner_name: str = "Maya"
greeting: str = build_greeting(learner_name)
print(greeting)

