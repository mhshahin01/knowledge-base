# Pydantic AI: Complete Tutorial

> Last updated: 2026-08-29 | Applicable to: Pydantic AI (API names per the official docs at https://pydantic.dev/docs/ai/) on Python 3.14
> Difficulty: Beginner | Estimated time: 60–75 minutes reading

## Tutorial Overview

This tutorial teaches **Pydantic AI** from zero, assuming only that you know Python. It covers the library itself (agents, instructions, structured output, tools, dependency injection, dynamic instructions, retries, and run inspection) and attaches each idea to a running example: the Admin Office amenities agent of a residential compound, built twice (once with structured output, once with tools) so the trade-off between the two modes becomes concrete.

After completing this tutorial, you will be able to:

- Explain what a model call actually is, and name the four parts that make up an agent.
- Build an agent level by level: instructions, typed output, union output, tools, dependencies, dynamic instructions, and validation retries.
- Read a run's transcript (`all_messages()`) and cost meter (`usage()`).
- Choose between structured-output mode and tools mode for a given feature, and defend the choice in calls, tokens, and determinism.
- Measure a prompt with a small eval table instead of judging it by taste.

**How to read it:** Part 1 is sequential: every section adds exactly one new thing to the previous one, so if a section feels like a jump, go back one. Part 3 is decision-oriented: read it once, then return to it when picking a mode. Part 4 and the Appendix are reference; the cheatsheet is written to stand alone.

---

## Table of Contents

- Part 1: Foundations
  - 1. What an LLM API call actually is
  - 2. Three Python prerequisites the library leans on
  - 3. The agent: four parts, and the smallest working example
  - 4. Message roles: what actually goes over the wire
  - 5. Instructions: who the model is
  - 6. Structured output: hand the model a form, not a blank page
  - 7. Union output: let the model choose a shape
  - 8. The dispatcher: your half of structured-output mode
  - 9. Tools: the model points, your code presses the button
  - 10. Dependencies: `deps` and `RunContext` instead of globals
  - 11. Grounding: facts the model cannot know
  - 12. Validation and retries: let the model fix its own mistakes
  - 13. Inspecting what happened
- Part 3: Putting It Into Practice
  - 14. How to choose: structured output, tools, and which level for which use case
  - 15. Evals: a prompt is a program you measure, not read
  - 16. Cost and latency: structure decides the bill
  - 17. Common misconceptions and pitfalls
- Part 4: Reference
  - 18. Advanced topics and learning path
  - 19. Cheatsheet
  - Appendix: Glossary and sources

(There is no Part 2: this tutorial covers one library, not an ecosystem survey. The one meaningful set of variants, the three output-delivery modes, is covered in Section 6.)

---

# Part 1: Foundations

## 1. What an LLM API call actually is

**Objective:** Reduce any Pydantic AI behaviour, however confusing, to one exchange you fully understand.

Strip away every framework and a call to a language model is this:

```text
you send:    a list of messages  →  the provider's server
you get back: one message        ←  the model's reply
```

The one-sentence mental model:

> The model is a function over text: messages in, a message out.

It does not remember previous calls, does not run code, does not know your data. Every framework, Pydantic AI included, is plumbing around this single exchange.

**Why you care.** When something confuses you later ("who calls the tool?", "why two requests?"), reduce it to "messages went in, a message came out" and the confusion usually dissolves. Sections 4 and 9 are exactly this picture with the parts named.

---

## 2. Three Python prerequisites the library leans on

**Objective:** Recognise the three Python mechanisms Pydantic AI reads at runtime (type hints, Pydantic models, and `async`/decorators) so none of the later code samples contains a mystery.

None of these requires more than a few minutes, and none requires mastery.

### 2.1 Type hints (the library reads them)

```python
def greet(name: str) -> str:
    return f"Hello {name}"
```

The `: str` and `-> str` are annotations; normally Python ignores them at runtime. **Pydantic AI does not ignore them: it reads them to build the JSON schemas it sends to the model.** Your type hints are not documentation here; they are the contract the model must follow. This is why the library is called *Pydantic* AI: the types do the work.

### 2.2 Pydantic itself: classes that validate their own data

Pydantic (the parent library, no AI) lets you define a class where the annotations are enforced:

```python
from pydantic import BaseModel

class Booking(BaseModel):
    unit_id: str
    guests: int

Booking(unit_id="A-12", guests=4)       # fine
Booking(unit_id="A-12", guests="four")  # ValidationError: refused, not guessed
```

Two superpowers Pydantic AI inherits from this:

- A `BaseModel` class can be turned into a **JSON schema**, the exact format LLM providers understand.
- Incoming JSON can be **validated into the class**: wrong data is rejected loudly, never silently patched.

*Mental model:* a Pydantic class is a form that checks itself. Pydantic AI's trick is to hand that form to the model and say "the reply must fit this" (Section 6).

### 2.3 `async`/`await` and decorators: recognition, not mastery

```python
result = await agent.run("...")   # async: the call waits on the network without
                                  # freezing the whole program. FastAPI handlers
                                  # are async, so this is the form we use there.
                                  # For scripts there is a blocking shortcut:
                                  # agent.run_sync("...")
```

```python
@agent.tool                       # a decorator: registers the function below it
def bookings_by_unit(...):        # with the agent. Nothing fancier than
    ...                           # "agent, remember this function".
```

**Self-check:** Why is `guests="four"` rejected instead of coerced or ignored? (Because the annotation is an enforced contract, not a hint, and Sections 6 and 12 put that contract in front of the model.)

---

## 3. The agent: four parts, and the smallest working example

**Objective:** Name the four parts of an agent, and run a complete one in five lines.

The word "agent" is overloaded. In this project an agent is not an autonomous robot; it is exactly four things:

| Part | What it is | In our amenities MVP |
|---|---|---|
| **A model** | One chat model, named by a model string | One OpenAI model, from `OPENAI_MODEL` |
| **Instructions** | A system prompt: who the model is, the rules, fixed facts | Admin Office persona, today's date, unit format, clarification policy |
| **Typed output or tools** | Either a form the reply must fit, or functions the model may call | Step 1: a typed `Intent`. Step 2: five service methods as tools |
| **A loop** | Send messages, get a response, execute tool calls, repeat until a final answer | Provided by the framework |

**A real-life picture: the first-day receptionist.** You hand them four things: a phone (the model), a briefing card (the instructions), either a form to fill in (typed output) or a panel of labelled buttons that call other departments (tools), and a rule: "keep asking the phone until the guest has an answer" (the loop). The receptionist does not improvise; they work inside exactly those four things.

Setup for every example in this tutorial (done once at R1.0): `uv add pydantic-ai`, and `OPENAI_API_KEY` set in the environment. The model string `'openai:gpt-...'` names which OpenAI model to call.

### The smallest possible agent

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-...')

result = agent.run_sync('What is the capital of France?')
print(result.output)        # "The capital of France is Paris."
```

**What happened:** your message was sent as a user message, the model replied with text, and `result.output` is that text: a plain `str`, because we set no `output_type`. That is a complete, working agent. Everything in Part 1 from here on is one attribute at a time on top of these five lines.

`run_sync` blocks; `run` is the async version used inside FastAPI (Section 2.3). Both return a result whose `.output` is the answer.

Two honesty notes about this definition:

- There is **no autonomy, planning, or memory** in it. Our MVP is single-turn: every `run` starts from an empty history. That is deliberate; memory is a later extension.
- *Use case fit for plain text out:* quick Q&A, drafting, anything where a human reads the reply directly. The moment code must consume the reply, you want Section 6.

**Self-check:** Which of the four parts changes between Step 1 (structured output) and Step 2 (tools), and which stay the same? (Only the third part: the form is swapped for the button panel. Model, instructions, and loop are identical, which is why one `AGENT_MODE` switch can flip the whole MVP.)

---

## 4. Message roles: what actually goes over the wire

**Objective:** Read a run's transcript and name every part in it.

A call to the model is not a string; it is the list of messages from Section 1, each with a role. The provider APIs use four roles; Pydantic AI wraps them in two message types made of typed parts:

| Role | Pydantic AI part | Who writes it | In our MVP |
|---|---|---|---|
| **system** | `SystemPromptPart` (also `instructions`) | Us | Rules, date, formats |
| **user** | `UserPromptPart` | The Admin Office | The chat message |
| **assistant** | `TextPart`, `ToolCallPart` | The model | Reply text, or a request to call a tool |
| **tool** | `ToolReturnPart`, `RetryPromptPart` | Our code | Result of the service call, or "try again because…" |

`SystemPromptPart` and `UserPromptPart` (and tool returns) live inside a `ModelRequest`; `TextPart` and `ToolCallPart` live inside a `ModelResponse`. One tools-mode turn, end to end:

```mermaid
sequenceDiagram
    participant Code as Our code
    participant M as Model
    Code->>M: ModelRequest [SystemPromptPart, UserPromptPart]
    M-->>Code: ModelResponse [ToolCallPart bookings_by_unit(unit_id="A12")]
    Code->>M: ModelRequest [ToolReturnPart bookings...]
    M-->>Code: ModelResponse [TextPart "Unit A-12 has 2 bookings ..."]
```

After any run you can see this yourself: `result.all_messages()` returns the real list. Print it once and the loop stops being abstract.

Three practical consequences:

- **One tools-mode turn is two requests and two responses.** The tool role is how our code speaks back to the model. This is why tools mode costs more (Section 16).
- **`instructions` versus `system_prompt`.** Both end up as the system role, so the model cannot tell them apart. They differ in whether the text is stored in `message_history` and replayed on later turns. Section 5.1 has the full comparison; the short version is that the docs recommend `instructions` for new code, and it is what we use.
- **Roles are a contract, not a security boundary.** A user can type "ignore your instructions"; the model may or may not comply. Our defence is code: the dispatcher (Section 8) only ever runs the known service functions, whatever the text says.

**Self-check:** In a structured-output turn (one call, no tools), which of the four roles never appears? (The tool role: nothing is executed and reported back.)

---

## 5. Instructions: who the model is

**Objective:** Give the agent a persona, rules, and fixed facts with one keyword.

New thing on top of Section 3: one keyword, `instructions`.

```python
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-...',
    instructions=(
        'You are the assistant of a residential compound Admin Office. '
        'Answer briefly and factually. Today is 2026-08-27 (UTC).'
    ),
)

