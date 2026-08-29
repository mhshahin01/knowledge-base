# Python Basics, Extracted From a Pydantic AI Intent Router

> Last updated: 2026-08-29 | Verified against: Python 3.14.3
> Source files: [`agent-single-intent.py`](agent-single-intent.py) and
> [`agent-multi-intents.py`](agent-multi-intents.py), both in this folder

Every Python language concept used by those two files, listed once and then explained in full.
The AI framework parts (`Agent`, `output_type`, `run_sync`) are covered in this exercise's
[README](README.md); this note is about the *language*, and touches Pydantic only where it explains
why a Python feature was chosen.

Both files are near-identical in structure. `agent-single-intent.py` is the smaller vocabulary;
`agent-multi-intents.py` adds exceptions, tuples, loops and a sentinel value. The **File** column
below tells you which one introduces each concept.

---

## Index

| # | Concept | File | Since |
| --- | --- | --- | --- |
| 1 | [Module docstring](#1-module-docstring) | both | 1.0 |
| 2 | [Module-level code runs at import](#2-module-level-code-runs-at-import) | both | 1.0 |
| 3 | [`import x` vs `from x import y`](#3-import-x-vs-from-x-import-y) | both | 1.0 |
| 4 | [Conditional and deferred imports](#4-conditional-and-deferred-imports) | both | 1.0 |
| 5 | [Import-time side effects (`load_dotenv()`)](#5-import-time-side-effects-load_dotenv) | both | - |
| 6 | [`os.getenv()` and the `None` return](#6-osgetenv-and-the-none-return) | both | 1.0 |
| 7 | [Truthiness](#7-truthiness) | both | 1.0 |
| 8 | [Naming conventions](#8-naming-conventions) | both | PEP 8 |
| 9 | [Dynamic typing: one name, two types](#9-dynamic-typing-one-name-two-types) | both | 1.0 |
| 10 | [Variable annotations (PEP 526)](#10-variable-annotations-pep-526) | both | 3.6 |
| 11 | [`Literal[...]`](#11-literal) | both | 3.8 |
| 12 | [`Union[...]` and the `\|` operator](#12-union-and-the--operator) | both | 3.5 / 3.10 |
| 13 | [Type aliases](#13-type-aliases) | both | 1.0 |
| 14 | [Builtin generics (PEP 585)](#14-builtin-generics-pep-585) | multi | 3.9 |
| 15 | [`int \| None` as "optional"](#15-int--none-as-optional) | multi | 3.10 |
| 16 | [Class definition and inheritance](#16-class-definition-and-inheritance) | both | 1.0 |
| 17 | [Class docstrings are runtime data](#17-class-docstrings-are-runtime-data) | both | 1.0 |
| 18 | [A class body of annotations only](#18-a-class-body-of-annotations-only) | both | 3.6 |
| 19 | [Function definitions and signature annotations](#19-function-definitions-and-signature-annotations) | both | 3.0 |
| 20 | [Function docstrings](#20-function-docstrings) | both | 1.0 |
| 21 | [`return` and multiple exit points](#21-return-and-multiple-exit-points-guard-clauses) | both | 1.0 |
| 22 | [Returning a tuple, and tuple unpacking](#22-returning-a-tuple-and-tuple-unpacking) | multi | 1.0 |
| 23 | [f-strings](#23-f-strings) | both | 3.6 |
| 24 | [`str.join()`](#24-strjoin) | both | 1.0 |
| 25 | [`str.split()` with no argument](#25-strsplit-with-no-argument) | both | 1.0 |
| 26 | [String concatenation with `+`](#26-string-concatenation-with-) | both | 1.0 |
| 27 | [Implicit string literal concatenation](#27-implicit-string-literal-concatenation) | both | 1.0 |
| 28 | [`len()` and the sequence protocol](#28-len-and-the-sequence-protocol) | both | 1.0 |
| 29 | [`isinstance()` and runtime dispatch](#29-isinstance-and-runtime-dispatch) | both | 1.0 |
| 30 | [Attribute access and method chaining](#30-attribute-access-and-method-chaining) | both | 1.0 |
| 31 | [`==` vs `is`](#31--vs-is) | multi | 1.0 |
| 32 | [Sentinel constants](#32-sentinel-constants) | multi | - |
| 33 | [`for` loops and `enumerate(..., start=1)`](#33-for-loops-and-enumerate-start1) | multi | 2.6 |
| 34 | [Generator expressions and `any()`](#34-generator-expressions-and-any) | multi | 2.5 |
| 35 | [`list.append()` and building output](#35-listappend-and-building-output) | multi | 1.0 |
| 36 | [Conditional expressions (the ternary)](#36-conditional-expressions-the-ternary) | multi | 2.5 |
| 37 | [Custom exception classes](#37-custom-exception-classes) | multi | 1.0 |
| 38 | [`raise`, and exceptions crossing call frames](#38-raise-and-exceptions-crossing-call-frames) | multi | 1.0 |
| 39 | [`try` / `except ... as`](#39-try--except--as) | multi | 1.0 |
| 40 | [`str(exception)` returns the message](#40-strexception-returns-the-message) | multi | 1.0 |
| 41 | [Keyword arguments](#41-keyword-arguments) | both | 1.0 |
| 42 | [`if __name__` is absent here, and why](#42-if-__name__-is-absent-here-and-why) | both | 1.0 |

---

## 1. Module docstring

```python
"""agent.py - intent routing with the scope guard ENFORCED in code.
...
"""
import os
```

A string literal as the **very first statement** of a file is the module docstring. It is not a
comment: Python evaluates it and binds it to `module.__doc__`, so `help(module)` and tooling can
read it.

The "first statement" rule is strict. A blank line or comment before it is fine, but any executable
statement (even `import os`) before the string demotes it to a plain, discarded expression.

```python
import agent_single_intent as m
print(m.__doc__)                    # the whole text
print(m.__doc__.splitlines()[0])    # the summary line
```

**Why here:** both files open with several paragraphs explaining *why* the design is what it is, and
how the file relates to its sibling. That is exactly the docstring's job. Notice the convention of a
one-line summary, a blank line, then the detail.

---

## 2. Module-level code runs at import

There is no `main()` in either agent file. Everything at zero indentation executes top to bottom the
first time the module is imported:

```python
load_dotenv()                       # runs
if os.getenv("OPENAI_API_KEY"):     # runs
    MODEL = "openai:gpt-5"
    print("Using real model")       # prints, at import time
class AddNumbers(BaseModel): ...    # the class statement runs, creating the class object
router = Agent(MODEL, ...)          # an Agent object is constructed
```

A `class` statement is not a declaration processed ahead of time. It is a runtime statement that
executes the class body and binds the resulting class object to the name. The same is true of `def`.

The module is cached in `sys.modules`, so a second `import` does **not** re-run any of it.

**Gotcha:** because `print("Using real model")` sits at module level, importing the file prints. That
is fine for a teaching script and wrong for a library. In library code, side-effecting work belongs
inside a function or behind `if __name__ == "__main__":`.

---

## 3. `import x` vs `from x import y`

```python
import os                                   # binds the name `os`
from typing import Literal, Union           # binds `Literal` and `Union`
from dotenv import load_dotenv              # binds the function itself
from pydantic import BaseModel
from pydantic_ai import Agent
```

`import os` binds one name, and you reach through it: `os.getenv`. `from typing import Literal`
copies a reference to the object into your module namespace; `typing` itself is never bound.

Practical differences:

| | `import os` | `from os import getenv` |
| --- | --- | --- |
| Call site | `os.getenv(...)` | `getenv(...)` |
| Origin visible at call site | yes | no |
| Namespace collisions | unlikely | likely (`Agent`, `BaseModel` are generic words) |
| Monkeypatching in tests | patch `os.getenv`, all callers see it | your local copy is already bound |

**Why here:** `os` is used once, so the qualified form costs nothing and documents itself. The typing
names are used many times in annotations, where `typing.Literal["add_numbers"]` would be noise.

---

## 4. Conditional and deferred imports

```python
if os.getenv("OPENAI_API_KEY"):
    MODEL = "openai:gpt-5"
    print("Using real model")
else:
    from pydantic_ai.models.test import TestModel
    MODEL = TestModel()
```

`import` is a statement, so it is legal anywhere a statement is: inside an `if`, inside a function,
inside a method. PEP 8 asks for imports at the top of the file, and this is one of the accepted
exceptions.

Two things are happening:

1. **Deferral.** `TestModel` is only imported when there is no API key. If the test-model module were
   slow or had heavy dependencies, real-key runs would not pay for it.
2. **Scoping.** The name `TestModel` only exists on the `else` branch's execution path. Because this
   is module level (not inside a function), it still lands in the module namespace, so
   `agent_module.TestModel` exists after a keyless import and does not after a keyed one. Inside a
   function, the binding would be local and vanish on return.

**Gotcha:** a conditional import at module level makes the module's public surface depend on the
environment. Static analysers and IDEs often flag `TestModel` as possibly-unbound. Acceptable in a
teaching script; in production, import unconditionally and branch only on the value.

---

## 5. Import-time side effects (`load_dotenv()`)

```python
from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel
from pydantic_ai import Agent
```

Look at the ordering: a **function call sandwiched between imports**. That is deliberate, and it is
the one place where the usual "all imports first" rule is actively harmful.

`load_dotenv()` reads a `.env` file and pushes its keys into `os.environ`. Some libraries read
configuration from the environment *while being imported*. If `from pydantic_ai import Agent` ran
first, it could snapshot an environment that has not been populated yet.

The same reasoning drives the `os.getenv` check below it: by the time that line runs, `.env` has
already been merged into the process environment.

**Gotcha:** linters (ruff `E402`, flake8 `E402`) will flag "module level import not at top of file"
on the two imports after the call. The usual fix is a targeted `# noqa: E402`, not reordering.

---

## 6. `os.getenv()` and the `None` return

```python
if os.getenv("OPENAI_API_KEY"):
```

`os.environ` is a dict-like mapping of the process environment. `os.environ["MISSING"]` raises
`KeyError`. `os.getenv("MISSING")` returns `None` instead, and `os.getenv("MISSING", "fallback")`
returns the default.

Everything in the environment is a **string**. There are no ints, no bools. `os.getenv("DEBUG")` with
`DEBUG=false` in the shell gives you the truthy string `"false"`, which is a classic bug.

```python
os.getenv("PORT")                 # '8080', a str, not 8080
int(os.getenv("PORT", "8080"))    # the explicit conversion you need
```

**Why here:** the file wants "run against the real model if a key is configured, otherwise run
offline against a fake". Absence, not value, is the signal, so `getenv` plus a truthiness test is
exactly right.

---

## 7. Truthiness

Python's `if` accepts any object, not just `bool`. It calls `__bool__()`, falling back to
`__len__() != 0`, defaulting to `True`.

Falsy in these files:

| Expression | Falsy when |
| --- | --- |
| `os.getenv("OPENAI_API_KEY")` | key unset (`None`) **or set to the empty string** |
| `if not plan:` | `plan` is `[]` |

```python
if not plan:
    return refusal()
```

`not plan` is the idiomatic empty-list check. `if len(plan) == 0:` is equivalent and noisier;
`if plan == []:` works but couples you to the exact type.

**Gotcha:** truthiness conflates "empty" with "missing". `if not plan` cannot distinguish `[]` from
`None`. Here that is fine, because both mean "no plan to run". When the difference matters, test
explicitly with `if plan is None:`.

---

## 8. Naming conventions

PEP 8, and all four styles below appear in these files:

| Style | Meaning | In these files |
| --- | --- | --- |
| `UPPER_SNAKE` | module constant, not reassigned after setup | `MODEL`, `CAPABILITIES`, `PREV` |
| `PascalCase` | class, or a type alias standing in for a type | `AddNumbers`, `WordCount`, `OutOfScope`, `StepFailed`, `Intent`, `Operand` |
| `snake_case` | function, variable, parameter | `add_numbers`, `word_count`, `run_step`, `previous`, `lines` |
| `_leading_underscore` | private by convention | not used here |

Two of these carry real information beyond taste:

- `Intent` and `Operand` are `PascalCase` despite being plain assignments, because they are used in
  annotation position. That is the signal to a reader that they name a *type*, not a value.
- `CAPABILITIES` is a `list`, which is mutable. `UPPER_SNAKE` is a promise you make, not one Python
  enforces: nothing stops `CAPABILITIES.append(...)` at runtime. A `tuple` would enforce it.

---

## 9. Dynamic typing: one name, two types

```python
if os.getenv("OPENAI_API_KEY"):
    MODEL = "openai:gpt-5"     # a str
else:
    MODEL = TestModel()        # a TestModel instance
```

`MODEL` holds a `str` on one path and an object on the other. Python permits this: names are untyped
references, and the object carries the type.

This is only workable because the consumer accepts both. `Agent(...)` takes either a model string it
resolves internally, or a model instance directly. If it accepted only one, the branch would be a
latent `TypeError` on the other path.

```python
MODEL = "openai:gpt-5"
type(MODEL)          # <class 'str'>
MODEL = TestModel()
type(MODEL)          # <class 'TestModel'>
```

**Gotcha:** this is the pattern a type checker complains about first. Under mypy, `MODEL` is inferred
as the join of both branches. Annotating it explicitly (`MODEL: str | Model = ...`) is the fix when
you add checking.

---

## 10. Variable annotations (PEP 526)

```python
class AddNumbers(BaseModel):
    kind: Literal["add_numbers"]
    a: int
    b: int
```

`a: int` with **no `=`** is an annotation-only statement. It creates no attribute. It records the name
and its type in `__annotations__`:

```python
AddNumbers.__annotations__   # {'kind': Literal['add_numbers'], 'a': int, 'b': int}
hasattr(AddNumbers, 'a')     # False
```

Python itself does nothing further. It does not check types, allocate slots, or generate an
`__init__`. Annotations are inert metadata, and that inertness is precisely what makes them reusable:
`dataclasses`, `attrs`, `NamedTuple` and Pydantic all read `__annotations__` and build machinery from
it.

Annotations also work on locals, and the multi-intent file uses that too:

```python
lines: list[str] = []
previous: int | None = None
```

Here the annotation adds nothing at runtime (the value already determines the type), but it tells a
reader and a checker that `lines` will hold strings, and that `previous` is expected to become an
`int` later.

**Python 3.14 note:** as of PEP 649/749, annotations are evaluated **lazily**, on first access to
`__annotations__`, rather than eagerly while the class body runs. Reading them works as before; the
practical gain is that forward references no longer need to be quoted.

---

## 11. `Literal[...]`

```python
kind: Literal["add_numbers"]
```

`Literal` narrows a type to an exact set of *values*, not just a type. `Literal["add_numbers"]` means
"the string `add_numbers`, and no other string".

`Literal["a", "b"]` allows either. `Literal[1, "x", True]` mixes types. The members must be hashable
immutable literals (str, int, bool, bytes, None, enum members). `Literal[[1, 2]]` is illegal.

**Why here:** it is a **discriminator**. The three intent classes share a `kind` field whose literal
values differ, which lets a validator look at one field and know which class the payload is. That
turns the union into a tagged union: fast to validate and unambiguous, instead of "try each class
until one fits".

```python
Operand = Union[int, Literal["previous_result"]]
```

Same tool, different job: here it defines an enum-of-one alongside a real type, so an operand is "a
number, or the specific magic word".

**Gotcha:** the string appears twice in the multi-intent file, once as `Literal["previous_result"]` in
the type and once as `PREV = "previous_result"` for comparisons. Type checkers cannot see through a
constant inside `Literal[...]`, so `Literal[PREV]` is rejected by some of them. Duplication is the
usual accepted cost. See [32](#32-sentinel-constants).

---

## 12. `Union[...]` and the `|` operator

```python
Intent = Union[AddNumbers, WordCount, OutOfScope]
```

"A value of any one of these types." Three spellings, all valid in 3.14:

```python
Union[int, str]        # typing.Union, works on every version
int | str              # PEP 604, 3.10+, preferred in new code
Optional[int]          # exactly Union[int, None]
```

The `|` form is not just syntax sugar for annotations, it is a real runtime operator on types
returning a `types.UnionType`:

```python
int | None             # int | None
type(int | None)       # <class 'types.UnionType'>
```

**Why `Union[...]` and not `AddNumbers | WordCount | OutOfScope`?** Both work here. `Union` reads
slightly better when the alternatives are long class names on one line, and it is the form that
survives copy-paste into codebases still on 3.9. Note that the same file uses `int | None` in
[`resolve()`](#15-int--none-as-optional), so the two styles are mixed. Picking one and sticking to it
is the better habit.

**Order matters to Pydantic, not to Python.** `Union[A, B]` and `Union[B, A]` are the same type to the
language, but a validator walking a union may try them in order. The discriminator field
([11](#11-literal)) removes that ambiguity entirely.

---

## 13. Type aliases

```python
Intent = Union[AddNumbers, WordCount, OutOfScope]
Operand = Union[int, Literal["previous_result"]]
```

A type alias is just an assignment. There is no `alias` keyword and no magic. The name now refers to
the type object and can be used anywhere a type can:

```python
def run_step(intent: Intent, previous: int | None) -> tuple[str, int]: ...
router = Agent(MODEL, output_type=list[Intent], ...)
```

The value is single-point-of-truth. Adding a fourth intent class means editing `Intent` once, and
every signature and every `output_type` follows.

**Modern alternative:** since 3.12, `type Intent = Union[...]` (PEP 695) declares an alias explicitly
and evaluates it lazily. The plain-assignment form used here works on every version and is still the
most common in the wild.

**Gotcha:** because it is a plain assignment, nothing distinguishes a type alias from an ordinary
variable holding a type object. `PascalCase` naming is the only convention carrying that signal,
which is why `Intent` and `Operand` are capitalised.

---

## 14. Builtin generics (PEP 585)

```python
output_type=list[Intent]
def run_step(...) -> tuple[str, int]:
lines: list[str] = []
```

Since 3.9 the builtin containers are themselves subscriptable in annotations. Before that you needed
`from typing import List, Tuple, Dict` and wrote `List[Intent]`. Those `typing` aliases still work,
are deprecated, and should not appear in new code.

| Old | Current |
| --- | --- |
| `List[Intent]` | `list[Intent]` |
| `Tuple[str, int]` | `tuple[str, int]` |
| `Dict[str, int]` | `dict[str, int]` |
| `Optional[int]` | `int \| None` |
| `Union[A, B]` | `A \| B` |

Two shapes of `tuple` worth distinguishing:

```python
tuple[str, int]    # exactly two items: a str then an int (a record)
tuple[str, ...]    # any number of strs (a homogeneous sequence)
```

`run_step` returns the first: a fixed-shape pair of "line to print" and "number to carry forward".

`list[Intent]` is doing real work in `output_type`. It is the entire difference between the two
files: widening the output type from one intent to a list of intents is what turns a classifier into
a planner.

---

## 15. `int | None` as "optional"

```python
def resolve(operand: Operand, previous: int | None) -> int:
def run_step(intent: Intent, previous: int | None) -> tuple[str, int]:
previous: int | None = None
```

`None` is a real value of a real type (`NoneType`), and `int | None` says the parameter is either an
int or that specific value. It is **not** the same as "this argument is optional": optionality is
about whether you may omit an argument, and is expressed with a default.

```python
def f(x: int | None):          # must be passed; may be None
def g(x: int = 0):             # may be omitted; never None
def h(x: int | None = None):   # may be omitted; may be None
```

**Why here:** `previous` models "the number the last step produced, if there was a last step". On the
first iteration there is no previous step, so `None` is the honest value. `0` would be a lie, because
`0` is a legitimate previous result, and code could not tell the two apart.

That is the payoff in `resolve`:

```python
if operand == PREV:
    if previous is None:
        raise StepFailed(dangling_reference())
    return previous
```

The `is None` check is what makes a dangling `"previous_result"` on step one detectable rather than
silently resolving to zero.

**Gotcha:** never test an `X | None` value with truthiness when `0` or `""` are valid values.
`if previous:` would treat a genuine previous result of `0` as "no previous result". `is None` is the
correct test.

---

## 16. Class definition and inheritance

```python
class AddNumbers(BaseModel):
    ...
class StepFailed(Exception):
    ...
```

`class Name(Base):` creates a class object at runtime and binds it to `Name`. The parentheses list
base classes; omitting them means inheriting `object`.

Both inheritances here are of the "borrow the machinery" kind:

- `BaseModel` supplies validation, `__init__`, `__eq__`, `__repr__`, `model_dump()` and JSON schema
  generation, all derived from the annotations in the body
  ([18](#18-a-class-body-of-annotations-only)).
- `Exception` supplies the raise/catch protocol. Deriving from it is what makes an object legal to
  `raise` and catchable by `except`.

You may subclass a subclass. `except Exception` catches `StepFailed` because inheritance defines the
catch hierarchy. That is why exception classes are arranged as trees.

---

## 17. Class docstrings are runtime data

```python
class AddNumbers(BaseModel):
    """The user wants two numbers added."""
    kind: Literal["add_numbers"]
```

Same mechanism as the module docstring: the first string in a class body becomes `__doc__`.

What makes these docstrings unusual is that they are **not only for humans**. Pydantic reads `__doc__`
and puts it into the JSON schema it generates as the description. That schema is what gets handed to
the language model. So this string is part of the prompt:

```python
class OutOfScope(BaseModel):
    """The request matches no supported intent."""
```

Rewriting that sentence changes how the model classifies. Compare with the multi-intent file, where
the docstrings were deliberately rewritten to describe chaining:

```python
class AddNumbers(BaseModel):
    """Add two numbers. Use "previous_result" for a value the step before produced."""
class WordCount(BaseModel):
    """Count the words in a piece of text. Produces a number later steps can use."""
```

**The general lesson:** a docstring is an attribute of a live object, not a comment. Anything can read
it, and here something does.

---

## 18. A class body of annotations only

```python
class WordCount(BaseModel):
    """The user wants the words in a piece of text counted."""
    kind: Literal["word_count"]
    text: str
```

No `__init__`, no `self`, no assignments, no methods. In plain Python this class would have nothing:
three annotations and a docstring produce a class with no attributes
([10](#10-variable-annotations-pep-526)).

`BaseModel`'s metaclass runs at class-creation time, reads `__annotations__`, and synthesises the
`__init__`, the validators and the schema. The same trick powers `@dataclass`.

The result is that the class body reads as a **declaration of shape**, which is the whole point in
these files: what a class *is* stays visible, because there is no constructor boilerplate between you
and the fields.

Three spellings, roughly equivalent in intent:

```python
class WordCount(BaseModel):        # validates at runtime, coerces, generates schema
    text: str

@dataclass
class WordCount:                   # generates __init__/__eq__/__repr__, no validation
    text: str

class WordCount:                   # you write everything
    def __init__(self, text: str):
        self.text = text
```

**Gotcha:** an annotation with a mutable default is a footgun in `@dataclass` (`x: list = []` is
rejected; you need `field(default_factory=list)`). Pydantic handles mutable defaults safely by
copying, but the habit of reaching for `default_factory` is worth keeping.

---

## 19. Function definitions and signature annotations

```python
def add_numbers(a: int, b: int) -> int:
    return a + b

def resolve(operand: Operand, previous: int | None) -> int:
def run_step(intent: Intent, previous: int | None) -> tuple[str, int]:
def refusal() -> str:
def handle(prompt: str) -> str:
```

`def` is a statement executed at runtime, creating a function object and binding it to the name.
Parameter annotations go after `:`, the return annotation after `->`.

**Annotations do not enforce anything.** `add_numbers("a", "b")` runs and returns `"ab"`, because `+`
is defined on `str`. The annotation is metadata stored on `__annotations__`, consumed by checkers
(mypy, pyright), editors, and libraries like Pydantic.

Their real value in these files is as **a contract at the boundary between model and code**. Once the
router hands back a validated `AddNumbers`, `intent.a` genuinely is an `int`, so
`add_numbers(a: int, b: int)` documents a guarantee that Pydantic already enforced upstream, rather
than an aspiration.

`refusal()` takes nothing and returns a fixed sentence. That is not a wasted function: it makes the
refusal text a single named thing that both files call from three places.

---

## 20. Function docstrings

```python
def handle(prompt: str) -> str:
    """Classify with the model, then dispatch in code."""

def resolve(operand: Operand, previous: int | None) -> int:
    """Turn one operand into a concrete number.

    This is where chaining actually happens: "previous_result" is not a value the
    model invented, it is a promise the code keeps by substituting the number the
    last step returned.
    """
```

Two useful patterns side by side.

`handle`'s is a one-liner: the signature already says "prompt in, string out", so the docstring adds
the *sequence*, which the signature cannot express.

`resolve`'s is the multi-paragraph form: summary line, blank line, then the part that matters, which
is not what the function does but **why it exists**. "The code keeps a promise the model made" is
design rationale, unrecoverable from reading the three-line body.

That is the split worth internalising: signatures document *what*, docstrings document *why*.

---

## 21. `return` and multiple exit points (guard clauses)

```python
def handle(prompt: str) -> str:
    intent = router.run_sync(prompt).output
    if isinstance(intent, AddNumbers):
        return f"{intent.a} + {intent.b} = {add_numbers(intent.a, intent.b)}"
    if isinstance(intent, WordCount):
        return f"{word_count(intent.text)} words"
    return refusal()
```

A function exits at the first `return` reached. There is no fallthrough between these `if`s because
each branch returns, which is why the code uses a sequence of `if`s rather than `if / elif / else`.
Both are correct; the flat form keeps nesting at one level and makes the final line read as "and
otherwise".

The final `return refusal()` is the important one. It is not an error path bolted on, it is the
**default**: anything that is not a recognised intent falls through to the code-owned refusal, so the
file cannot accidentally return `None` for an unhandled case.

A function that falls off the end without `return` returns `None` implicitly:

```python
def f(x):
    if x > 0:
        return "positive"
    # returns None for x <= 0

f(-1)   # None, not an error, which is exactly the bug that bites later
```

Neither file has that hole. Every path in `handle`, `run_step` and `resolve` either returns or raises.

---

## 22. Returning a tuple, and tuple unpacking

```python
def run_step(intent: Intent, previous: int | None) -> tuple[str, int]:
    ...
    return f"{a} + {b} = {total}", total
```

`return x, y` builds a tuple; the parentheses are optional, the comma is what creates it. The caller
takes it apart in one statement:

```python
line, previous = run_step(step, previous)
```

That is **unpacking**: the tuple's two items bind to two names positionally. It is how Python returns
"more than one thing" without an out-parameter or a wrapper class.

Notice `previous` appears on both sides of the loop's call. It is passed in as the carry from the last
step and rebound to this step's result, which is the mechanism that makes chaining work across
iterations.

Unpacking fails loudly on a length mismatch, which is a feature:

```python
a, b = (1, 2, 3)     # ValueError: too many values to unpack (expected 2)
a, b = (1,)          # ValueError: not enough values to unpack (expected 2, got 1)
```

**When to stop using tuples:** two items with obvious roles is fine. At three or four, positional
meaning gets lost and a `NamedTuple` or a small model is clearer. `tuple[str, int]` here is right at
the limit where it still reads.

---

## 23. f-strings

```python
f"{intent.a} + {intent.b} = {add_numbers(intent.a, intent.b)}"
f"{word_count(intent.text)} words"
f"{a} + {b} = {total}"
f"{count} words"
f"{position}. {line}"
```

An `f` prefix makes `{...}` an expression slot evaluated at runtime and rendered with `str()`.
Anything goes inside the braces, including full function calls, which the first example uses to
compute and format in one line.

Useful forms not in these files but worth knowing:

```python
f"{value!r}"          # repr() instead of str()
f"{ratio:.2f}"        # format spec: two decimals
f"{count=}"           # self-documenting: renders "count=5"
f"{'; '.join(items)}" # nested quotes had to differ, before 3.12
```

Since 3.12 (PEP 701) f-strings can reuse the same quote character inside and can contain backslashes,
so the old workarounds are gone in new code.

**Gotcha:** an f-string is evaluated **immediately**. That makes it wrong for logging templates
(`log.info(f"...")` formats even when the level is off; `log.info("%s", x)` defers) and dangerous for
SQL, where it produces injection. It is right here, because these strings are being built to return
straight away.

---

## 24. `str.join()`

```python
"; ".join(CAPABILITIES)
"\n".join(lines)
```

The separator is the string you call the method on, and the argument is the iterable of strings. It
reads backwards the first time and is the correct idiom.

Both uses are shaping user-facing output: `"; "` flattens the capability list into a sentence, `"\n"`
stacks numbered plan steps into a block.

```python
"; ".join(["add two numbers together", "count the words in a text"])
# 'add two numbers together; count the words in a text'
```

Two things it will not do:

```python
", ".join([1, 2, 3])                     # TypeError: sequence item 0: expected str instance
", ".join(str(n) for n in [1, 2, 3])     # '1, 2, 3'
```

**Why not `+` in a loop?** Building a string with `result += line` creates a new string object each
iteration, since strings are immutable. `join` allocates once. For the handful of lines here it makes
no measurable difference; the habit matters at scale.

---

## 25. `str.split()` with no argument

```python
def word_count(text: str) -> int:
    return len(text.split())
```

The whole word counter is one call, and the no-argument form is doing the work. `split()` with no
separator splits on **runs of any whitespace** and discards leading and trailing whitespace.
`split(" ")` splits on each single space literally and keeps the empties:

```python
"  a   b  ".split()       # ['a', 'b']
"  a   b  ".split(" ")    # ['', '', 'a', '', '', 'b', '', '']
"one\ttwo\nthree".split() # ['one', 'two', 'three']
```

So `word_count("  the   quick brown  ")` is `3`, not `8`. That is the behaviour you want for counting
words, and it is free.

Related: `.strip()` removes surrounding whitespace, `.splitlines()` splits on line boundaries,
`.split(",", maxsplit=1)` limits the number of splits.

**Honest limit:** "words" here means "whitespace-separated tokens". `"don't"` is one, `"a - b"` is
three, and CJK text without spaces counts as one. Fine for the exercise; say so out loud if such a
function ever ships.

---

## 26. String concatenation with `+`

```python
return "Sorry, I can't do that. I can: " + "; ".join(CAPABILITIES) + "."
```

`+` on two strings produces a new string. Chained `+` here glues a fixed prefix, a computed middle,
and a full stop.

This could equally be an f-string:

```python
return f"Sorry, I can't do that. I can: {'; '.join(CAPABILITIES)}."
```

Both are fine. `+` avoids nesting quotes inside braces (which mattered before 3.12) and keeps the
`join` visually separate. Personal preference; be consistent within a file.

`+` is only defined between strings:

```python
"count: " + 5        # TypeError: can only concatenate str (not "int") to str
"count: " + str(5)   # 'count: 5'
```

Note the apostrophe in `"Sorry, I can't do that."`: the literal uses double quotes precisely so the
`'` needs no escaping. Choosing the quote character to avoid escapes is standard practice.

---

## 27. Implicit string literal concatenation

```python
system_prompt=(
    "Break the user's request into an ordered list of intents, one per step. "
    "Most requests are a single step, so return a list of one. "
    'When a step needs a number the previous step produces, put "previous_result" '
    "in place of that number instead of guessing it. "
    "Return out_of_scope for any step that is not addition or word counting."
),
```

Adjacent string literals with nothing between them are joined **by the parser**, at compile time. No
`+`, no runtime cost. The wrapping parentheses are what allow it to span lines.

Two details visible above:

1. **The trailing spaces are load-bearing.** `"...one per step. "` ends with a space because the next
   literal starts immediately after it. Drop it and you get `step.Most`. This is the single most
   common bug with this pattern.
2. **Line three switches to single quotes** so that `"previous_result"` can keep its double quotes
   inside without escaping. Mixing quote styles deliberately is idiomatic.

**Gotcha:** the same rule silently merges strings in a list where a comma was forgotten:

```python
CAPABILITIES = [
    "add two numbers together"      # missing comma
    "count the words in a text",
]
# ['add two numbers togethercount the words in a text']  -- one item, no error
```

---

## 28. `len()` and the sequence protocol

```python
len(text.split())      # number of words
len(plan) > 1          # more than one step?
```

`len(x)` calls `x.__len__()`. It works on anything implementing it: `list`, `str`, `tuple`, `dict`,
`set`, and your own classes.

`len()` is a builtin function rather than a method because the protocol is uniform: one spelling for
every container. That is the same design as `str()`, `iter()` and `bool()`.

```python
len([1, 2, 3])         # 3
len("hello")           # 5  (characters, not bytes)
len({"a": 1})          # 1  (keys)
```

**Gotcha:** `len()` does not work on generators or arbitrary iterators, because they do not know their
size without being consumed. `len(x for x in range(3))` raises `TypeError`. That is relevant to
[34](#34-generator-expressions-and-any): the genexp passed to `any()` has no length, and needs none.

---

## 29. `isinstance()` and runtime dispatch

```python
if isinstance(intent, AddNumbers):
    ...
if isinstance(intent, WordCount):
    ...
return refusal()
```

`isinstance(obj, Class)` is a runtime check that returns `True` for the class **or any subclass**. It
is the mechanism that turns a static `Union` type into executable branching.

This is the hinge of the whole design. The model returns *one of three shapes*; the code asks *which
shape is this* and dispatches accordingly. Nothing the model says gets executed, only classified.

Type checkers understand `isinstance` as **narrowing**: inside the first branch, `intent` is known to
be `AddNumbers`, so `intent.a` type-checks. Outside it, `intent.a` would be an error, because
`WordCount` has no `a`.

```python
isinstance(True, int)          # True: bool subclasses int
type(True) is int              # False: exact type check
isinstance(x, (int, float))    # a tuple of classes means "any of these"
```

**Alternatives worth knowing:**

```python
match intent:                          # structural pattern matching, 3.10+
    case AddNumbers(a=a, b=b): ...
    case WordCount(text=text): ...
    case _: return refusal()

if intent.kind == "add_numbers":       # dispatch on the discriminator field
```

The `isinstance` chain was chosen here because it is the version a reader of any Python vintage
understands instantly, and because it works directly with the `Union` alias.

---

## 30. Attribute access and method chaining

```python
intent = router.run_sync(prompt).output
plan = router.run_sync(prompt).output
```

Read left to right: `router` is an object, `.run_sync` is a method looked up on it, `(prompt)` calls
it, the result is a result object, `.output` reads an attribute off that.

Chaining is fine while each link is meaningful. The line above is two links and reads as one sentence:
"run this synchronously, take the output". A five-link chain is where debugging becomes guesswork,
because a `None` anywhere in the middle produces an `AttributeError` that does not say which link
failed.

The parallel between the two files is worth noticing: the *expression is identical* in both, and the
type of what comes back differs (`Intent` vs `list[Intent]`) purely because `output_type` differs.
Same call, different contract.

`intent.a`, `intent.b`, `intent.text` and `intent.kind` are all plain attribute reads on the model
instance Pydantic built.

---

## 31. `==` vs `is`

Both appear in `resolve`, a few lines apart, and the choice is correct in each:

```python
if operand == PREV:        # value comparison
    if previous is None:   # identity comparison
```

`==` asks "are these equal", via `__eq__`. `is` asks "are these the same object in memory".

`operand == PREV` is right because `operand` is a string that arrived from JSON. It is a different
string object from the one `PREV` names, but it has the same characters, and characters are what
matter.

`previous is None` is right because `None` is a **singleton**: there is exactly one `None` object in a
Python process, so identity is the fastest and most precise test. `previous == None` would work but is
non-idiomatic and can be subverted by a class with a custom `__eq__`. PEP 8 says use `is`.

```python
a = "previous_result"
b = "previous" + "_result"
a == b       # True
a is b       # implementation-dependent; do not rely on it
```

**Rule:** `is` for `None`, `True`, `False` and other sentinels. `==` for everything else.

---

## 32. Sentinel constants

```python
PREV = "previous_result"
Operand = Union[int, Literal["previous_result"]]
...
if operand == PREV:
```

A magic string named once. The name explains at the comparison site what the literal means, and a typo
in `PREV` is a `NameError` at import while a typo in `"previous_reslt"` is a silent mismatch at
runtime.

The duplication between `PREV` and the string inside `Literal[...]` is the compromise noted in
[11](#11-literal): `Literal[PREV]` is not accepted by all type checkers, because `Literal` requires an
actual literal. Options if that bothers you:

```python
PREV: Final = "previous_result"        # typing.Final; some checkers then accept Literal[PREV]
class Prev(str, Enum):                 # heavier, gains exhaustiveness checking
    PREVIOUS = "previous_result"
```

For a teaching file, the plain constant plus the duplicated literal is the least distracting choice.

**The broader idea:** `"previous_result"` is a value in the *data* that means "look this up rather than
take it literally". That is a sentinel, and the same pattern shows up as `None` for absence, `-1` for
not-found, and `object()` for "argument genuinely not passed". Naming it is what keeps it from
becoming folklore.

---

## 33. `for` loops and `enumerate(..., start=1)`

```python
for position, step in enumerate(plan, start=1):
```

Three things at once.

**`for` iterates a sequence, not indices.** Python's `for` is a foreach. There is no counter to
initialise or bound to get wrong.

**`enumerate` pairs each item with a counter**, yielding `(index, item)` tuples lazily. `start=1`
shifts the counter, which is exactly right here because `position` is shown to a human
(`"1. 5 words"`), and humans count from one while Python counts from zero.

```python
list(enumerate(['x', 'y'], start=1))   # [(1, 'x'), (2, 'y')]
```

**The loop target unpacks the tuple**, so `position` and `step` bind in one step. Same mechanism as
[22](#22-returning-a-tuple-and-tuple-unpacking).

The anti-pattern this replaces:

```python
for i in range(len(plan)):        # do not
    step = plan[i]
    position = i + 1
```

**Scope gotcha:** loop variables leak. After the loop, `position` and `step` still exist, holding their
last values. If `plan` was empty they were never bound, and referencing them is a `NameError`. The
code avoids that by not touching them after the loop.

---

## 34. Generator expressions and `any()`

```python
if any(isinstance(step, OutOfScope) for step in plan):
    return refusal()
```

`isinstance(step, OutOfScope) for step in plan` is a **generator expression**: a lazy stream of
booleans, one produced per request, no list built.

`any()` consumes it and returns `True` at the **first** `True`, stopping there. That short-circuit is
why the genexp matters: on a plan whose first step is out of scope, exactly one `isinstance` runs.

```python
any(x > 2 for x in [1, 2, 3, 99])    # True, stops at 3
all(x > 0 for x in [1, 2, 3])        # True, the mirror of any()
any([])                              # False (nothing is true)
all([])                              # True (vacuously)
```

The bracketed version, `any([... for step in plan])`, builds the whole list first and evaluates every
element regardless. Same answer, more work. Dropping the brackets when the genexp is the sole argument
is both idiomatic and free.

**Why here specifically:** this is the all-or-nothing policy gate, and the comment above it says so.
The plan is scanned for any unsupported step *before* a single step executes, so a request is never
half-run. Checking upfront is only possible because the model returned the entire plan at once, which
is the multi-intent design's payoff.

---

## 35. `list.append()` and building output

```python
lines: list[str] = []
...
    lines.append(f"{position}. {line}" if len(plan) > 1 else line)
return "\n".join(lines)
```

The accumulate-then-join pattern: start with an empty list, append per iteration, join once at the end.

`append` mutates in place and returns `None`, which produces a classic bug:

```python
lines = lines.append("x")     # lines is now None
```

The annotation `lines: list[str]` on the empty literal is not decoration. `[]` alone tells a checker
nothing about what will go in it; the annotation states the intent before the first `append`.

**Why not a list comprehension?** Because the loop body can `return` early on `StepFailed`, and each
iteration feeds `previous` into the next. Comprehensions cannot break out and cannot carry state
between iterations. This is the case where an explicit loop is the right tool.

---

## 36. Conditional expressions (the ternary)

```python
lines.append(f"{position}. {line}" if len(plan) > 1 else line)
```

`A if condition else B` is an **expression**: it evaluates to a value and can go anywhere a value can,
including directly inside a call, as here. The condition sits in the middle, which is unusual among
languages and reads as "this, if that, otherwise the other".

It is a presentation rule expressed inline: number the lines only when there is more than one, so a
single-step answer reads `5 words` rather than `1. 5 words`.

`main.py` in the same folder uses the same form twice:

```python
intents = output if isinstance(output, list) else [output]
print(f"== {'multi' if multi else 'single'}-intent ==\n")
```

Only one branch is evaluated, so it short-circuits like `if`/`else`.

**Gotcha:** nested ternaries become unreadable fast (`a if p else b if q else c`). Two levels is the
practical limit; beyond that, use a real `if` block or a lookup dict.

---

## 37. Custom exception classes

```python
class StepFailed(Exception):
    """Carries a code-owned message explaining why the plan stopped."""
```

That is the entire class. A docstring as the body means no `pass` is needed, since a class body must
contain at least one statement and a string literal is one.

Defining your own exception type gives you a name to catch that is **exactly as narrow as the thing you
want to handle**. `except StepFailed` cannot accidentally swallow a `KeyError` or a `ConnectionError`
raised somewhere else in the call stack, which `except Exception` would.

```python
class StepFailed(Exception): pass                  # equivalent, less informative
class StepFailed(Exception):
    """Docstring."""                               # the form used here
class StepFailed(ValueError): ...                  # narrower parent, if callers might catch ValueError
```

**Why here:** it carries the refusal or dangling-reference message out of a nested helper without
threading a return value through every caller. The docstring names the invariant that makes the design
safe: the message is *code-owned*, never model-generated, which is the whole premise of the exercise.

Naming convention: exception classes end in `Error` when they signal a fault (`ValueError`,
`StepFailedError`). `StepFailed` reads as a state here and is defensible; `StepFailedError` would be
the more conventional spelling.

---

## 38. `raise`, and exceptions crossing call frames

```python
def resolve(operand, previous):
    if operand == PREV:
        if previous is None:
            raise StepFailed(dangling_reference())
        return previous
    return operand

def run_step(intent, previous):
    if isinstance(intent, AddNumbers):
        a = resolve(intent.a, previous)     # may raise, and does not catch
        ...
    raise StepFailed(refusal())
```

`raise Exc(args)` instantiates and throws. Control leaves the current function immediately and unwinds
outward until a matching `except` is found.

Trace the deep path: `handle` calls `run_step`, which calls `resolve`, which raises. `run_step` has no
`try`, so the exception passes straight through it and is caught in `handle`. **Intermediate frames do
not need to know.** That is the property that makes exceptions worth using over returning error codes,
which every layer would have to inspect and forward.

Note also that `run_step`'s final line is a `raise`, not a `return`. The function's annotation is
`-> tuple[str, int]`, and the unsupported case has no valid tuple to produce, so raising is more honest
than inventing one or returning `None`.

**When not to use exceptions:** for control flow that is ordinary rather than exceptional. Here the bar
is met: both raises mean "the plan cannot continue", which is genuinely the end of the operation.

---

## 39. `try` / `except ... as`

```python
try:
    line, previous = run_step(step, previous)
except StepFailed as stop:
    return str(stop)
```

The `try` block is deliberately **one line long**. Only the call that can raise sits inside it, so
nothing unrelated is caught by accident. Widening a `try` to wrap a whole function is the usual way
this goes wrong.

`as stop` binds the exception instance to a name. It is a real object: `stop.args`, `stop.__class__`
and its traceback are all available.

The full form, for reference:

```python
try:
    ...
except SomeError as e:
    ...          # handle
except (A, B):
    ...          # multiple types, no binding
else:
    ...          # ran only if no exception was raised
finally:
    ...          # always runs, exception or not
```

**Gotcha:** the `as` name is **deleted** when the `except` block ends, to break a reference cycle with
the traceback. Save what you need before leaving:

```python
try:
    ...
except StepFailed as stop:
    message = str(stop)
print(stop)      # NameError: name 'stop' is not defined
```

The code sidesteps this by returning from inside the block.

**Never write a bare `except:`.** It catches `KeyboardInterrupt` and `SystemExit` too, making the
program unkillable. If you must be broad, `except Exception:` is the floor.

---

## 40. `str(exception)` returns the message

```python
raise StepFailed(dangling_reference())
...
except StepFailed as stop:
    return str(stop)
```

`Exception.__init__` stores its positional arguments in `self.args`, and `__str__` renders them: with
exactly one argument it returns that argument as a string, with no class name or decoration.

```python
str(StepFailed("boom"))       # 'boom'
repr(StepFailed("boom"))      # "StepFailed('boom')"
StepFailed("boom").args       # ('boom',)
str(StepFailed())             # ''             (no args, empty string)
str(StepFailed("a", "b"))     # "('a', 'b')"   (multiple args, tuple repr)
```

So `str(stop)` here returns precisely the sentence `refusal()` or `dangling_reference()` produced,
ready to hand to the user.

That is the mechanism the design depends on. The exception is being used as a **message carrier**: the
code that knows *why* the plan stopped builds the sentence, throws it, and the code that owns the
user-facing return value unwraps it. No model text touches either end.

---

## 41. Keyword arguments

```python
router = Agent(
    MODEL,
    output_type=Intent,
    system_prompt=(
        "Classify the user's request into exactly one intent. "
        "If it is not addition or word counting, return out_of_scope."
    ),
)

enumerate(plan, start=1)
```

`MODEL` is positional; `output_type=` and `system_prompt=` are keyword arguments, matched by name
rather than position. Keywords may be given in any order and make the call self-documenting, which
matters most when the value alone is meaningless (`start=1`, `output_type=Intent`).

The trailing comma after the last argument is legal and conventional in a multi-line call: adding a
fourth argument later touches one line, so the diff shows one change.

Function definitions can require the distinction:

```python
def f(a, b, *, c):       # c must be passed by keyword
def f(a, /, b):          # a must be passed positionally
```

Neither file defines such a signature, but they consume libraries that do, which is why `output_type`
cannot be passed positionally to `Agent`.

---

## 42. `if __name__` is absent here, and why

Neither agent file has:

```python
if __name__ == "__main__":
```

`main.py` does. That split is the point.

`__name__` is a module-level string set to `"__main__"` when a file is run directly, and to the module
name when it is imported. Guarding your entry point with it is what makes a file both importable and
runnable.

The two agent files are **libraries**: they define `router`, `handle()` and the intent classes, and
running them directly does nothing visible. `main.py` is the **entry point**: it imports one of them,
loops over sample prompts, and prints. Keeping those roles apart means the agent files can be imported
by a test, a notebook, or the other script without triggering output.

The one leak from that rule is the `print("Using real model")` at module level, discussed in
[2](#2-module-level-code-runs-at-import).

---

## Gotchas, collected

| # | Gotcha | Right way |
| --- | --- | --- |
| 5 | Imports before `load_dotenv()` may snapshot an empty environment | call `load_dotenv()` before importing config-reading libraries; silence `E402` |
| 6 | Env vars are always `str`; `"false"` is truthy | convert explicitly with `int(...)`, or compare to known strings |
| 7 | `if not plan` cannot tell `[]` from `None` | `if plan is None` when the difference matters |
| 8 | `UPPER_SNAKE` does not make a list immutable | use a `tuple` if it must not change |
| 15 | `if previous:` treats a real result of `0` as absent | `if previous is None` |
| 19 | Annotations enforce nothing at runtime | run mypy/pyright, or validate with Pydantic |
| 21 | A function with no `return` on some path returns `None` silently | make every branch return or raise |
| 23 | f-strings evaluate immediately | `log.info("%s", x)` for logging; never f-string SQL |
| 24 | `join` on non-strings raises `TypeError` | `", ".join(str(x) for x in items)` |
| 25 | `split(" ")` keeps empty strings; `split()` does not | prefer bare `split()` for word splitting |
| 27 | A missing comma in a list of strings silently merges two items | check trailing spaces and commas in wrapped literals |
| 28 | `len()` does not work on generators | materialise with `list()` first, if you truly need the count |
| 29 | `isinstance(True, int)` is `True` | `type(x) is int` for exact checks |
| 31 | `== None` works but is wrong | `is None` |
| 33 | Loop variables leak after the loop, or never bind if it was empty | do not read them after the loop |
| 34 | `any([...])` evaluates every element | drop the brackets to keep the short-circuit |
| 35 | `list.append()` returns `None` | `lines.append(x)`, never `lines = lines.append(x)` |
| 39 | The `except ... as e` name is deleted after the block | save what you need inside the block |
| 39 | Bare `except:` swallows `KeyboardInterrupt` | `except Exception:` at the very widest |

---

## Concepts by file

**Only in `agent-single-intent.py`:** nothing. It is a strict subset.

**Added by `agent-multi-intents.py`:** builtin generics `list[X]` / `tuple[X, Y]` (14), `int | None`
(15), tuple return and unpacking (22), `==` vs `is` (31), sentinel constants (32), `for` + `enumerate`
(33), generator expressions + `any()` (34), `list.append` (35), conditional expressions (36), custom
exceptions (37), `raise` (38), `try` / `except ... as` (39), `str(exception)` (40).

That is the honest measure of what "return a list instead of one item" costs in language surface:
roughly a dozen more concepts, almost all of them about **sequencing and failure**, which is exactly
what a plan adds over a classification.

---

## Not covered here

`main.py` in the same folder uses `importlib.util.spec_from_file_location`, `pathlib.Path`,
`sys.argv`, `types.ModuleType`, a filtered list comprehension, and `if __name__ == "__main__":`. Those
are the dynamic-import and CLI-entry-point concepts, worth their own note.
