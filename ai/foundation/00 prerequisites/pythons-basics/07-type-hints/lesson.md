# Chunk 07: Type Hints

## Goal

By the end of this chunk, you will be able to:

- add type hints to variables and functions;
- describe lists and dictionaries;
- describe a value that may be `None`;
- create a reusable type alias;
- explain the difference between hints and validation.

## 1. Type hints describe expected data

A **type hint** states what kind of value is expected. It helps readers, editors, and type-checking tools understand your code.

For a variable, place a colon and the type after its name:

```python
learner_name: str = "Maya"
completed_lessons: int = 4
```

For a function, hint each parameter after its name and the returned value after `->`.

The first example says that `name` should be a string and that `build_greeting()` returns a string.

Run [01_basic_hints.py](examples/01_basic_hints.py).

Expected output:

```text
Welcome, Maya!
```

The hints do not change what the function does. They make its expectations visible.

## 2. Common function hints

These built-in types appear often:

| Hint | Expected value |
|---|---|
| `str` | text |
| `int` | a whole number |
| `float` | a number with a decimal part |
| `bool` | `True` or `False` |
| `None` | no returned value |

A function that performs an action without returning a useful value uses `-> None`.

The next example accepts a string and an integer, then displays the string repeatedly. Its `-> None` hint shows that displaying the result is the function's final action.

Run [02_function_hints.py](examples/02_function_hints.py).

Expected output:

```text
Python Python Python
```

## 3. Hinting collections

Put the item type inside square brackets to describe a collection:

- `list[str]` means a list of strings;
- `dict[str, int]` means a dictionary with string keys and integer values.

The next function accepts a list of prompts and returns their combined character count as an integer.

Run [03_collection_hints.py](examples/03_collection_hints.py).

Expected output:

```text
Total characters: 32
```

Modern Python uses built-in forms such as `list[str]`. Older material may show `List[str]` imported from `typing`.

## 4. A value may be `None`

Sometimes a function may return a value or may find nothing. The hint `str | None` means “a string or `None`.” The `|` symbol combines allowed types.

The next function searches for a model name. It returns the matching string when found and `None` otherwise. The calling code checks with `is None` before using the result.

Run [04_optional_value.py](examples/04_optional_value.py).

Expected output:

```text
Found: medium-model
Missing model: None
```

Do not use a truth check when `None` has a specific meaning and other false-like values, such as an empty string, may be valid.

## 5. Type aliases simplify repeated hints

A **type alias** gives a useful name to a longer type. Modern Python defines one with the `type` statement.

The final example names `dict[str, str]` as `Message`. Its functions can then use `Message` and `list[Message]` instead of repeating the longer forms.

Run [05_type_alias.py](examples/05_type_alias.py).

Expected output:

```text
SYSTEM: Answer briefly.
USER: Explain type hints.
```

The alias does not create a new runtime object. It gives a clearer name to an existing type description.

## 6. Hints are not runtime validation

Python normally does not reject an argument just because it disagrees with a type hint. Incorrect data may fail later or even produce a surprising result.

Type hints answer:

> What data does this code expect?

Runtime validation answers:

> Does this actual value follow the rules?

Pydantic will later use type hints as the basis for runtime validation. Keeping these two ideas separate is essential.

## Practice

Return to your `prompt_builder.py` from Chunk 04 and add hints:

1. `topic` should be `str`.
2. `level` should be `str`.
3. `build_prompt()` should return `str`.
4. Variables holding the returned prompts should be `str`.

Then define this additional function yourself:

```python
def display_prompts(prompts: list[str]) -> None:
```

Its body should loop through and print the prompts.

### Optional challenge

Create a type alias named `Settings` for `dict[str, str | float]`. Use it as the return hint of a function that builds a settings dictionary.

## Check your understanding

1. What does `-> str` describe?
2. How do you hint a list of integers?
3. What does `str | None` mean?
4. Why use a type alias?
5. Do type hints validate values automatically at runtime?

Answers: (1) the expected return type; (2) `list[int]`; (3) either a string or `None`; (4) to give a clear name to a repeated or longer type; (5) no.

## You are ready for Chunk 08 when...

You can add hints to a function, read `list[str]` and `str | None`, and explain why type hints alone do not validate incoming data.
