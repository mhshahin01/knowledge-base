"""option-a-all-messages.py - multi-turn chat, Option A: accumulate the transcript.

Five scripted turns through the same agent. After each run, the NEXT run is
handed `result.all_messages()`: the history we passed in plus everything this
run produced. The model sees the whole conversation every turn, so "my unit"
and "tomorrow" resolve.

The twin file, option-b-new-messages.py, is byte-identical except for the one
marked line near the bottom. Run both and compare the traces.

Run:  python option-a-all-messages.py
"""
import os

from dotenv import load_dotenv
load_dotenv()  # .env has the API key for the model

from pydantic_ai import Agent

if os.getenv("OPENAI_API_KEY"):
    MODEL = "openai:gpt-5"        # any real model string works
    print("Using real model")
else:
    from pydantic_ai.models.test import TestModel
    MODEL = TestModel()           # free fake model: traces still show the mechanics

INSTRUCTIONS = (
    "You are the assistant of a residential compound Admin Office. "
    "Answer briefly and factually. Today is 2026-09-02. "
    "Use the bookings_by_unit tool for any booking question, "
    "with day='today' or day='tomorrow' as the resident means."
)

agent = Agent(MODEL, instructions=INSTRUCTIONS)

# --- a tiny deterministic booking service, so the traces are stable ---
BOOKINGS = {
    ("A-12", "today"): [{"amenity": "Swimming Pool", "time": "18:00"}],
    ("A-12", "tomorrow"): [{"amenity": "Yoga Room", "time": "07:00"}],
}


@agent.tool_plain
def bookings_by_unit(unit_id: str, day: str = "today") -> list[dict]:
    """Show all bookings for one residential unit.

    Args:
        unit_id: The unit identifier, for example A-12 or B-07.
        day: 'today' or 'tomorrow'.
    """
    return BOOKINGS.get((unit_id.upper(), day), [])


TURNS = [
    "My unit is A-12.",
    "Any bookings for my unit today?",
    "And tomorrow?",
    "Which amenity did I book tomorrow?",
    "What was my unit again?",
]


def show_trace(messages, indent="  "):
    """Print every message part: what the model actually receives."""
    if not messages:
        print(f"{indent}(empty)")
    for m in messages:
        for p in m.parts:
            kind = type(p).__name__
            if kind == "ToolCallPart":
                text = f"{p.tool_name}({p.args})"
            else:
                text = str(getattr(p, "content", ""))[:70]
            print(f"{indent}{kind:16} {text}")


def main():
    history = []
    for i, text in enumerate(TURNS, start=1):
        print("=" * 60)
        print(f"TURN {i}/{len(TURNS)}: {text!r}")
        print(f"--- history handed in ({len(history)} messages) ---")
        show_trace(history)
        result = agent.run_sync(text, message_history=history or None)
        print("--- reply ---")
        print(f"  {result.output}")
        print(f"--- usage: {result.usage}")
        history = result.all_messages()   # Option A: accumulate the whole transcript
    print("=" * 60)
    print("FINAL TRANSCRIPT (what the model would see on a turn 6):")
    show_trace(history)


if __name__ == "__main__":
    main()
