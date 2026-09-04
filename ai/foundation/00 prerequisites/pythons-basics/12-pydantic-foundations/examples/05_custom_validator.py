from pydantic import BaseModel, field_validator


class ChatMessage(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def clean_content(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("content cannot be empty")

        return cleaned_value


message = ChatMessage(content="  Explain validators.  ")
print(f"Content: {message.content}")

