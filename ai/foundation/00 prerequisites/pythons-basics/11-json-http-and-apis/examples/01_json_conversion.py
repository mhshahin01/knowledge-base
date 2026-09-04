import json


progress = {"topic": "Python", "completed": True}

json_text = json.dumps(progress)
loaded_progress = json.loads(json_text)

print(f"JSON: {json_text}")
print(f"Python type: {type(loaded_progress).__name__}")
print(f"Topic: {loaded_progress['topic']}")

