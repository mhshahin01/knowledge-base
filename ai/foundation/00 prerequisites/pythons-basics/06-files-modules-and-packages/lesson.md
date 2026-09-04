# Chunk 06: Files, Modules, and Packages

## Goal

By the end of this chunk, you will be able to:

- read and write a text file;
- import tools from Python's standard library;
- split your own code into modules;
- recognize a Python package;
- load structured JSON data.

## 1. Paths identify files

A **path** describes where a file or folder is located. Python's standard-library `pathlib` module provides the `Path` class for working with paths.

An `import` makes code from another module available. This line imports only the `Path` name:

```python
from pathlib import Path
```

The first example starts from the running script's `__file__` path, moves to the chunk directory, and locates `data/learning_notes.txt`. It then reads the file as UTF-8 text.

Run [01_read_file.py](examples/01_read_file.py).

Expected output:

```text
Practice a little each day.
Run every example yourself.
```

Using the script's location makes the path reliable regardless of which directory your terminal currently uses.

## 2. Writing a text file

`Path.write_text()` writes a string to a file. It replaces the file's previous contents if the file already exists.

The next example first creates an `output` directory when needed. It then saves a study summary using UTF-8 encoding.

Run [02_write_file.py](examples/02_write_file.py).

Expected output:

```text
Saved: study_summary.txt
```

After running it, inspect `06-files-modules-and-packages/output/study_summary.txt`.

Use `encoding="utf-8"` for predictable text handling across operating systems.

## 3. Modules organize code

Every `.py` file is a **module**. Moving reusable functions into a module keeps the main program shorter and avoids copying code.

The file [prompt_tools.py](examples/prompt_tools.py) defines `build_prompt()`. The next program imports that function and calls it.

Run [03_use_module.py](examples/03_use_module.py).

Expected output:

```text
Teach dictionaries in simple steps.
```

Python runs a module's top-level code when importing it. A main guard prevents test or demonstration code from running during an import:

```python
if __name__ == "__main__":
    print("This module was run directly.")
```

Run [prompt_tools.py](examples/prompt_tools.py) directly to see its guarded demonstration. Importing it in `03_use_module.py` does not run that demonstration.

## 4. Packages group modules

A **package** is a directory containing related Python modules. A package commonly includes an `__init__.py` file, which can expose selected names to users of the package.

This chunk contains a small `course_tools` package:

```text
course_tools/
    __init__.py
    messages.py
```

The next program imports `create_message()` from the package. The package's `__init__.py` makes that function available at the package level.

Run [04_use_package.py](examples/04_use_package.py).

Expected output:

```text
{'role': 'user', 'content': 'Explain packages.'}
```

Packages become more valuable as a project grows and related code needs clear boundaries.

## 5. JSON stores structured data

**JSON** is a text format used by configuration files, web services, and AI APIs. Its objects look similar to Python dictionaries.

Python's standard-library `json` module converts JSON text into Python values. The final example reads `model_settings.json`, converts it into a dictionary with `json.loads()`, and accesses its values by key.

Run [05_json_data.py](examples/05_json_data.py).

Expected output:

```text
Model: example-model
Temperature: 0.2
Streaming: False
```

JSON uses lowercase `true`, `false`, and `null`. After conversion to Python, they become `True`, `False`, and `None`.

## Practice

Create `save_goal.py` in the `examples` folder:

1. Ask the user for a learning goal.
2. Clean it with `.strip()`.
3. Build an output path using `Path(__file__)`.
4. Create the output directory if needed.
5. Save the goal in `output/learning_goal.txt`.
6. Read the file back and print its contents.

### Optional challenge

Add a `format_goal(goal)` function to a new `goal_tools.py` module. Import and use it from `save_goal.py`. Put demonstration code in `goal_tools.py` behind a main guard.

## Check your understanding

1. What does an `import` do?
2. Why is `Path(__file__)` useful?
3. What happens when `write_text()` targets an existing file?
4. What is the difference between a module and a package?
5. What Python type usually represents a JSON object after loading?

Answers: (1) it makes code from another module available; (2) it lets paths start from the script's location; (3) the old contents are replaced; (4) a module is one `.py` file, while a package groups modules in a directory; (5) `dict`.

## You are ready for Chunk 07 when...

You can read a file with `Path`, import a function from another module, and explain why packages help organize a growing project.