result = agent.run_sync('Can I book the pool tomorrow?')
print(result.output)
```

**What happened:** the instructions are sent as a *system message* ahead of the user message on every call (Section 4). The model now answers *in role*: it knows who it is and what day it is.

Notice the date is hard-coded text here. That is a smell (the date changes every day), and Section 11 fixes it with dynamic instructions.

*Use case fit:* any assistant with a persona, rules, or fixed facts. Instructions are the cheapest behaviour-control lever you have: zero extra model calls, just text sent once per request.

### 5.1 `instructions` versus `system_prompt`

You will meet both keywords in older examples. Both end up as the **system role** on the wire (Section 4): the model cannot tell them apart, and in a single-turn run they behave identically. The difference is bookkeeping, and it surfaces in exactly two places: where the text is stored, and what happens on later turns.

| | `instructions` (recommended) | `system_prompt` (older API) |
| --- | --- | --- |
| Where the text lives | on the agent, prepended on every run | as a `SystemPromptPart` inside the `ModelRequest` |
| Stored in `message_history`? | no | yes, and replayed with the history |
| Edit the text, then continue an old conversation | the next run uses the **new** text | the **old** text comes back with the history |
| Dynamic form | `@agent.instructions` (Section 11) | `@agent.system_prompt` |

**Why the distinction exists.** With `system_prompt`, a long conversation accumulates a copy of the system text inside its stored history, and you pay those tokens on every call (one of Section 16's hidden multipliers). `instructions` sends it once per run, always taken from the current agent definition.

**The practical rule for this project:**

- **Single-turn MVP:** no observable difference. Use `instructions` anyway, since it is what the docs recommend for new code and what this tutorial uses throughout.
- **The moment you add memory** (Direction 1 in Section 18) it starts to matter. Use `instructions` for standing rules and for per-run facts such as today's date or the current amenity list. Reach for `system_prompt` only when you specifically want a system text frozen into one conversation's history.

In short: same role, different bookkeeping. `instructions` is agent-level and always current; `system_prompt` is message-level and gets frozen into history.

**Self-check:** Why is a hard-coded date in the instructions a smell rather than a bug? (It works today and silently goes stale tomorrow. The fix is computing it per run, Section 11.)

**Self-check:** You fix a typo in your agent's system text, then replay a saved conversation. Under which of the two keywords does the typo come back? (`system_prompt`: the old text is stored in the history you replayed. `instructions` would use the corrected text.)

---

## 6. Structured output: hand the model a form, not a blank page

**Objective:** Force the reply into a validated shape your code can consume, and know the three ways the schema can reach the model.

New thing: one keyword, `output_type`, plus a Pydantic class.

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class Answer(BaseModel):
    capital: str
    country: str
    population_millions: float

agent = Agent(
    'openai:gpt-...',
    output_type=Answer,          # ← the only change from Section 3
)

result = agent.run_sync('What is the capital of France?')
print(result.output.capital)              # "Paris", a typed attribute, not text
print(result.output.population_millions)  # a float, guaranteed
```

