# Chunk 05: Errors and Debugging

## Goal

By the end of this chunk, you will be able to:

- recognize common kinds of errors;
- read the useful part of a traceback;
- handle an expected error with `try` and `except`;
- reject invalid values with `raise`;
- use small checks while debugging.

## 1. Three kinds of problems

Python programs commonly have three kinds of problems:

| Kind | Meaning | Example |
|---|---|---|
| Syntax error | Python cannot understand the code | a missing `:` after `if` |
| Exception | The code starts but cannot complete an operation | `int("hello")` |
| Logic error | The code runs but produces the wrong result | adding when you meant to subtract |

When an exception is not handled, Python displays a **traceback**. Start reading at the bottom: it gives the exception type and message. Then look upward for the line in your own file that caused it.

For example, `int("hello")` ends with a message like this:

```text
ValueError: invalid literal for int() with base 10: 'hello'
```

`ValueError` tells you that the kind of operation was valid, but the supplied value was not.

## 2. Handling an expected error

Use `try` when an operation may fail in an expected way. Put the recovery action in `except`.

The first example attempts to convert user input to an integer. If conversion fails, the `ValueError` branch displays a helpful message. The `else` block runs only when no exception occurred.

Run [01_safe_number.py](examples/01_safe_number.py). Try it once with `25` and once with `hello`.

Valid interaction:

```text
How many minutes did you study? 25
Recorded 25 minutes.
```

Invalid interaction:

```text
How many minutes did you study? hello
Please enter a whole number.
```

Catch the specific exception you expect. A broad `except:` can hide unrelated programming mistakes.

## 3. Rejecting an invalid value

A function can use `raise` to deliberately stop when its input breaks a rule. This keeps invalid data from moving further through the program.

The next example requires confidence to be between `0.0` and `1.0`. It raises a `ValueError` for `1.4`. The calling code catches that error and displays its message.

Run [02_raise_error.py](examples/02_raise_error.py).

Expected output:

```text
Invalid confidence: confidence must be between 0.0 and 1.0
```

## 4. Different failures need different responses

One operation may fail for different reasons. Separate `except` blocks can provide a suitable result for each exception.

The next function reads a token count from a dictionary:

- a missing `"tokens"` key causes `KeyError` and returns `0`;
- a value that cannot become an integer causes `TypeError` or `ValueError` and also returns `0`;
- valid data is converted and returned normally.

Run [03_specific_errors.py](examples/03_specific_errors.py).

Expected output:

```text
42
0
0
```

Returning `0` is appropriate for this learning example. In a real application, decide whether a fallback, a log message, or a stopped operation is safest.

## 5. Debugging with small checks

Debugging means finding why observed behavior differs from expected behavior. A useful process is:

1. Reproduce the problem with a small input.
2. Read the complete error message.
3. Inspect the values near the failing line.
4. Change one likely cause.
5. Run the same input again.

An `assert` records an expectation that should always be true inside correctly written code. If the condition is false, Python raises `AssertionError`.

The final example checks a small calculation using known inputs. These checks help reveal future logic errors.

Run [04_small_checks.py](examples/04_small_checks.py).

Expected output:

```text
All checks passed.
```

Use normal validation and exceptions for user input. Assertions are mainly developer checks and may be disabled when Python runs with optimization.

## Practice

Create `safe_temperature.py` in the `examples` folder:

1. Ask for a temperature.
2. Try to convert it to `float`.
3. Catch `ValueError` and display `Please enter a number.`
4. In `else`, reuse the temperature decision rules from Chunk 02.

Test it with `8`, `15.5`, and `cold`.

### Optional challenge

Define `validate_temperature(value)`. Raise `ValueError` when the value is below `-100` or above `100`. Catch the error when calling the function.

## Check your understanding

1. Where should you begin when reading a traceback?
2. When does a `try` statement's `else` block run?
3. Why should you catch a specific exception?
4. What does `raise` do?
5. Are assertions a replacement for validating user input?

Answers: (1) at the final exception type and message; (2) when the `try` block succeeds; (3) to avoid hiding unrelated mistakes; (4) it deliberately produces an exception; (5) no, use normal validation for user input.

## You are ready for Chunk 06 when...

You can read the bottom of a traceback, catch an expected `ValueError`, and explain why a function might raise an exception.

