def calculate_remaining(completed, total):
    remaining = total - completed
    return remaining


lessons_left = calculate_remaining(3, 5)
print(f"Lessons remaining: {lessons_left}")

