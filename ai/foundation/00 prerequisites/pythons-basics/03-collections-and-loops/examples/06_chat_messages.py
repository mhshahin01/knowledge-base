messages = [
    {"role": "system", "content": "Answer clearly."},
    {"role": "user", "content": "What is a Python list?"},
    {"role": "assistant", "content": "A list stores values in order."},
]

for message in messages:
    role = message["role"].upper()
    content = message["content"]
    print(f"{role}: {content}")
