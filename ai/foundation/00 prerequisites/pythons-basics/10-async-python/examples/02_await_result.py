import asyncio


async def fetch_lesson(topic: str) -> str:
    await asyncio.sleep(0.1)
    return f"Loaded: {topic}"


async def main() -> None:
    lesson = await fetch_lesson("functions")
    print(lesson)


asyncio.run(main())