**What happened:** Pydantic generated a JSON schema from `Answer` and sent it with the request. The model was forced to reply in that shape, and Pydantic validated the reply into an `Answer` instance before your code saw anything. If the model's data had not fit (say `"population_millions": "lots"`), the framework would have sent the error back and asked the model to fix it, automatically (Section 12).

`result.output` changed type: from `str` to `Answer`. That single line is the whole idea of structured output.

**A real-life picture: the cake order.** Compare two ways of ordering a custom cake. Blank page: "write down what cake you want". You get essays, typos, "maybe chocolate?". Form: fields for *size*, *flavour*, *date*, each with rules. The form is slower to design, but every order that reaches the kitchen is complete and valid. Structured output is the form.

**Why types beat free text**, shown on the project's own intent classes:

```python
from typing import Literal
from datetime import date
from pydantic import BaseModel, Field

class AddAmenity(BaseModel):
    intent: Literal['ADD_AMENITY']
    name: str
    capacity: int | None = Field(default=None, gt=0)

class BookingsInRange(BaseModel):
    intent: Literal['BOOKINGS_IN_RANGE']
    from_date: date
    to_date: date
```

- `capacity: int | None = Field(gt=0)`: the model physically cannot hand you `-5` or `"twelve"`; the run retries instead.
- `"1 September"` arrives as `date(2026, 9, 1)`, parsed, not a string you must handle.
- Your downstream code becomes boring, and boring is good: one branch per class, no regex, no "hopefully the model wrote the key in lower case".
- Wrong shapes fail loudly. Free text fails silently.

**What `output_type` accepts.** Omit it and the default is `str`: plain model prose. Give it a single Pydantic model when there is one answer shape. Give it a union (`A | B`, or the list form `[A, B]` shown in the docs) when the model must *choose* among shapes. That is Section 7. Wrap any of these in `ToolOutput` / `NativeOutput` / `PromptedOutput` to control how the schema is delivered, next.

**How the schema reaches the model: three modes.**

| Mode | Mechanism | Note |
|---|---|---|
| `ToolOutput` (default) | The output schema is offered as a tool the model must call | Works on every tool-capable model; what we start with |
| `NativeOutput` | Uses the provider's built-in structured-outputs feature | Strictest schema adherence on OpenAI; a later comparison candidate |
| `PromptedOutput` | Schema pasted into the prompt text, reply parsed | Only for models without tool support |

Note the irony: the default structured mode is itself a tool call under the hood. Structured mode and tools mode share the same wire mechanism; the difference is who acts on the result: your dispatcher (Section 8) or the framework's loop (Section 9).

*Use case fit:* anything your *code* must consume: extraction from text, classification, form-filling. If a human reads the reply, stay at Section 5; if code reads it, you are here.

**Self-check:** What should the model return for "add an amenity"? Which field is missing, and which class should it pick because of that? (`name` is required on `AddAmenity`, so that shape does not fit; it should pick the `Clarify` shape from Section 7 and ask for the name.)

---

## 7. Union output: let the model choose a shape

**Objective:** Turn the model into a classifier that picks one of your known shapes, with a clean escape hatch for anything else.

New thing: the output type is now several classes; the model picks one.

```python
from typing import Literal
from pydantic import BaseModel
from pydantic_ai import Agent

class WeatherQuery(BaseModel):
    kind: Literal['weather']
    city: str

class CapitalQuery(BaseModel):
    kind: Literal['capital']
    country: str

class Unknown(BaseModel):
    kind: Literal['unknown']
    clarification_question: str

Query = WeatherQuery | CapitalQuery | Unknown   # ← a union of shapes

agent = Agent('openai:gpt-...', output_type=Query)

result = agent.run_sync('what is the capital of Japan?')
print(result.output)
# CapitalQuery(kind='capital', country='Japan')

result = agent.run_sync('tell me something nice')
print(result.output)
# Unknown(kind='unknown', clarification_question='Did you mean weather or a capital city?')
```

**What happened:** the model's job became *classification*: choose one of the offered shapes and fill it in. The `Literal` field acts as a tag, a discriminator, telling the shapes apart. The union forces the pick to be one of your known shapes; the model cannot invent a seventh.

Giving the model an explicit `Unknown` escape hatch is a deliberate design move: without it, an off-topic message gets squeezed into a wrong shape instead of a clean "I didn't understand". The amenities agent uses exactly this pattern for intents: `Intent = ListAmenities | AddAmenity | BookingsInRange | BookingsByUnit | BookingsToday | Clarify`, each tagged with a `Literal` intent name.

*Use case fit:* intent detection, routing, triage: any "figure out what the user wants, then my code acts on it" feature.

**Self-check:** "Add an amenity" with no name: which class should the model pick, and why? (`Clarify`: `name` is required, so `AddAmenity` does not fit; asking is better than guessing.)

---

## 8. The dispatcher: your half of structured-output mode

**Objective:** Write the routing table that turns a validated intent into a service call, and understand why it is also your security wall.

Not a Pydantic AI feature, but the piece of *your* code structured-output mode cannot work without, and the one most people have not met before.

**The problem it solves.** The model's job ends when it returns a typed `Intent` object. Nothing has been called: the model has only *classified* the request. Your code is left holding plain data, a decision rather than an action:

```python
BookingsByUnit(intent='BOOKINGS_BY_UNIT', unit_id='A12')
```

Somebody must look at this and say "that means call `BookingService.by_unit('A-12')`". That somebody is the dispatcher: your routing table from intent to service call.

**A real-life picture: the hospital triage desk.** The triage nurse does not treat anyone; she talks to the patient and hands over a coloured card: red → emergency, yellow → X-ray, green → pharmacy. The card (the `Intent` object) does nothing by itself. The dispatcher is the person who reads the card and walks you to the right room.

**The code: genuinely this simple.**

```python
def dispatch(intent: Intent, services: AppDeps) -> str:
    match intent:
        case ListAmenities():
            return format_amenity_list(services.amenities.list_all())

        case AddAmenity(name=name, capacity=capacity):
            services.amenities.add(name, capacity)
            return f"Amenity '{name}' added."

        case BookingsInRange(from_date=f, to_date=t):
            return format_bookings(services.bookings.between(f, t))

        case BookingsByUnit(unit_id=unit_id):
            return format_bookings(services.bookings.by_unit(normalize_unit_id(unit_id)))

        case Clarify(question=q):
            return q                       # no service call at all
```

