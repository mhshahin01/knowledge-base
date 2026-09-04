# Chunk 10: Async Python

## Goal

By the end of this chunk, you will be able to:

- define and run an asynchronous function;
- wait for an asynchronous result with `await`;
- run independent waiting operations concurrently;
- handle exceptions from asynchronous code;
- recognize when async is useful.

## 1. Async is for waiting efficiently

Applications spend time waiting for network responses, files, or databases. **Asynchronous** code can let other work progress during that waiting time.

Define an asynchronous function with `async def`. Calling it creates a **coroutine**, which represents work that can be awaited. `asyncio.run()` starts the top-level coroutine in a normal Python program.

The first example defines one coroutine and runs it.

Run [01_first_coroutine.py](examples/01_first_coroutine.py).

Expected output:

```text
Starting async Python.
```

Async does not automatically make calculations faster. It is most useful for operations that spend time waiting.

## 2. `await` waits without blocking async work

Use `await` inside an async function to wait for another asynchronous operation. The current coroutine pauses until the result is ready.

The next example uses `asyncio.sleep()` to represent a short network wait. `fetch_lesson()` returns a string, and `main()` awaits that result before printing it.

Run [02_await_result.py](examples/02_await_result.py).

Expected output:

```text
Loaded: functions
```

You may use `await` only inside code running asynchronously.

## 3. Concurrency handles independent waits together

Sequential code waits for one operation before starting the next. **Concurrent** async code can start several independent operations and wait for all of them together.

`asyncio.gather()` accepts multiple coroutines and returns their results in the same order they were supplied.

The next example checks three models concurrently. Their simulated delays differ, but the displayed result order stays predictable.

Run [03_concurrent_work.py](examples/03_concurrent_work.py).

Expected output:

```text
small-model: ready
medium-model: ready
large-model: ready
```

Concurrency is valuable when separate AI or HTTP requests do not depend on one another.

## 4. Async exceptions behave normally

An awaited operation can raise an exception. Use the same `try` and `except` structure learned in Chunk 05.

The next async function rejects an empty prompt. `main()` awaits it inside `try` and handles the resulting `ValueError`.

Run [04_async_errors.py](examples/04_async_errors.py).

Expected output:

```text
Prompt error: prompt cannot be empty
```

## 5. Avoid blocking the event loop

The **event loop** coordinates asynchronous work. A slow regular function blocks that loop because it cannot pause at `await`.

Inside async code:

- use `await asyncio.sleep(...)`, not `time.sleep(...)`;
- use async HTTP and database clients when available;
- keep heavy CPU calculations separate from the event loop.

Many AI frameworks provide both styles:

- a synchronous method for simple scripts;
- an async method for servers or concurrent workflows.

Choose async because your program manages waiting operations—not merely because async syntax exists.

## Practice

Create `prepare_prompts.py` in the `examples` folder:

1. Define `async def prepare_prompt(topic: str) -> str`.
2. Await `asyncio.sleep(0.1)` inside it.
3. Return `Explain {topic}.`.
4. In `main()`, use `asyncio.gather()` for `lists`, `functions`, and `classes`.
5. Loop through and print the returned prompts.
6. Start the program with `asyncio.run(main())`.

### Optional challenge

Make one topic empty and raise `ValueError` for it. Catch the failure around `asyncio.gather()` in `main()`.

## Check your understanding

1. What does calling an `async def` function create?
2. Where can `await` be used?
3. What problem is async best suited to?
4. Does `asyncio.gather()` preserve result order?
5. Should async code use `time.sleep()` for a delay?

Answers: (1) a coroutine; (2) inside asynchronous code; (3) managing waiting or I/O; (4) yes; (5) no, use `await asyncio.sleep()`.

## You are ready for Chunk 11 when...

You can run a coroutine, await a result, and explain why several independent network requests may run concurrently.

Official reference: [Python `asyncio`](https://docs.python.org/3.14/library/asyncio.html).
