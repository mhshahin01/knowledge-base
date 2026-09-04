# Python Foundations for AI

This course starts at zero and grows toward building reliable AI applications with tools such as Pydantic and Pydantic AI.

The course targets **Python 3.14**, the current stable Python feature line. Every example is a runnable `.py` file.

## How to study

For each chunk:

1. Read the short explanation.
2. Predict what each example will print.
3. Run the example.
4. Change one thing and run it again.
5. Complete the small practice task before moving on.

You do not need to memorize everything. Aim to understand what the code is asking Python to do.

## Learning path

| Chunk | Topic | Why it matters for AI applications |
|---|---|---|
| [01](01-first-steps/lesson.md) | Running Python, values, variables, and basic input | Every Python program uses these ideas |
| [02](02-decisions/lesson.md) | Decisions with `if` | Choose what an application should do |
| [03](03-collections-and-loops/lesson.md) | Lists, dictionaries, and loops | Work with collections of messages and data |
| [04](04-functions/lesson.md) | Functions | Organize reusable application behavior |
| [05](05-errors-and-debugging/lesson.md) | Errors and debugging | Make failures understandable and recoverable |
| [06](06-files-modules-and-packages/lesson.md) | Files, modules, and packages | Structure a real project |
| [07](07-type-hints/lesson.md) | Type hints | Describe data clearly before using Pydantic |
| [08](08-classes-and-data-models/lesson.md) | Classes and data models | Understand model-based application design |
| [09](09-environments-and-dependencies/lesson.md) | Virtual environments and dependencies | Install frameworks safely |
| [10](10-async-python/lesson.md) | Async Python | Handle AI and web requests efficiently |
| [11](11-json-http-and-apis/lesson.md) | JSON, HTTP, and APIs | Exchange data with AI services |
| [12](12-pydantic-foundations/lesson.md) | Pydantic foundations | Validate structured application data |
| [13](13-first-pydantic-ai-app/lesson.md) | First Pydantic AI application | Apply the full foundation |

## Run an example

Open a terminal in this course folder. On Windows, run:

```powershell
py 01-first-steps/examples/01_hello.py
```

On macOS or Linux, use `python3` instead of `py`.

## Advanced-chunk dependencies

Chunks 09–13 use the versions recorded in [requirements.txt](requirements.txt). They were verified together on September 4, 2026.
