# Chunk 02: Making Decisions

## Goal

By the end of this chunk, you will be able to:

- compare values;
- run code only when a condition is true;
- choose between two or more actions;
- combine simple conditions.

## 1. Comparisons create Boolean values

A **condition** is an expression that Python evaluates as either `True` or `False`. These two values have the type `bool`.

Python uses comparison operators to compare values:

| Operator | Meaning | Example |
|---|---|---|
| `==` | equal to | `score == 10` |
| `!=` | not equal to | `name != ""` |
| `>` | greater than | `score > 10` |
| `<` | less than | `score < 10` |
| `>=` | greater than or equal to | `score >= 10` |
| `<=` | less than or equal to | `score <= 10` |

Remember: `=` assigns a value, while `==` compares two values.

The first example compares a completed lesson count with a goal. Each comparison produces `True` or `False`.

Run [01_comparisons.py](examples/01_comparisons.py).

Expected output:

```text
True
False
True
```

## 2. A decision with `if`

An `if` statement runs an indented block only when its condition is `True`.

The next example checks whether the learner has completed enough lessons. Because `completed_lessons >= goal` is true, Python runs the indented `print()` line.

Run [02_simple_if.py](examples/02_simple_if.py).

Expected output:

```text
You reached your goal!
Keep learning.
```

Important details:

- Put a colon `:` after the condition.
- Indent the code controlled by `if` using four spaces.
- Non-indented code continues normally after the decision.

## 3. Choosing between two actions

Use `if` with `else` when exactly one of two actions should happen.

The next program asks how many minutes the learner studied. `int()` converts the answer from text to a whole number. If the number reaches the target, Python prints the first message. Otherwise, it prints the `else` message.

Run [03_if_else.py](examples/03_if_else.py) and try both a number below `20` and a number equal to or above `20`.

Example interaction:

```text
How many minutes did you study? 25
Great work! You reached today's target.
```

For now, enter only whole numbers. We will handle invalid input safely in Chunk 05.

## 4. Choosing between several actions

Use `elif`, meaning “else if,” to check another condition when the earlier condition was false.

The next example classifies a model confidence score:

- `0.80` or higher becomes `high`;
- otherwise, `0.50` or higher becomes `medium`;
- anything lower becomes `low`.

Python stops at the first true branch, so the order matters. The most demanding condition comes first.

Run [04_multiple_choices.py](examples/04_multiple_choices.py).

Expected output:

```text
Confidence: medium
```

## 5. Combining conditions

Python provides three useful logical operators:

| Operator | Result |
|---|---|
| `and` | `True` only when both conditions are true |
| `or` | `True` when at least one condition is true |
| `not` | Reverses `True` and `False` |

The final example approves a request only when the user is active **and** has enough credits. It also uses `not` to give a specific message to inactive users.

Run [05_combined_conditions.py](examples/05_combined_conditions.py).

Expected output:

```text
Request approved.
```

Use parentheses when they make a combined condition easier to read, even when Python does not require them.

## Practice

Create `temperature_advice.py` in the `examples` folder. Plan the behavior before writing the code:

1. Ask the user for a whole-number temperature.
2. Convert the answer with `int()`.
3. Print `Wear a coat.` when the temperature is below `10`.
4. Print `Take a light jacket.` when it is from `10` through `19`.
5. Print `A jacket is not needed.` when it is `20` or higher.

Test the boundary values `9`, `10`, `19`, and `20`. Boundary tests help reveal gaps between conditions.

### Optional challenge

Ask whether it is raining. Clean the answer with `.strip().lower()`. Recommend an umbrella when the answer is `"yes"` **or** `"y"`.

## Check your understanding

1. What is the difference between `=` and `==`?
2. Why is indentation important after `if`?
3. When does an `else` block run?
4. Why should `confidence >= 0.80` come before `confidence >= 0.50`?
5. What does `and` require?

Answers: (1) `=` assigns and `==` compares; (2) indentation identifies the controlled block; (3) when all preceding conditions in the statement are false; (4) otherwise a high value would match the medium test first; (5) both conditions must be true.

## You are ready for Chunk 03 when...

You can use `if`, `elif`, and `else` to choose an action, and you understand that every condition becomes `True` or `False`.
