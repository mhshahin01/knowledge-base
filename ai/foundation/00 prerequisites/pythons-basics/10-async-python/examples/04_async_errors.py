import asyncio


async def prepare_prompt(prompt: str) -> str:
    await asyncio.sleep(0.1)

    if not prompt.strip():
        raise ValueError("prompt cannot be empty")

    return prompt.strip()


async def main() -> None:
    try:
        await prepare_prompt("   ")
    except ValueError as error:
        print(f"Prompt error: {error}")


asyncio.run(main())