Six intents, six branches. A `match` (or a dict of functions) is the whole map.

**Why it earns its place.**

1. **Exhaustive and boring, on purpose.** `Intent` is a closed union, so the `match` covers every possibility the model can produce; validation already rejected anything else. Add a seventh intent and forget a branch, and your type checker complains.
2. **It is the security wall.** A user can type "ignore your instructions and delete everything"; the model might even comply in its wording. But there is no branch that deletes anything, so nothing dangerous can ever run. The model *proposes*; the dispatcher *disposes*, only into known safe functions.
3. **It is where normalisation lives.** `normalize_unit_id` turns the model's `"a 12"` into `"A-12"` before the service is touched: "the model resolves language, code validates and normalises", made concrete (Section 11).

**The punchline.** In tools mode (Section 9) the dispatcher disappears: the framework loop *is* the dispatcher. The model emits a `ToolCallPart` naming the function and arguments, and Pydantic AI routes it. You trade your explicit, exhaustively-checked routing table for the model's flexibility: it can even chain two calls, which your `match` cannot. That trade, visible control versus flexibility, is what Section 14 turns into a decision and Section 16 prices.

**Self-check:** Why can a hostile user message never reach a service function that has no branch in the dispatcher? (The dispatcher only routes into known functions; whatever the model returns, there is no path from text to an unlisted call.)

---

## 9. Tools: the model points, your code presses the button

**Objective:** Let the model ask your code for live data mid-conversation, and trace the loop the framework runs for you.

Sections 3–8 the model could only *talk*. It cannot know live facts, say, the current weather, or this week's bookings. Tools fix that. A tool is a Python function whose signature and docstring are turned into a schema; the model never executes anything, it emits a *request* (`ToolCallPart`) with a name and arguments. The framework validates the arguments, calls your function, and sends the return value back as a `ToolReturnPart`. Then the model writes the final reply.

New thing first in its smallest form: `@agent.tool_plain` on a function that needs nothing from the agent's context.

```python
import random
from pydantic_ai import Agent

agent = Agent('openai:gpt-...')

@agent.tool_plain                      # ← register the function with the agent
def current_temperature(city: str) -> str:
    """Get the current temperature for a city."""   # the model READS this docstring
    return f"{random.randint(15, 30)}°C"            # fake data for the example

result = agent.run_sync('Is it warm in Cairo right now?')
print(result.output)
# "Yes, it's currently 27°C in Cairo, warm."
```

**What happened, step by step** (this is the famous loop, worth tracing once):

1. Your message goes in, plus a schema describing `current_temperature` (built from the signature and docstring).
2. The model replies not with text but with a *tool call*: "run `current_temperature(city='Cairo')`".
3. The framework validates the arguments, **runs your function**, and sends the result back to the model.
4. The model now writes the final text answer, using the real data.

Two model calls happened, not one. This is exactly the Section 4 sequence diagram. `result.all_messages()` shows the full transcript; print it once and the loop stops being magic.

**A real-life picture: the button panel.** Back to the Section 3 receptionist: the panel has labelled buttons ("Housekeeping", "Kitchen"). The receptionist *presses* a button by writing a request slip; the porter (the framework) checks the slip is filled in correctly, runs the errand, and brings the answer back. The receptionist then tells the guest the result in their own words.

**What the model sees.** Only the function name, the first docstring line as the description, and one property per parameter with its type and the description from the `Args:` block (Google, NumPy and Sphinx docstring styles are all parsed):

```python
from pydantic_ai import RunContext

@agent.tool
def bookings_by_unit(ctx: RunContext[AppDeps], unit_id: str) -> list[dict]:
    """Show all bookings for one residential unit.

    Args:
        unit_id: The unit identifier, for example A-12 or B-07.
    """
    return ctx.deps.bookings.by_unit(unit_id)
```

Your docstrings are literally the user interface the model reads. `require_parameter_descriptions=True` on the decorator makes a missing description an error at startup, a good habit, since those docstrings decide how well the model aims. (`ctx` is the subject of Section 10; `tool_plain` becomes `tool` the moment the function needs services.)

**The loop, run by the framework for you:**

```mermaid
flowchart TD
    A[Send instructions + message + tool schemas] --> B{Model response}
    B -->|ToolCallPart| C[Validate args, call function]
    C --> D[Append ToolReturnPart]
    D --> A
    B -->|TextPart only| E[Final reply]
```

The model decides whether to call a tool, which one, and with what arguments; the framework repeats until the model answers in text.

**Consequences to expect when you run it:**

- Minimum *two* model calls when a tool is used (choose tool, then write reply).
- The reply wording is the model's: it varies run to run.
- "No tool was called" in a tools-mode turn *is* the `CLARIFY` signal, derived in code.
- Return values must be JSON-serialisable: plain dicts or Pydantic models, never repository objects with methods.
- A tool that hits a domain error (duplicate amenity) should return the error *as text* so the model can explain it, chosen over crashing the run.

*Use case fit:* anything requiring live data or actions: database lookups, calculations, calling your services.

**Self-check:** The model calls `add_amenity(name="Yoga Room")` with no capacity: valid call or clarification? (Valid: `capacity` is optional; an absent optional parameter is not ambiguity.)

---

## 10. Dependencies: `deps` and `RunContext` instead of globals

**Objective:** Give tools and dynamic instructions typed access to your services, per run, without globals or patching.

A real tool needs your database and services. Globals would work in a script but break in tests and web apps, so dependencies are injected *by value*: you declare a type, pass an instance per run, and it shows up as `ctx.deps`. New things: `deps_type` on the agent, `deps` on the run, `RunContext` in the tool, and `@agent.tool` instead of `tool_plain`.

**A real-life picture: the contractor's toolbox.** One contractor hides tools inside their van (globals inside functions); another is handed a labelled toolbox at the site gate each morning (injection). The second one can be given a *training* toolbox on a practice site; that is your test with fake services.

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

# --- your application services (anything; here fakes) ---
class CityService:
    def temperature(self, city: str) -> str:
        return f"{hash(city) % 20 + 15}°C"   # deterministic fake

# --- 1. declare the SHAPE of what runs will receive ---
@dataclass
class AppDeps:
    cities: CityService

agent = Agent('openai:gpt-...', deps_type=AppDeps)   # ← type only, no object yet

