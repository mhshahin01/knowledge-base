"""wrapper-pydantic.py - the same call, through Pydantic AI.

Identical behaviour to wrapper-openai.py: read a line, ask the model, print the
reply. The difference is that the request shape and the response shape are both
hidden behind Agent, so there is less to get wrong and less to see.

`instructions` here becomes the same "system" role entry that wrapper-openai.py
builds by hand. The model receives an identical request either way. What differs
is bookkeeping: `instructions` is read from the agent on every run, while a
`system_prompt` would be stored in the message history and replayed. See section
5.1 of ../../../002-pydantic-ai-basics.md.

Run:  python wrapper-pydantic.py
"""
from dotenv import load_dotenv
load_dotenv()
from pydantic_ai import Agent

MODEL = "openai:gpt-5"

INSTRUCTIONS = (
    "You are a concise medical assistant for medicine students You can only answer medical questions. Other than this to be rejected!. "
    "Answer in at most two sentences."
)

agent = Agent(MODEL, instructions=INSTRUCTIONS)


def ask(prompt: str) -> str:
    """Send one message, return the reply text."""
    return agent.run_sync(prompt).output


if __name__ == "__main__":
    prompt = input("You: ")
    print("AI :", ask(prompt))
