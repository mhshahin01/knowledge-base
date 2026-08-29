"""agent.py - intent routing with the scope guard ENFORCED in code.

Companion to ../001-mapping-intent, which asks the model to refuse out-of-scope
requests in its system prompt. That is advisory: the model decides whether to
honour it, and it invents capabilities it does not have.

Here the model only classifies. It returns one of three typed intents, validated
by Pydantic. Every side effect and every user-facing string is produced by the
code below, so an unsupported request cannot be answered and the capability list
cannot drift from the real handlers.
"""
import os
from typing import Literal, Union

from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel
from pydantic_ai import Agent

if os.getenv("OPENAI_API_KEY"):
    MODEL = "openai:gpt-5"
    print("Using real model")
else:
    from pydantic_ai.models.test import TestModel
    MODEL = TestModel()


# --- The intents: the only shapes the model is allowed to return -------------
class AddNumbers(BaseModel):
    """The user wants two numbers added."""
    kind: Literal["add_numbers"]
    a: int
    b: int


class WordCount(BaseModel):
    """The user wants the words in a piece of text counted."""
    kind: Literal["word_count"]
    text: str


class OutOfScope(BaseModel):
    """The request matches no supported intent."""
    kind: Literal["out_of_scope"]
    reason: str


Intent = Union[AddNumbers, WordCount, OutOfScope]


router = Agent(
    MODEL,
    output_type=Intent,
    system_prompt=(
        "Classify the user's request into exactly one intent. "
        "If it is not addition or word counting, return out_of_scope."
    ),
)


# --- The handlers: ordinary functions, no model involved ----------------------
CAPABILITIES = [
    "add two numbers together",
    "count the words in a text",
]


def add_numbers(a: int, b: int) -> int:
    return a + b


def word_count(text: str) -> int:
    return len(text.split())


def refusal() -> str:
    return "Sorry, I can't do that. I can: " + "; ".join(CAPABILITIES) + "."


def handle(prompt: str) -> str:
    """Classify with the model, then dispatch in code."""
    intent = router.run_sync(prompt).output
    if isinstance(intent, AddNumbers):
        return f"{intent.a} + {intent.b} = {add_numbers(intent.a, intent.b)}"
    if isinstance(intent, WordCount):
        return f"{word_count(intent.text)} words"
    return refusal()