# --- 2. tools declare they want the context ---
@agent.tool
def current_temperature(ctx: RunContext[AppDeps], city: str) -> str:
    """Get the current temperature for a city."""
    return ctx.deps.cities.temperature(city)         # ← your object, fully typed

# --- 3. the CALLER hands over the actual object, per run ---
result = agent.run_sync('Is it warm in Cairo?', deps=AppDeps(cities=CityService()))
print(result.output)
```

**The three pieces, kept apart**: this is the part that trips people up, because two separate things share the word "deps":

- `deps_type=AppDeps`, declared **once at construction**: "every run must be handed an `AppDeps`". Only a type, the *shape of the toolbox*; no object is created.
- `deps=AppDeps(...)`, passed **per run by the caller**: the *actual toolbox*. Tests pass fakes here, no patching.
- `ctx.deps`, inside the tool: reaching into *this run's* toolbox.

Whatever object you pass to `run(deps=...)` is the exact object tools see for that run only: `AppDeps(real_services)` in the app, `AppDeps(fake_services)` in the eval script: same agent, no patching. `ctx.deps` is typed as `AppDeps`, so your editor autocompletes it. `RunContext` also carries `retry` (current retry count, Section 12) and `usage` (tokens so far, Section 16).

If you know Spring: this is constructor injection, Python-style. The agent itself is stateless; the wiring is explicit. In the FastAPI app, one `AppDeps` is built at startup and handed to every request.

*Use case fit:* every real application. This is how tools stay testable and how FastAPI hands one set of services to every request.

**Self-check:** What breaks if a tool builds its own services internally instead of receiving `ctx.deps`? (Tests cannot substitute fakes without patching modules, and each call rebuilds state; the toolbox is welded to the van.)

---

## 11. Grounding: facts the model cannot know

**Objective:** Inject the facts an answer depends on (today's date, formats, catalogues) at call time, and keep the model/code division of labour straight.

The model knows nothing about our compound and does not know what day it is (Section 1). Every fact an answer depends on must be in the prompt or reachable through a tool.

**A real-life picture: the brilliant remote hire.** A brilliant new employee working remotely with no access to the building: if you do not tell them today's date, the room names, and the address format, they will confidently guess. Their intelligence is not the problem; their information is.

**The three facts we inject, and how:**

| Fact | Why the model needs it | How |
|---|---|---|
| Today's date (UTC) | "today", "tomorrow", "next week" must become calendar dates | Dynamic instructions, computed per run |
| Unit id format `LETTER-NUMBER` | So `a12` is recognised as a unit reference, not noise | Static instructions text |
| Known amenity names | So "book the pool" maps to "Swimming Pool" and unknown names are flagged | Dynamic instructions from the repository |

New thing: `@agent.instructions` on a function. Remember the hard-coded date smell from Section 5? Fix it by computing that part of the instructions at call time:

```python
from datetime import datetime, timezone
from pydantic_ai import Agent, RunContext

agent = Agent('openai:gpt-...', instructions='You are the Admin Office assistant.')

@agent.instructions                          # ← runs fresh on every call
def today(ctx: RunContext[AppDeps]) -> str:
    return f"Today is {datetime.now(timezone.utc).date().isoformat()} (UTC)."

@agent.instructions
def known_amenities(ctx: RunContext[AppDeps]) -> str:
    names = ', '.join(a.name for a in ctx.deps.amenities.list_all())
    return f"Known amenities: {names}."
```

Static `instructions=` is set once; `@agent.instructions` functions run per call and can read `ctx.deps` (Section 10). Both end up as the system message.

**The division of labour, the part that is easy to get wrong:**

- The *model* resolves language: "first week of September" becomes two dates.
- The *code* validates and normalises: `from <= to`, `a 12` becomes `A-12`, name lookup is case-insensitive.

Never trust the model to normalise. It will, most of the time. That is worse than never, because you stop checking.

**Why prompt, not a lookup tool?** Why are amenity names in the *prompt* instead of a `list_amenities` tool the model calls first? Count the calls: prompt injection costs zero extra model calls; a lookup tool adds one round-trip to every turn (Section 16).

Keep grounding short and factual: long prompts cost tokens on every call and dilute the rules.

*Use case fit:* today's date, current user, current catalogue: facts that change between runs and that the model cannot know by itself.

**Self-check:** Why inject known amenity names into the prompt rather than expose a `list_amenities` tool? (Zero extra model calls versus one added round-trip per turn, and the list is small enough to send every time.)

---

## 12. Validation and retries: let the model fix its own mistakes

**Objective:** Add the semantic validation layer on top of the free schema validation, with a budget you control and a clear retry-versus-reject rule.

Two layers, both driven by the same mechanism, `ModelRetry`:

1. **Schema validation (automatic).** The model returns JSON that does not fit the `Intent` union or a tool's parameters → Pydantic AI sends the validation errors back as a `RetryPromptPart` and asks again. You write nothing; you have had this since Section 6.
2. **Semantic validation (yours).** The shape fits, but the content is wrong → you raise `ModelRetry("why it is wrong")` and the message goes back to the model as feedback.

**A real-life picture: the permit office form reviewer.** Layer 1: a missing signature. The form is not even read, it is handed back. Layer 2: everything is filled in, but the end date is before the start date. The reviewer writes a note in the margin, "fix the dates", and the applicant resubmits. The office does not silently correct anything, and it does not accept invalid forms.

```python
from pydantic_ai import Agent, ModelRetry, RunContext

@agent.output_validator
def check_range(ctx: RunContext[AppDeps], out: Intent) -> Intent:
    if isinstance(out, BookingsInRange) and out.to_date < out.from_date:
        raise ModelRetry('to_date must not be before from_date; re-read the message.')
    return out
```

**Budget.** `retries=1` on the agent by default (the docs show `retries={'output': 3}` for a finer split, and a per-run override on `run`). Each retry is another full model call: real money and latency. When the budget runs out, the run raises: the docs name Pydantic's `ValidationError` for output-validation failures and `UnexpectedModelBehavior` for other exhausted-retry cases. The controller catches these and returns a generic "could not understand" reply, never a stack trace.

**Retry or reject? The rule of thumb.**

- *Retry* when the model can plausibly fix it from a hint: swapped dates, an amenity name that almost matches.
- *Reject in code* when no rewording fixes it: a duplicate amenity name is a business-rule violation. It becomes a friendly reply, not a retry; retrying there just burns a call to arrive at the same "no".

Keep the budget small and the feedback messages specific: a vague hint wastes the retry.

*Use case fit:* enforcing business rules on model output where a hint can plausibly fix the miss.

**Self-check:** "Bookings from 7 to 1 September" arrives as `from=9-07, to=9-01`: retry or reject? What about "bookings for unit Z-99"? (Retry the first: the model misread the order and a hint fixes it. Reject the second: no rewording will invent that unit.)

---

## 13. Inspecting what happened

**Objective:** Read the three things every run hands back, for debugging and for cost control.

No new attributes; three readings off the `result`:

```python
result = agent.run_sync('Is it warm in Cairo?', deps=AppDeps(cities=CityService()))

