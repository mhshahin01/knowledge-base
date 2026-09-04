def create_message(role, content):
    return {"role": role, "content": content}


def display_messages(messages):
    for message in messages:
        role = message["role"].upper()
        content = message["content"]
        print(f"{role}: {content}")


conversation = [
    create_message("system", "Answer simply."),
    create_message("user", "What does return do?"),
]

display_messages(conversation)
