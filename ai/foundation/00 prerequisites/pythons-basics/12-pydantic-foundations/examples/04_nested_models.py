from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class Conversation(BaseModel):
    messages: list[ChatMessage]


incoming_data = {
    "messages": [
        {"role": "system", "content": "Answer clearly."},
        {"role": "user", "content": "Explain Pydantic."},
    ]
}

conversation = Conversation.model_validate(incoming_data)

print(f"Message count: {len(conversation.messages)}")
print(f"First role: {conversation.messages[0].role}")
print(f"Second content: {conversation.messages[1].content}")

