from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


json_text = '{"role":"user","content":"Explain JSON models."}'
message = ChatMessage.model_validate_json(json_text)

print(message.model_dump())
print(message.model_dump_json())
