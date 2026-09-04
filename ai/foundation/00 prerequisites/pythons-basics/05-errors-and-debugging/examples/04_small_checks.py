def calculate_average(total, count):
    if count == 0:
        raise ValueError("count cannot be zero")
    return total / count


assert calculate_average(10, 2) == 5
assert calculate_average(9, 3) == 3

print("All checks passed.")
