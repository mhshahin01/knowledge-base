from dataclasses import dataclass


@dataclass
class ChatMessage:
    role: str
    content: str


message = ChatMessage(role="user", content="Explain dataclasses.")

print(f"Role: {message.role}")
print(f"Content: {message.content}")
print(message)

