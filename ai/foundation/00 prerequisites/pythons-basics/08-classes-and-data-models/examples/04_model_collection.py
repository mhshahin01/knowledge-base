from dataclasses import dataclass


@dataclass
class ChatMessage:
    role: str
    content: str


def display_messages(messages: list[ChatMessage]) -> None:
    for message in messages:
        print(f"{message.role.upper()}: {message.content}")


conversation = [
    ChatMessage(role="system", content="Answer clearly."),
    ChatMessage(role="user", content="What is a data model?"),
]

display_messages(conversation)

