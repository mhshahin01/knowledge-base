class Learner:
    def __init__(self, name: str, topic: str) -> None:
        self.name = name
        self.topic = topic


first_learner = Learner("Maya", "functions")
second_learner = Learner("Sam", "classes")

print(f"{first_learner.name} is learning {first_learner.topic}.")
print(f"{second_learner.name} is learning {second_learner.topic}.")

