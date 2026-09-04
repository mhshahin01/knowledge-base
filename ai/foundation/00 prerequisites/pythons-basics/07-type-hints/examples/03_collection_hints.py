def count_characters(prompts: list[str]) -> int:
    total = 0

    for prompt in prompts:
        total += len(prompt)

    return total


lesson_prompts: list[str] = ["Explain lists.", "Explain functions."]
character_count: int = count_characters(lesson_prompts)
print(f"Total characters: {character_count}")

