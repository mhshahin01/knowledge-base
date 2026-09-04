# Chunk 13: Your First Pydantic AI Application

## Goal

By the end of this chunk, you will be able to:

- create and run a Pydantic AI agent;
- use synchronous and asynchronous runs;
- require validated structured output;
- give an agent a function tool and typed dependencies;
- switch deliberately from an offline test model to a real provider.

These examples use Pydantic AI 2.39.0. Install the course dependencies from Chunk 09 first.

## 1. An agent connects instructions, a model, and a prompt

A Pydantic AI `Agent` coordinates a model run. Its main pieces are:

- the **model**, which produces responses;
- reusable **instructions**, which describe the agent's behavior;
- a run **prompt**, which contains the current request;
- a **result**, whose `.output` contains the final value.

The first example uses `TestModel`, Pydantic AI's built-in offline model. It does not call an LLM or require an API key. `custom_output_text` makes its result predictable while you learn the agent interface.

Run [01_first_agent.py](examples/01_first_agent.py).

Expected output:

```text
A function is a reusable block of code.
```

`run_sync()` is convenient for a small synchronous script.

## 2. Agents also run asynchronously

In an async application, await `agent.run()` instead of calling `run_sync()`. The returned result still provides `.output`.

The next example connects the async foundation from Chunk 10 to an agent run.

Run [02_async_agent.py](examples/02_async_agent.py).

Expected output:

```text
Async agents can wait without blocking other async work.
```

Use the sync interface for a simple script and the async interface when already inside an async application.

## 3. Structured output returns a validated model

Pass a Pydantic model as `output_type` when your application needs data rather than free-form text. Pydantic AI asks the model for that shape and validates the result.

The next example requires a `LessonPlan`. The offline `TestModel` supplies known output arguments, and Pydantic validates them before `result.output` becomes a `LessonPlan` instance.

Run [03_structured_output.py](examples/03_structured_output.py).

Expected output:

```text
Plan type: LessonPlan
Title: Functions
Minutes: 20
Topics: parameters, return values
```

With a real model, invalid structured output can be sent back for correction according to the agent's retry settings.

## 4. Tools let a model request Python work

A **function tool** lets the model ask your Python code to perform an action or retrieve information. Pydantic AI builds the tool schema from the function's name, type hints, parameters, and docstring.

Use:

- `@agent.tool_plain` when the function needs no run context;
- `@agent.tool` when it needs `RunContext`, such as access to dependencies.

The next example stores course progress in a dataclass dependency. `get_completed_lessons()` receives it through `RunContext`. The offline test model calls the tool before returning its final text.

Run [04_tool_and_dependencies.py](examples/04_tool_and_dependencies.py).

Expected output:

```text
Tool read: Maya completed 8 lessons.
Maya has completed 8 lessons.
```

Dependencies are values your application supplies for one run. They keep databases, settings, clients, and user context out of global variables.

## 5. Switching to a real model is explicit

A real model requires a provider/model name and usually a provider API key. The final example reads the model name from `PYDANTIC_AI_MODEL`. Without that variable, it exits safely without making a request.

Run [05_real_model.py](examples/05_real_model.py) as-is first.

Expected output:

```text
Set PYDANTIC_AI_MODEL before running a real model.
```

To use a real provider, consult its current Pydantic AI setup page. Then set the provider's required API-key variable and a supported model string. For example, the shape in PowerShell is:

```powershell
$env:PYDANTIC_AI_MODEL = "provider:model-name"
$env:PROVIDER_API_KEY = "your-secret-key"
python 13-first-pydantic-ai-app/examples/05_real_model.py
```

`PROVIDER_API_KEY` is a placeholder; use the exact environment-variable name documented by your chosen provider. Never save a real key in these `.py` files or print it.

Real model output varies and may incur cost. Start with the offline examples until their structure is comfortable.

## How the foundation fits together

This small agent now uses concepts from the entire course:

| Foundation | Pydantic AI use |
|---|---|
| Variables and collections | Prompts, messages, and settings |
| Decisions and errors | Validation and recovery paths |
| Functions | Tools and application logic |
| Modules and packages | Project organization |
| Type hints | Tool schemas and expected data |
| Async Python | Non-blocking model and API calls |
| HTTP and JSON | Provider communication |
| Classes and Pydantic | Dependencies and structured output |

## Practice: build a study coach

Create `study_coach.py` in the `examples` folder:

1. Define a `StudyAdvice` Pydantic model with `topic: str`, `minutes: int`, and `first_step: str`.
2. Constrain `minutes` to `1` through `60`.
3. Create a `TestModel` with valid `custom_output_args`.
4. Create an agent with short teaching instructions and `output_type=StudyAdvice`.
5. Run it with a learning request.
6. Print each field from `result.output`.

### Optional challenge

Add a typed `available_topics()` tool that returns a list of strings. Confirm that `TestModel` calls it before producing the structured result.

## Check your understanding

1. Where is an agent run's final value stored?
2. What is the async alternative to `run_sync()`?
3. What does `output_type` provide?
4. When should a tool use `RunContext`?
5. Why begin with `TestModel`?

Answers: (1) `result.output`; (2) `await agent.run(...)`; (3) a required, validated output shape; (4) when it needs run dependencies or other context; (5) it is fast, deterministic, offline, and costs nothing.

## Foundation complete

You now have the Python foundation needed to understand a small typed AI application. The next learning stage should build one focused project, adding real model access, testing, logging, and deployment only as the project needs them.

Official references: [Pydantic AI installation](https://pydantic.dev/docs/ai/overview/install/), [agents](https://pydantic.dev/docs/ai/core-concepts/agent/), [output](https://pydantic.dev/docs/ai/core-concepts/output/), [function tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/), and [testing](https://pydantic.dev/docs/ai/guides/testing/).
