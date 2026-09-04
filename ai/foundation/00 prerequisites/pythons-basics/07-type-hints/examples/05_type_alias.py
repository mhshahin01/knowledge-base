type Message = dict[str, str]


def create_message(role: str, content: str) -> Message:
    return {"role": role, "content": content}


def display_messages(messages: list[Message]) -> None:
    for message in messages:
        role = message["role"].upper()
        print(f"{role}: {message['content']}")


conversation: list[Message] = [
    create_message("system", "Answer briefly."),
    create_message("user", "Explain type hints."),
]

display_messages(conversation)
