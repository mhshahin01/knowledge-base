"""wrapper-multi.py - 003's wrapper, with the backend chosen at the command line.

Identical to wrapper-pydantic.py from 003 except for one thing: the model string
comes out of a dict instead of being hard-coded. That dict is the whole exercise.
Three backends, three very different machines, one code path:

    haiku    Anthropic's cloud, paid per token, needs a key
    gpt-oss  20B parameters, ~13 GB, running on your own machine, free
    gemma    270M parameters, ~291 MB, running on your own machine, free

Nothing below the dict knows which one it got. That is the claim 003 made when
it said swapping provider was a one-line change; this file is the receipt.

Run:  python wrapper-multi.py            # gemma, the default, free and local
      python wrapper-multi.py gpt-oss
      python wrapper-multi.py haiku
"""
import sys

from dotenv import load_dotenv
load_dotenv()
from pydantic_ai import Agent

MODELS = {
    "haiku": "anthropic:claude-haiku-4-5",   # cloud, paid, needs ANTHROPIC_API_KEY
    "gpt-oss": "ollama:gpt-oss:latest",      # local, free, needs OLLAMA_BASE_URL
    "gemma": "ollama:gemma3:270m",           # local, free, needs OLLAMA_BASE_URL
}

DEFAULT = "gemma"

INSTRUCTIONS = (
    "You are a concise medical assistant for medicine students. You can only answer "
    "medical questions. Reject anything else. "
    "Answer in at most two sentences."
)


def ask(name: str, prompt: str) -> str:
    """Send one message to the named backend, return the reply text."""
    agent = Agent(MODELS[name], instructions=INSTRUCTIONS)
    return agent.run_sync(prompt).output


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    if name not in MODELS:
        sys.exit(f"Unknown model {name!r}. Pick one of: {', '.join(MODELS)}")

    prompt = input("You: ")
    try:
        print(f"AI ({name}):", ask(name, prompt))
    except Exception as error:
        # A missing key or a stopped Ollama daemon is a configuration problem, not
        # a bug, and a 40-line traceback buries the one line that says which.
        # Note where this sits: at the edge, not inside ask(). The part of the
        # program that talks to models still has no idea which backend it got.
        sys.exit(f"{name} failed: {type(error).__name__}: {error}")