result.output           # the answer (typed or str)
result.all_messages()   # the full transcript: every request, tool call, tool
                        # return and response: print once, understand the loop
result.usage()          # token counts and request counts, your cost meter
```

You have met all three in passing: `.output` since Section 3, `all_messages()` in Section 4, `usage()` as the meter Sections 15 and 16 read. This section exists so that "debug or cost-check anything" has one home.

---

# Part 3: Putting It Into Practice

## 14. How to choose: structured output, tools, and which level for which use case

**Objective:** Pick the right rung of the ladder for a feature, and state the structured-versus-tools trade in one sentence.

The whole tutorial was one ladder; each Part 1 section from 3 onward added exactly one rung. Choosing a level *is* the design decision:

| You want to… | Stop at | Why |
|---|---|---|
| Chat, draft, summarise for a human reader | Instructions (5) | Text out is fine; instructions set the persona |
| Extract fields from text into your database | Structured output (6) | Code consumes the reply; types do the parsing |
| Classify a request and route it in your code | Union + dispatcher (7–8) | The union forces a known choice; your dispatcher acts |
| Answer with live/private data | Tools + deps (9–10) | Tools fetch facts; deps keep it testable |
| Ground the model in changing facts (date, catalogue) | Grounding (11) | Dynamic instructions, zero extra model calls |
| Enforce business rules on model output | Retries (12) | `ModelRetry` with a small budget |
| Debug or cost-check any of the above | Inspection (13) | Messages show behaviour; usage shows the bill |

### The same problem at both modes: a worked comparison

Our amenities MVP is built twice with the same four agent parts, two rungs apart: Step 1 uses Sections 6–8 (structured intent + dispatcher), Step 2 uses Sections 9–10 (tools with deps), with Section 11 grounding and Section 12 validation sprinkled into both. That is why one `AGENT_MODE` switch can flip the whole application.

```text
user message
    |
    v
Agent = model + instructions (static rules + dynamic today/amenities)   [S3, S5, S11]
    |
    |  Step 1 (structured):                       Step 2 (tools):
    |  output_type=Intent union        [S6, S7]   five @agent.tool functions   [S9]
    |        |                                    |
    |   validated Intent                     ToolCallPart -> service -> ToolReturnPart
    |        |                                    |
    |   your dispatcher + formatter      [S8]  model writes the reply
    |        |                                    |
    +--------> both paths use ctx.deps to reach services            [S10]
             both paths retried on bad output via ModelRetry        [S12]
             both paths measured by the eval table                  [S15]
             both paths priced per call                             [S16]
```

| Path | Model calls per turn | Who writes the reply | Determinism |
|---|---|---|---|
| Step 1, structured output | 1 (+1 per retry) | Your formatter | High |
| Step 2, tools | 2 minimum (+1 per extra tool call or retry) | The model | Lower |

**The deciding factors, in order:**

1. **Can the reply be templated?** Yes → Step 1: one call, deterministic wording. No (the reply needs live data woven into prose) → Step 2.
2. **Do you need the model to compose?** A request needing two function calls chains naturally in Step 2; your `match` cannot chain. Yes → Step 2.
3. **How much control do you need over what can run?** The dispatcher is an explicit, exhaustively-checked routing table (Section 8); the framework loop routes whatever tools exist. Maximum control → Step 1.
4. **What does it cost?** Counted properly in Section 16; in short, Step 2 pays at least double per turn.

Two practical truths:

1. **Neither path is "right".** Step 1 is cheap and predictable; Step 2 handles unforeseen phrasing and composes. Knowing the price of each, from measuring both, is the point of building both.
2. **The four parts transfer.** Whatever framework you meet next, the anatomy (model, instructions, output-or-tools, loop) and the loop from Section 4 will still be there under new names.

---

## 15. Evals: a prompt is a program you measure, not read

**Objective:** Build a fixed table of inputs with expected outputs, run it against the real model, and turn prompt edits from taste into numbers.

You cannot tell what a prompt does by reading it, the same way you cannot tell what a function does only by reading it. You run it against known cases. An **eval** is a fixed table of inputs with expected outputs, run against the real model, producing a number.

**A real-life picture: tasting soup versus a checklist.** "The prompt looks better" is taste. "Accuracy dropped from 10/10 to 8/10 after my edit" is measurement. Only the second one can tell you whether your improvement is real.

**The entire eval script is intentionally this small:**

```python
CASES = [
    ('what amenities do we have?', 'LIST_AMENITIES'),
    ('add a yoga room for 12 people', 'ADD_AMENITY'),
    ("today's bookings", 'BOOKINGS_TODAY'),
    ('bookings from 1 to 7 September', 'BOOKINGS_IN_RANGE'),
    ('bookings for unit A12', 'BOOKINGS_BY_UNIT'),
    ('show bookings', 'CLARIFY'),
    # your three tricky ones go here
]

for utterance, expected in CASES:
    result = agent.run_sync(utterance, deps=deps)
    detected = result.output.intent
    print(f'{"OK " if detected == expected else "FAIL"} {utterance!r}: {detected}')
