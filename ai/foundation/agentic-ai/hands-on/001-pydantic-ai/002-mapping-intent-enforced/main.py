"""main.py - run the enforced router from the command line.

Run:   python main.py
       python main.py "add 2 and 3"

With no argument it replays the sample prompts from the README, so you can see
which ones are handled and which are refused.
"""
import sys

from agent import handle, router

SAMPLES = [
    "add 2 and 3",
    "how many words are in 'the quick brown fox jumps'?",
    "count the words in 'I am learning pydantic ai' and then add 100 to that count",
    "what is the capital of France?",
    "book me a flight to Cairo next Tuesday",
    "hi!",
]


def show(prompt: str) -> None:
    intent = router.run_sync(prompt).output
    print(f"prompt : {prompt}")
    print(f"intent : {type(intent).__name__} {intent.model_dump()}")
    print(f"reply  : {handle(prompt)}")
    print("-" * 70)


if __name__ == "__main__":
    prompts = sys.argv[1:] or SAMPLES
    for p in prompts:
        show(p)
