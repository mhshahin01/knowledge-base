"""main.py - run either router from the command line.

Run:   python main.py                       single-intent, sample prompts
       python main.py --multi               multi-intent, sample prompts
       python main.py --multi "add 2 and 3" multi-intent, your own prompt

The two agent files are kebab-case to match the repo convention, and a hyphen is
not a legal Python identifier, so `import agent-multi-intents` is a syntax error.
load_agent() sidesteps that by loading the file by path, which is all `import`
does underneath anyway.
"""
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

SAMPLES = [
    "add 2 and 3",
    "how many words are in 'the quick brown fox jumps'?",
    "count the words in 'I am learning pydantic ai' and then add 100 to that count",
    "what is the capital of France?",
    "book me a flight to Cairo next Tuesday",
    "hi!",
]


def load_agent(filename: str) -> ModuleType:
    """Import a module from a path, so kebab-case filenames still work."""
    path = Path(__file__).parent / filename
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def show(module: ModuleType, prompt: str) -> None:
    output = module.router.run_sync(prompt).output
    intents = output if isinstance(output, list) else [output]
    rendered = ", ".join(f"{type(i).__name__}{i.model_dump()}" for i in intents)
    print(f"prompt : {prompt}")
    print(f"intent : {rendered}")
    print(f"reply  : {module.dispatch(output)}")   # same output, no 2nd model call
    print("-" * 70)


if __name__ == "__main__":
    args = sys.argv[1:]
    multi = "--multi" in args
    prompts = [a for a in args if not a.startswith("--")] or SAMPLES

    module = load_agent("agent-multi-intents.py" if multi else "agent-single-intent.py")
    print(f"== {'multi' if multi else 'single'}-intent ==\n")
    for prompt in prompts:
        show(module, prompt)