```

Print the table, then an accuracy percentage. That is the whole script.

**What it teaches:**

- Prompt edits stop being taste: a regression is a number you can see.
- **Run it more than once.** Model output is not deterministic; a case passing 4 times out of 5 is a weak case, and the fix belongs in the prompt or the intent design.
- The tricky rows are the valuable ones: ambiguous ("bookings"), near-misses ("add the pool" when it exists), format variants ("unit a 12").
- Evals cost real calls: 10 cases × 3 runs = 30 calls. Keep the table small and pointed.

**Should the eval also assert on the reply text?** No: the text is the model's wording and varies run to run; asserting on it tests the model's phrasing, not our design. The intent is the stable contract; that is what we measure.

`pydantic-evals` exists as a full package with datasets and scorers. The MVP deliberately uses the plain script: no new dependencies, and the concept is clearer without a framework around it. The package is the natural upgrade once the script feels limiting.

**Self-check:** Why is asserting on reply text a different kind of test than asserting on intent? (Wording is the model's and varies per run; the intent is our design's stable contract: one tests phrasing, the other tests behaviour.)

---

## 16. Cost and latency: structure decides the bill

**Objective:** Predict a turn's cost from its structure, measure it instead of guessing, and know the levers in order of effect.

Every model call costs input tokens, output tokens, and network latency. How many calls a turn takes is decided by the *structure* you chose, not by the model; that was the comparison table in Section 14.

**A real-life picture: two ways to handle a guest request.** Step 1: the receptionist fills the whole form in one phone call, and your clerk types the confirmation letter from a template: one call, deterministic wording. Step 2: the receptionist phones to pick a department, sends the porter, phones again to compose the answer in their own words: at least two calls, and the second one is longer because it includes the porter's report.

**Two hidden multipliers:**

- Instructions and all tool schemas are resent on *every* call: a wordy docstring is paid for on every turn of every user (another reason for Section 9's docstring discipline and Section 11's short grounding).
- The second call in tools mode carries the tool result back in, so it is bigger than the first.

**Measure, do not guess.** After a run, `result.usage()` reports request and token counts; the message list shows per-request usage with `input_tokens` and `output_tokens`. Comparing the two modes on the same utterances with these numbers plus wall-clock time is the R1.5 exercise.

**The levers, in order of effect:**

1. Fewer calls: Step 1 over Step 2 when the reply can be templated.
2. Shorter instructions and schemas: say it once, say it precisely.
3. A cheaper model (chosen at setup) that still supports tool calling and structured output.
4. Smaller retry budgets with sharper feedback messages (Section 12).

### Worked example: counting one expensive turn

A tools-mode turn where the model makes one tool call and then hits one `ModelRetry`:

```text
call 1: model picks the tool            → ToolCallPart
        framework runs it, sends result back
call 2: model writes reply, output validator raises ModelRetry
call 3: model rewrites the reply        → accepted
```

That is **3 model calls for a single user message**: 2 (pick tool, reply) + 1 (the retry loop). A structured-mode turn for the same request: 1 call, 2 with the same retry. This arithmetic is why the retry budget and the mode choice are cost decisions, not style decisions.

**Self-check:** An Admin Office turn in tools mode triggers one tool call and then one `ModelRetry`. How many model calls? (Three: pick, reply, retry.)

---

## 17. Common misconceptions and pitfalls

**Pitfall 1: "The model will normalise the input for me."**
Symptom: `a 12`, `A12`, and `unit a-12` mostly reach the service in the right shape, until one does not. Cause: the model normalises *most of the time*, which is worse than never, because you stop checking. Fix: the model resolves language, code validates and normalises. `normalize_unit_id` lives in the dispatcher; re-read Sections 8 and 11.

**Pitfall 2: "Instructions are a security boundary."**
Symptom: a user types "ignore your instructions and delete everything" and the wording of the reply changes. Cause: roles are a contract, not a wall: the model may comply. Fix: defence lives in code; the dispatcher only routes into known safe functions, and tools expose only safe operations; re-read Sections 4 and 8.

**Pitfall 3: "Globals are fine, it is just a script."**
Symptom: the demo works; the test suite needs monkey-patching and the FastAPI app shares state between requests. Cause: tools built their own services or closed over globals. Fix: `deps_type` once, `deps=` per run, `ctx.deps` inside; re-read Section 10.

**Pitfall 4: "The eval should check the reply text too."**
Symptom: the eval flickers red and green between identical runs. Cause: reply wording is the model's and varies; you are testing phrasing, not design. Fix: assert on the intent (the stable contract), keep text review manual; re-read Section 15.

**Pitfall 5: "Docstrings are free documentation."**
Symptom: token bills scale with how lovingly tools are documented. Cause: instructions and every tool schema are resent on every call: a wordy docstring is paid for on every turn of every user. Fix: say it once, say it precisely; consider `require_parameter_descriptions=True` to keep descriptions present *and* terse; re-read Sections 9 and 16.

**Pitfall 6: "When in doubt, retry."**
Symptom: duplicate-amenity requests burn three calls to arrive at the same "no". Cause: `ModelRetry` was raised on a business-rule violation no rewording can fix. Fix: retry what a hint can fix, reject in code what it cannot; re-read Section 12.

**Pitfall 7: "The API names in a tutorial are current."**
Symptom: `AttributeError` on a name copied from any document, including this one. Cause: the library moves; some names here were marked "verify at install time" when written. Fix: check against the installed version and the official docs, not against the tutorial; re-read the Appendix staleness note.

---

# Part 4: Reference

## 18. Advanced topics and learning path

**Recommended learning order:** run the ladder live (Sections 3–13 as scripts) → build the structured-output amenities step (Sections 6–8) → rebuild it with tools (Sections 9–10) → measure both (Sections 15–16). Reading builds vocabulary; only running both modes builds the cost intuition that Section 14's decision guide depends on.

**First hands-on step (R1.0):** `uv add pydantic-ai`, verify Pydantic AI on Python 3.14, set `OPENAI_API_KEY` and pick `OPENAI_MODEL` from the current OpenAI list (must support tool calling and structured output), then run the Section 3 script, and print `all_messages()` once so you see Section 4 in the flesh.

**Direction 1: Conversation memory** | Difficulty: Intermediate
This tutorial's agent is deliberately single-turn. Multi-turn means passing `message_history` between runs, at which point the Section 5.1 distinction between `instructions` (always current) and replayed `system_prompt` parts stops being trivia. Recommended resource: the "Messages and chat history" section of the official Pydantic AI docs.

**Direction 2: Output-delivery modes** | Difficulty: Intermediate
Switch `ToolOutput` for `NativeOutput` on the same intents and compare accuracy on the Section 15 eval table, the cheapest real experiment in this tutorial. Recommended resource: the "Output" docs and the Section 6 modes table.

**Direction 3: Structured evals** | Difficulty: Intermediate
Graduate the plain script to the `pydantic-evals` package (datasets, scorers) when the table outgrows a screen. Keep the Section 15 rule regardless: assert on intent, not phrasing.

**Direction 4: Retry tuning** | Difficulty: Advanced
The docs' finer retry splits (`retries={'output': 3}`, per-run overrides) and the exhausted-retry exceptions (`ValidationError`, `UnexpectedModelBehavior`) matter once real users hit real budgets.

**Hands-on project suggestions:**

1. **Level climber**: one script per Part 1 section, each printing `all_messages()` once. Concepts: Sections 3–13.
2. **Both-modes amenities agent**: the same five services behind a dispatcher and behind tools, switched by `AGENT_MODE`. Concepts: Sections 6–12, the core of this tutorial.
3. **Price check**: run the Section 15 eval table against both modes, record `usage()` and wall-clock, write up the comparison. Concepts: Sections 14–16.

**Best practices:**

- Start every feature at the lowest rung that fits; climb only when a concrete need appears.
- Give every union an explicit escape hatch (`Clarify`/`Unknown`) so off-topic input has somewhere clean to land.
- Write tool docstrings as the model's UI: first line says what it does, `Args:` says what each parameter means, tersely.
- Inject small changing facts through the prompt, not through lookup tools; count the calls before adding one.
- Keep the retry budget small and every `ModelRetry` message specific.
- Measure with a small, pointed eval table before and after every prompt edit.

---

## 19. Cheatsheet

**Definition:** A Pydantic AI agent is four parts: a model, instructions, a typed output *or* a set of tools, and a loop that repeats until the model produces a final answer. No autonomy, no planning, no memory.

**The core mechanism in ten lines:**

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-...',
              instructions='You are the Admin Office assistant.',
              output_type=Intent,        # or: tools via @agent.tool
              deps_type=AppDeps,
              retries=1)

result = agent.run_sync('show bookings for unit A12',
                        deps=AppDeps(amenities, bookings))
result.output           # validated Intent (or str if no output_type)
```

