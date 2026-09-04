# Chunk 03: Collections and Loops

## Goal

By the end of this chunk, you will be able to:

- store several values in a list;
- read and update list items;
- repeat an action with a loop;
- store labeled values in a dictionary;
- combine lists and dictionaries to represent structured data.

## 1. Lists hold values in order

A **list** stores multiple values in one variable. Write its items between square brackets `[]` and separate them with commas.

Lists keep their order. Each position has an **index**, starting at `0`:

```text
Item:   Python   Pydantic   Pydantic AI
Index:     0         1           2
```

The first example creates a learning path, reads two items by index, and uses `len()` to count all items.

Run [01_lists.py](examples/01_lists.py).

Expected output:

```text
First topic: Python
Second topic: Pydantic
Number of topics: 3
```

An index outside the list causes an `IndexError`. For a three-item list, the valid indexes are `0`, `1`, and `2`.

## 2. Lists can change

Lists are **mutable**, meaning their contents can change after creation.

The next example uses three common list operations:

- `append()` adds one item to the end;
- assignment replaces an item at an index;
- `remove()` removes the first matching value.

Run [02_changing_lists.py](examples/02_changing_lists.py).

Expected output:

```text
['Python basics', 'Functions', 'Pydantic']
```

## 3. Loops repeat an action

A `for` loop takes each item from a collection, one at a time, and runs an indented block for that item.

The next example loops through three tasks. During each repetition, `task` refers to the current item. `enumerate()` also provides a number; `start=1` makes that number begin at `1` instead of `0`.

Run [03_for_loops.py](examples/03_for_loops.py).

Expected output:

```text
1. Read the lesson
2. Run the examples
3. Complete the practice
All tasks displayed.
```

The final non-indented line runs once, after the loop finishes.

## 4. Dictionaries store labeled values

A **dictionary** stores pairs of keys and values. Write the pairs between curly braces `{}`. A colon separates each key from its value.

Lists answer “what is at this position?” Dictionaries answer “what value belongs to this label?”

The next example represents one AI response. It reads values using keys, adds a new pair, and updates an existing value.

Run [04_dictionaries.py](examples/04_dictionaries.py).

Expected output:

```text
Model: example-model
Status: complete
Tokens: 42
```

Trying to read a missing key with square brackets causes a `KeyError`. When a key may be absent, `.get()` can return `None` or a fallback value instead:

```python
cost = response.get("cost", "not available")
```

## 5. Looping through a dictionary

The `.items()` method provides each key and value together. Two loop variables receive them during every repetition.

The next example prints each setting and its current value.

Run [05_dictionary_loop.py](examples/05_dictionary_loop.py).

Expected output:

```text
temperature: 0.2
max_tokens: 200
stream: False
```

## 6. Combining lists and dictionaries

Real applications often combine collections. A chat history, for example, can be a list in which every item is a dictionary. The list preserves message order; each dictionary labels the message's `role` and `content`.

The final example loops through this nested structure and reads two keys from every message.

Run [06_chat_messages.py](examples/06_chat_messages.py).

Expected output:

```text
SYSTEM: Answer clearly.
USER: What is a Python list?
ASSISTANT: A list stores values in order.
```

You will see this general data shape again when working with AI libraries and APIs.

## Practice

Create `model_catalog.py` in the `examples` folder. Before writing it, plan this data:

1. Make a list containing three dictionaries.
2. Give every dictionary a `name` and an `available` value.
3. Use `True` or `False` for `available`.
4. Loop through the list.
5. Print only the names of available models.

Example data shape:

```python
models = [
    {"name": "small-model", "available": True},
    {"name": "large-model", "available": False},
]
```

This is only the starting shape; add a third model yourself.

### Optional challenge

Count the available models. Start with `available_count = 0`, then add `1` whenever a model is available. Print the final count after the loop.

## Check your understanding

1. What index identifies the first list item?
2. What does `append()` do?
3. Why is the code inside a `for` loop indented?
4. How is a dictionary key different from a list index?
5. Why is a list of dictionaries useful for chat messages?

Answers: (1) `0`; (2) it adds an item to the end; (3) indentation identifies the repeated block; (4) a key is a meaningful label rather than a numeric position; (5) the list keeps message order while each dictionary labels its data.

## You are ready for Chunk 04 when...

You can loop through a list, read dictionary values by key, and recognize a list containing dictionaries.

