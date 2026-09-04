import asyncio


async def show_message() -> None:
    print("Starting async Python.")


asyncio.run(show_message())

