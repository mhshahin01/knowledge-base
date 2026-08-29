"""agent-multi-intents.py - one prompt, an ordered LIST of typed intents.

Companion to agent-single-intent.py, which returns exactly one intent per prompt
and therefore drops half of a compound request:

    "count the words in 'I am learning pydantic ai' and then add 100 to that count"
    -> WordCount(text=...)        the "add 100" half is silently lost

Here output_type is list[Intent]. The model returns the steps in order, code runs
them in order, and a later step can consume an earlier one's number through the
"previous_result" operand.

Enforcement is unchanged and that is the point: widening the output from one
intent to a list of intents does not hand any prose back to the model. It still
emits nothing but validated shapes, and every string the user reads is still
written by the handlers below.
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


# --- Operands: a literal number, or a reference to the last step's result ----
PREV = "previous_result"

Operand = Union[int, Literal["previous_result"]]


# --- The intents: the only shapes the model is allowed to return -------------
class AddNumbers(BaseModel):
    """Add two numbers. Use "previous_result" for a value the step before produced."""
    kind: Literal["add_numbers"]
    a: Operand
    b: Operand


class WordCount(BaseModel):
    """Count the words in a piece of text. Produces a number later steps can use."""
    kind: Literal["word_count"]
    text: str


class OutOfScope(BaseModel):
    """A step that matches no supported intent."""
    kind: Literal["out_of_scope"]
    reason: str


Intent = Union[AddNumbers, WordCount, OutOfScope]


router = Agent(
    MODEL,
    output_type=list[Intent],
    system_prompt=(
        "Break the user's request into an ordered list of intents, one per step. "
        "Most requests are a single step, so return a list of one. "
        'When a step needs a number the previous step produces, put "previous_result" '
        "in place of that number instead of guessing it. "
        "Return out_of_scope for any step that is not addition or word counting."
    ),
)


# --- The handlers: ordinary functions, no model involved ----------------------
CAPABILITIES = [
    "add two numbers together",
    "count the words in a text",
    "chain those two in one request",
]


def add_numbers(a: int, b: int) -> int:
    return a + b


def word_count(text: str) -> int:
    return len(text.split())


def refusal() -> str:
    return "Sorry, I can't do that. I can: " + "; ".join(CAPABILITIES) + "."


def dangling_reference() -> str:
    return "Sorry, a step referred to a previous result before one existed."


class StepFailed(Exception):
    """Carries a code-owned message explaining why the plan stopped."""


def resolve(operand: Operand, previous: int | None) -> int:
    """Turn one operand into a concrete number.

    This is where chaining actually happens: "previous_result" is not a value the
    model invented, it is a promise the code keeps by substituting the number the
    last step returned.
    """
    if operand == PREV:
        if previous is None:
            raise StepFailed(dangling_reference())
        return previous
    return operand


def run_step(intent: Intent, previous: int | None) -> tuple[str, int]:
    """Run one validated intent. Returns the line to show and the number to carry."""
    if isinstance(intent, AddNumbers):
        a = resolve(intent.a, previous)
        b = resolve(intent.b, previous)
        total = add_numbers(a, b)
        return f"{a} + {b} = {total}", total
    if isinstance(intent, WordCount):
        count = word_count(intent.text)
        return f"{count} words", count
    raise StepFailed(refusal())


def dispatch(plan: list[Intent]) -> str:
    """Run a validated plan in order. No model involved."""
    if not plan:
        return refusal()

    # Policy: all-or-nothing. One unsupported step refuses the whole plan, so a
    # request is never half-executed. Run the supported steps first instead if
    # your handlers are read-only and partial progress is useful.
    if any(isinstance(step, OutOfScope) for step in plan):
        return refusal()

    lines: list[str] = []
    previous: int | None = None
    for position, step in enumerate(plan, start=1):
        try:
            line, previous = run_step(step, previous)
        except StepFailed as stop:
            return str(stop)
        lines.append(f"{position}. {line}" if len(plan) > 1 else line)
    return "\n".join(lines)


def handle(prompt: str) -> str:
    """Classify into a plan with the model once, then run the plan in code."""
    return dispatch(router.run_sync(prompt).output)
