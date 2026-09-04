# Chunk 12: Pydantic Foundations

## Goal

By the end of this chunk, you will be able to:

- define a Pydantic model;
- validate untrusted input;
- inspect validation errors;
- add field constraints and custom validation;
- validate nested data;
- convert models to dictionaries and JSON.

These examples use Pydantic 2.13.5. Install the course dependencies from Chunk 09 first.

## 1. Models validate data at runtime

Type hints describe expected data, but Python does not enforce them by itself. A Pydantic model reads those hints and validates actual values at runtime.

Define a model by inheriting from `BaseModel`. Each annotated class attribute becomes a field.

The first example validates a dictionary. The incoming lesson count is the string `"8"`; Pydantic converts it to an integer because the conversion is safe.

Run [01_first_model.py](examples/01_first_model.py).

Expected output:

```text
Maya completed 8 lessons.
lessons type: int
```

Use `model_validate()` when data arrives as a dictionary or another Python object. Pydantic returns a validated model instance.

## 2. Validation errors are structured

Invalid data raises `ValidationError`. Its `.errors()` method returns a list of dictionaries describing each problem, including its field location, error type, and message.

The next example supplies text where a number is required. It catches the error and displays two stable details.

Run [02_validation_errors.py](examples/02_validation_errors.py).

Expected output:

```text
Field: temperature
Error type: float_parsing
```

A real application may return these details to a form, log them, or ask an AI model to correct its output.

## 3. Fields can have constraints

`Field()` adds rules beyond the basic type. The next settings model requires:

- a nonempty model name;
- temperature from `0.0` through `2.0`;
- a positive token limit.

`ConfigDict(extra="forbid")` also rejects unexpected fields instead of silently ignoring them.

Run [03_field_constraints.py](examples/03_field_constraints.py).

Expected output:

```text
model='example-model' temperature=0.2 max_tokens=200
```

Constraints place important rules next to the field they protect.

## 4. Models can be nested

A model field can contain another model or a list of models. `Literal` restricts a value to specific choices.

The next example defines a conversation containing chat messages. Pydantic converts each message dictionary into a `ChatMessage` instance and verifies its role.

Run [04_nested_models.py](examples/04_nested_models.py).

Expected output:

```text
Message count: 2
First role: system
Second content: Explain Pydantic.
```

Nested models are especially useful for validating API responses and structured AI output.

## 5. Custom validators handle special rules

Use `@field_validator` when a rule cannot be expressed clearly with `Field()` alone. The validator receives the field value after basic type validation, checks or transforms it, and returns the accepted value.

The next validator strips surrounding spaces and rejects content that becomes empty.

Run [05_custom_validator.py](examples/05_custom_validator.py).

Expected output:

```text
Content: Explain validators.
```

A validator must return the accepted value. Raise `ValueError` when the value breaks the rule.

## 6. Models convert to and from JSON

Use Pydantic's current model methods:

- `model_validate_json()` validates JSON text directly;
- `model_dump()` produces a Python dictionary;
- `model_dump_json()` produces a JSON string.

The final example validates a JSON message and serializes the model in both forms.

Run [06_json_models.py](examples/06_json_models.py).

Expected output:

```text
{'role': 'user', 'content': 'Explain JSON models.'}
{"role":"user","content":"Explain JSON models."}
```

Older Pydantic v1 tutorials may use methods such as `parse_obj()` and `.dict()`. New code should use the `model_*` methods above.

## Practice

Create `study_plan.py` in the `examples` folder:

1. Define a `StudyPlan` model with `topic: str`, `minutes: int`, and `completed: bool = False`.
2. Require `topic` to contain at least one character.
3. Require `minutes` to be from `1` through `180`.
4. Forbid extra fields.
5. Validate one dictionary successfully.
6. Catch and inspect `ValidationError` for an invalid dictionary.
7. Print the valid plan as JSON.

### Optional challenge

Define a `Course` model containing `plans: list[StudyPlan]`, then validate a dictionary containing three plans.

## Check your understanding

1. How is Pydantic validation different from a normal type hint?
2. What does `model_validate()` return?
3. What exception represents invalid model data?
4. What does `extra="forbid"` protect against?
5. Which method validates JSON text directly?

Answers: (1) it checks actual values at runtime; (2) a validated model instance; (3) `ValidationError`; (4) unexpected input fields; (5) `model_validate_json()`.

## You are ready for Chunk 13 when...

You can define a constrained `BaseModel`, catch `ValidationError`, and serialize a valid model to JSON.

Official references: [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/) and [validators](https://docs.pydantic.dev/latest/concepts/validators/).
