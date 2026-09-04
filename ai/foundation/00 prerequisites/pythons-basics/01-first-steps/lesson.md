# Chunk 01: Your First Python Programs

## Goal

By the end of this chunk, you will be able to:

- run a Python file;
- recognize common kinds of values;
- save values in variables;
- display values with `print()`;
- receive simple user input.

## 1. A Python file

A Python program is a plain-text file whose name ends in `.py`. Python reads the file from top to bottom and performs each instruction in order.

The first example gives the text `Hello, Python!` to the built-in `print()` function. A function is a named action. Parentheses contain the information given to that action.

Run [01_hello.py](examples/01_hello.py):

```powershell
py 01-first-steps/examples/01_hello.py
```

Expected output:

```text
Hello, Python!
I am learning one step at a time.
```

The quotation marks tell Python that the contents are text. They are not included in the output.

## 2. Values and their types

A **value** is a piece of data. Every value has a **type**, which tells Python what kind of data it is and what can be done with it.

| Python type | Meaning | Example |
|---|---|---|
| `str` | Text, also called a string | `"Ada"` |
| `int` | Whole number | `3` |
| `float` | Number with a decimal part | `3.5` |
| `bool` | Either true or false | `True` |
| `NoneType` | No value yet | `None` |

Notice that text uses quotes but numbers do not. `True`, `False`, and `None` begin with capital letters and do not use quotes.

## 3. Variables

A **variable** is a name that refers to a value. The `=` symbol assigns the value on its right to the name on its left.

The next example creates four variables. It then uses an **f-string** to place their values inside readable text. An f-string begins with `f`, and expressions inside `{}` are evaluated by Python.

Run [02_variables.py](examples/02_variables.py).

Expected output:

```text
Maya is learning Python.
Completed lessons: 1
Study time: 25.5 minutes
Ready for the next lesson: True
```

Choose descriptive variable names such as `completed_lessons`. Python convention uses lowercase words joined by underscores.

## 4. User input

The `input()` function shows a prompt and waits for the user to type. It always returns text, even if the user types digits.

The final example asks for a name and a learning goal. It stores both answers, removes accidental surrounding spaces with `.strip()`, and uses an f-string to create a personal summary.

Run [03_learning_profile.py](examples/03_learning_profile.py), then answer its two questions.

Example interaction:

```text
What is your name? Sam
What do you want to build with Python? an AI assistant

Welcome, Sam!
Your goal is to build an AI assistant.
```

## 5. Comments

A comment starts with `#`. Python ignores everything after it on that line. Use comments to explain **why** something is done when the reason is not obvious.

```python
# Remove spaces so the saved name is clean.
name = input("What is your name? ").strip()
```

Avoid comments that merely repeat clear code.

## Practice

Create a file named `my_profile.py` in the `examples` folder. Before writing it, plan these three actions:

1. Ask for the user's name.
2. Ask how many minutes they want to study today.
3. Print one friendly sentence containing both answers.

Example result:

```text
Hi, Lee! Your study target is 20 minutes today.
```

### Optional challenge

`input()` returns text. Convert the minutes to a whole number with `int(...)`, then print its type:

```python
minutes = int(input("How many minutes will you study? "))
print(type(minutes))
```

Expected final line:

```text
<class 'int'>
```

If letters are entered instead of a whole number, the program will stop with an error. That is normal for now; a later chunk will teach safe error handling.

## Check your understanding

1. Why does `"25"` represent text while `25` represents a number?
2. What does `=` do in `name = "Maya"`?
3. What type does `input()` return?
4. What is the purpose of an f-string?

Answers: (1) quotation marks create a string; (2) it assigns a value to a variable; (3) `str`; (4) it places values or expressions inside text.

## You are ready for Chunk 02 when...

You can run a `.py` file, create a few variables, and print a sentence containing their values. Perfection is not required.

