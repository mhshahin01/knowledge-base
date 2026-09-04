answer = input("How many minutes did you study? ")

try:
    minutes = int(answer)
except ValueError:
    print("Please enter a whole number.")
else:
    print(f"Recorded {minutes} minutes.")

