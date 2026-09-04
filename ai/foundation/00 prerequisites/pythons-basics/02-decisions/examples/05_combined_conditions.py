is_active = True
available_credits = 2

if is_active and available_credits > 0:
    print("Request approved.")
elif not is_active:
    print("Activate your account first.")
else:
    print("Not enough credits.")
