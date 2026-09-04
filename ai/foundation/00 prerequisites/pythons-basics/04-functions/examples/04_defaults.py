def build_instruction(topic, tone="clear"):
    return f"Explain {topic}. Use a {tone} tone."


first_instruction = build_instruction("Python lists")
second_instruction = build_instruction("Python functions", tone="concise")

print(first_instruction)
print(second_instruction)