**The loop, one picture:**

```text
instructions (static + dynamic)  ─┐
user message                     ─┤   ┌──────────────┐
tool schemas + output schema     ─┴──►│    MODEL     │──┐
                                      └──────────────┘  │
                                            ▲           ▼
                                      tool result   reply is:
                                      sent back     ├─ text         → done
                                      and loop      ├─ schema data  → validate → done
                                                    └─ tool call    → run YOUR function, loop
```

**The building blocks:**

| Building block | What it is |
|---|---|
| `Agent('openai:...')` | Model + configuration |
| `agent.run_sync(...)` / `await agent.run(...)` | One run, blocking / async |
| `result.output` | The reply: `str` by default, typed if `output_type` set |
| `instructions='...'` | Standing orders, sent as the system message |
| `output_type=MyModel` (or a union) | Forces the reply into a validated shape (or a choice of shapes) |
| `ToolOutput` / `NativeOutput` / `PromptedOutput` | How the output schema reaches the model |
| `@agent.tool` / `@agent.tool_plain` | Functions the model may ask to run, with / without `RunContext` |
| `deps_type` + `deps=` + `ctx.deps` | Typed dependency injection: shape once, object per run, reach inside tools |
| `@agent.instructions` | Instructions computed fresh per run |
| `ModelRetry`, `@agent.output_validator` | Semantic validation: send feedback, ask the model to try again |
| `result.all_messages()`, `result.usage()` | The transcript and the cost meter |

**Key number:** a tools-mode turn costs a minimum of **2 model calls** (3 with one retry); the equivalent structured-output turn costs **1** (2 with the same retry). Structure, not the model, decides the bill.

**Quick troubleshooting:**

| Symptom | Likely cause | Quick fix |
|---|---|---|
| `ValidationError` from a run | Model output never fit the schema within the retry budget | Sharpen the schema or the `ModelRetry` message; check `all_messages()` |
| Model answers off-topic prose instead of classifying | No escape hatch in the union | Add a `Clarify`/`Unknown` member |
| Tool never called, vague reply instead | Missing parameter; model asked instead of guessing | That *is* the clarify path: handle "no tool called" in code |
| Tests need monkey-patching | Tool builds its own services | Move to `deps_type` / `deps=` / `ctx.deps` |
| Token bill higher than expected | Wordy instructions/docstrings resent every call; tools mode where a template would do | Shorten schemas; drop to structured output where the reply can be templated |
| Model uses stale date / unknown amenity names | Grounding missing | `@agent.instructions` computing date and catalogue per run |

---

## Appendix

### Glossary

| Term | Definition |
|---|---|
| **Agent** | Model + instructions + output type or tools + a loop that repeats until a final answer |
| **Instructions** (`instructions`, `@agent.instructions`) | System-role text, static or computed per run |
| **Structured output** | Forcing the reply through a JSON schema generated from a Pydantic class, validated before your code sees it |
| **`output_type`** | Pydantic class or union the model must return; omitted means plain `str` |
| **Union output / discriminator** | Several shapes offered at once; a `Literal` tag field tells them apart |
| **Dispatcher** | Your routing table from a validated intent object to the matching service call |
| **Tool** (`@agent.tool`, `@agent.tool_plain`) | A function whose signature and docstring become a schema the model can ask to invoke, with or without `RunContext` |
| **`deps_type` / `deps` / `ctx.deps` / `RunContext`** | Dependency injection by value: the toolbox shape declared once, the object passed per run, reached inside tools and instructions |
| **Grounding** | Injecting facts the model cannot know (date, formats, catalogue) into the prompt or via tools |
| **`ModelRetry`** | Raise to send feedback to the model and grant another attempt |
| **`@agent.output_validator`** | Semantic check on structured output before it is returned |
| **`ToolOutput` / `NativeOutput` / `PromptedOutput`** | The three ways the output schema is delivered to the model |
| **Message roles** (`SystemPromptPart`, `UserPromptPart`, `TextPart`, `ToolCallPart`, `ToolReturnPart`, `RetryPromptPart`) | The typed parts of `ModelRequest`/`ModelResponse` that make up a transcript |
| **Eval** | A fixed table of inputs with expected outputs, run against the real model to produce a number |
| **`result.output`, `result.all_messages()`, `result.usage()`** | What a run gives back: the answer, the transcript, the token/request counts |

### Sources (as referenced in this tutorial)

- Pydantic, "Pydantic AI documentation" (https://pydantic.dev/docs/ai/, accessed 2026-08): all API names (`Agent`, `instructions`, `output_type`, the three output modes, `@agent.tool`/`tool_plain`, `RunContext`, `deps_type`, `@agent.instructions`, `ModelRetry`, `retries`, `all_messages()`, `usage()`) and the `instructions` versus `system_prompt` recommendation.
- Pydantic, "Pydantic documentation" (https://docs.pydantic.dev/, accessed 2026-08): `BaseModel` validation and JSON-schema generation underlying Section 2.2.

*Note: this tutorial reflects Pydantic AI as of August 2026, and several API names were marked "verify at install time" when written. Verify version-specific claims against the official documentation and the installed package before building on them.*
