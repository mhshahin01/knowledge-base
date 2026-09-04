# Chunk 04: Functions

## Goal

By the end of this chunk, you will be able to:

- define and call a function;
- give information to a function through parameters;
- return a result from a function;
- use default and keyword arguments;
- write functions that work with lists and dictionaries.

## 1. Functions group reusable actions

A **function** is a named block of code that performs a task. Python includes functions such as `print()` and `len()`, and you can define your own with `def`.

Defining a function prepares it but does not run it. Calling the function by writing its name followed by `()` runs its indented body.

The first example defines `show_welcome()` and then calls it twice.

Run [01_simple_function.py](examples/01_simple_function.py).

Expected output:

```text
Welcome to Python!
Learn one small idea at a time.
Welcome to Python!
Learn one small idea at a time.
```

Function names normally use lowercase words joined by underscores. A name should describe the action, such as `show_welcome` or `calculate_total`.

## 2. Parameters provide input

A **parameter** is a name in a function definition. It receives a value when the function is called. The supplied value is called an **argument**.

In the next example, `name` and `topic` are parameters. `"Maya"` and `"functions"` are arguments in the first call. The same function works with different arguments in the second call.

Run [02_parameters.py](examples/02_parameters.py).

Expected output:

```text
Maya is learning functions.
Sam is learning dictionaries.
```

## 3. `return` sends a result back

`print()` displays a value for a person. `return` sends a value back to the code that called the function so the program can keep using it.

The next function calculates a result and returns it. The calling code saves that result in `lessons_left`, then prints it.

Run [03_return_values.py](examples/03_return_values.py).

Expected output:

```text
Lessons remaining: 2
```

A function without an explicit `return` produces the special value `None` after it finishes.

## 4. Default and keyword arguments

A parameter can have a default value. The caller may omit that argument when the default is suitable.

The next function gives `tone` the default value `"clear"`. The first call uses that default. The second call supplies `tone="concise"` as a **keyword argument**, which makes the purpose of the value easy to see.

Run [04_defaults.py](examples/04_defaults.py).

Expected output:

```text
Explain Python lists. Use a clear tone.
Explain Python functions. Use a concise tone.
```

Parameters without defaults must come before parameters with defaults in a function definition.

## 5. Functions keep work organized

A useful function usually does one clear job. Larger programs combine several small functions.

The final example uses:

- `create_message()` to build and return one dictionary;
- `display_messages()` to loop through a list and display every dictionary.

The functions are defined first. The main part of the program then calls them to create and display an AI-style conversation.

Run [05_message_functions.py](examples/05_message_functions.py).

Expected output:

```text
SYSTEM: Answer simply.
USER: What does return do?
```

The names created inside a function, including its parameters, are normally **local** to that function. This helps each function perform its job without accidentally changing unrelated parts of the program.

## Practice

Create `prompt_builder.py` in the `examples` folder. Plan the function before writing it:

1. Define `build_prompt(topic, level="beginner")`.
2. Make it return a sentence containing both values.
3. Call it once using the default level.
4. Call it again with `level="intermediate"`.
5. Print both returned sentences outside the function.

Example output shape:

```text
Teach loops to a beginner learner.
Teach functions to an intermediate learner.
```

### Optional challenge

Define `create_user_message(content)`. It should clean `content` with `.strip()` and return this dictionary shape:

```python
{"role": "user", "content": "the cleaned content"}
```

Call the function and print its returned dictionary.

## Check your understanding

1. Does defining a function also run it?
2. What is the difference between a parameter and an argument?
3. How is `return` different from `print()`?
4. Why would a parameter have a default value?
5. Why are several small functions often easier to work with than one large function?

Answers: (1) no, the function must be called; (2) a parameter is the receiving name, while an argument is a supplied value; (3) `return` gives a result back to the program, while `print()` displays it; (4) it makes a common argument optional; (5) each function has one smaller, clearer job.

## You are ready for Chunk 05 when...

You can define a function with parameters, call it with arguments, and use its returned value outside the function.

