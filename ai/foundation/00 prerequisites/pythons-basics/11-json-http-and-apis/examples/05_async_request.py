import asyncio

import httpx


async def main() -> None:
    url = "https://jsonplaceholder.typicode.com/todos/1"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()

    task = response.json()
    print(f"Async title: {task['title']}")


asyncio.run(main())
