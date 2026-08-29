"""compare.py - one question, three backends, one table.

wrapper-multi.py proves the swap works. This file makes the swap worth doing:
it sends the same prompt, with the same persona, to all three backends and puts
the answers next to each other with what each one cost in time, tokens and money.

The registry and the persona are copied from wrapper-multi.py rather than
imported. That is deliberate, and it matches 003: each file in these exercises
reads top to bottom on its own, without you having to open another one.

Run:  python compare.py
      "What are the symptoms of anaemia?" | python compare.py
"""
import sys
import time

from dotenv import load_dotenv
load_dotenv()
from pydantic_ai import Agent

MODELS = {
    "haiku": "anthropic:claude-haiku-4-5",   # cloud, paid, needs ANTHROPIC_API_KEY
    "gpt-oss": "ollama:gpt-oss:latest",      # local, free, needs OLLAMA_BASE_URL
    "gemma": "ollama:gemma3:270m",           # local, free, needs OLLAMA_BASE_URL
}

INSTRUCTIONS = (
    "You are a concise medical assistant for medicine students. You can only answer "
    "medical questions. Reject anything else. "
    "Answer in at most two sentences."
)


def run_one(name: str, prompt: str) -> dict:
    """Ask one backend, and time it. Returns one row of the comparison table.

    Every field below comes off the same AgentRunResult regardless of which
    backend answered. That uniformity is the point: nothing here branches on
    whether the reply came from Anthropic's servers or from localhost.
    """
    agent = Agent(MODELS[name], instructions=INSTRUCTIONS)

    started = time.perf_counter()
    result = agent.run_sync(prompt)
    elapsed = time.perf_counter() - started

    return {
        "model": name,
        "reply": result.output,
        "seconds": elapsed,
        "input_tokens": result.usage.input_tokens,
        "output_tokens": result.usage.output_tokens,
        "cost": result.usage.cost,          # None for Ollama: no price list to look up
    }


def handle_failure(name: str, error: Exception) -> dict | None:
    """Decide what ONE backend's failure does to the WHOLE comparison.

    Called when a backend raises instead of answering. The realistic causes:
    ANTHROPIC_API_KEY missing or wrong, the Ollama daemon not running, the
    model never pulled, the network gone.

    You have three options, and the caller below already handles all three:

      * return a row dict (same keys as run_one, with `reply` set to an error
        message and the numbers zeroed) -> the failure is recorded as a row and
        the other backends still run
      * return None -> this backend is dropped silently and the others still run
      * raise -> the whole comparison aborts here

    What is implemented below is the middle option: record the failure as a row
    and keep going. The reasoning is that the backend most likely to fail is the
    only paid one, and losing a free two-row local comparison because a cloud key
    was missing is the worse outcome. A visible FAILED row keeps the gap honest,
    which a silent `return None` would not.

    Swap it for either of the other two if you disagree - the caller handles all
    three, and this is the one decision in the exercise with no right answer.
    """
    return {
        "model": name,
        "reply": f"FAILED: {type(error).__name__}: {error}",
        "seconds": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cost": None,
    }


def print_table(rows: list[dict]) -> None:
    """The numbers first, compactly, then each reply in full underneath."""
    print()
    print(f"{'model':<9} {'seconds':>8} {'in':>5} {'out':>5} {'cost $':>10}")
    print("-" * 41)
    for row in rows:
        cost = "-" if row["cost"] is None else f"{row['cost']:.6f}"
        print(
            f"{row['model']:<9} {row['seconds']:>8.2f} {row['input_tokens']:>5} "
            f"{row['output_tokens']:>5} {cost:>10}"
        )

    for row in rows:
        print(f"\n{row['model']}:")
        print(" ".join(row["reply"].split()))


if __name__ == "__main__":
    prompt = input("You: ") if sys.stdin.isatty() else sys.stdin.read().strip()

    rows = []
    for name in MODELS:
        print(f"asking {name}...", file=sys.stderr)
        try:
            rows.append(run_one(name, prompt))
        except Exception as error:
            row = handle_failure(name, error)
            if row is not None:
                rows.append(row)

    print_table(rows)
