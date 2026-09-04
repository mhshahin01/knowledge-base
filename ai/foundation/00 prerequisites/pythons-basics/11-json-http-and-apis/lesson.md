# Chunk 11: JSON, HTTP, and APIs

## Goal

By the end of this chunk, you will be able to:

- convert between Python values and JSON text;
- describe an HTTP request and response;
- send GET and POST requests with HTTPX;
- check HTTP failures;
- send an asynchronous request.

Install the course dependencies from Chunk 09 before running these examples.

## 1. JSON carries structured data

**JSON** is a text format commonly used to send data to and from APIs. Python's `json` module performs both directions:

- `json.dumps()` converts a Python value to a JSON string;
- `json.loads()` converts a JSON string to a Python value.

The first example converts a dictionary to JSON and back. Notice that Python's `True` becomes JSON's lowercase `true`.

Run [01_json_conversion.py](examples/01_json_conversion.py).

Expected output:

```text
JSON: {"topic": "Python", "completed": true}
Python type: dict
Topic: Python
```

JSON supports objects, arrays, strings, numbers, booleans, and `null`. They usually become Python dictionaries, lists, strings, numbers, booleans, and `None`.

## 2. HTTP connects to an API

An **API** defines how programs communicate. Web APIs commonly use HTTP.

An HTTP exchange contains:

- a method such as `GET` or `POST`;
- a URL identifying the resource;
- optional headers, parameters, or a body;
- a response with a status code and body.

`GET` normally reads data. The next example uses HTTPX to request one sample task from JSONPlaceholder, a public practice API. `raise_for_status()` raises an exception for unsuccessful status codes, and `.json()` converts the response body to Python data.

Run [02_get_request.py](examples/02_get_request.py) while connected to the internet.

Expected output:

```text
Status: 200
Title: delectus aut autem
Completed: False
```

Always set a timeout. A network request should not wait forever.

## 3. POST sends data

`POST` commonly sends a new payload. HTTPX's `json=` argument converts a Python value to JSON and adds the appropriate content type.

The next example uses `MockTransport`, a local pretend API, so it makes no external change. The handler receives the request and returns a response with status `201`, meaning a resource was created.

Run [03_post_json.py](examples/03_post_json.py).

Expected output:

```text
Status: 201
Saved prompt: Explain async Python.
```

The mock is only a teaching replacement for a server. Normal application code still uses the same `client.post(...)` shape.

## 4. Network and HTTP errors differ

Two broad failure groups matter:

- `httpx.RequestError`: the request could not complete, perhaps because of a connection or timeout problem;
- `httpx.HTTPStatusError`: a response arrived, but its status was an error such as `404` or `500`.

The next example's local mock returns `404`. Calling `raise_for_status()` turns that response into `HTTPStatusError`, which the program handles.

Run [04_http_errors.py](examples/04_http_errors.py).

Expected output:

```text
Request failed with status 404.
```

Do not automatically retry every failure. A timeout may be temporary, while `401 Unauthorized` usually means credentials must be fixed.

## 5. Async HTTP fits async applications

Use `httpx.AsyncClient` inside async code. Its request methods are awaited, and the client should be closed with `async with`.

The final example performs the same public GET request asynchronously.

Run [05_async_request.py](examples/05_async_request.py) while connected to the internet.

Expected output:

```text
Async title: delectus aut autem
```

Reuse one client for multiple related requests in a real application instead of creating a new client for every request.

## 6. Keep API keys secret

API keys prove that your program may use a service. Never place a real key directly in source code or commit it to version control.

For a temporary PowerShell session, set an environment variable:

```powershell
$env:EXAMPLE_API_KEY = "your-key"
```

Read it in Python without printing it:

```python
import os

api_key = os.environ["EXAMPLE_API_KEY"]
headers = {"Authorization": f"Bearer {api_key}"}
```

Use the environment-variable name required by the actual provider.

## Practice

Create `inspect_task.py` in the `examples` folder:

1. Request `https://jsonplaceholder.typicode.com/todos/2`.
2. Set a timeout.
3. Call `raise_for_status()`.
4. Convert the body with `.json()`.
5. Print the task's `id`, `title`, and `completed` values.
6. Catch `httpx.RequestError` and `httpx.HTTPStatusError` separately.

### Optional challenge

Write an async version and request tasks `1`, `2`, and `3` concurrently with `asyncio.gather()`.

## Check your understanding

1. What is the difference between `json.dumps()` and `json.loads()`?
2. What does a GET request normally do?
3. What does HTTPX's `json=` argument do?
4. Why call `raise_for_status()`?
5. Where should API keys be stored instead of source code?

Answers: (1) one encodes to JSON text and the other decodes it; (2) reads a resource; (3) encodes Python data as a JSON request body; (4) to turn error responses into exceptions; (5) in a suitable secret store or environment variable.

## You are ready for Chunk 12 when...

You can make a GET request, inspect its status, convert its JSON body, and explain why untrusted response data still needs validation.

Official references: [HTTPX quick start](https://www.python-httpx.org/quickstart/) and [async support](https://www.python-httpx.org/async/).
