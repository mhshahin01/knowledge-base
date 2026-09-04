import asyncio


async def check_model(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name}: ready"


async def main() -> None:
    results = await asyncio.gather(
        check_model("small-model", 0.3),
        check_model("medium-model", 0.2),
        check_model("large-model", 0.1),
    )

    for result in results:
        print(result)


asyncio.run(main())

