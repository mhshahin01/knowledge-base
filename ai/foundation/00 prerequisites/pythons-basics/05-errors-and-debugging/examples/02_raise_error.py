def validate_confidence(confidence):
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be between 0.0 and 1.0")
    return confidence


try:
    validate_confidence(1.4)
except ValueError as error:
    print(f"Invalid confidence: {error}")

