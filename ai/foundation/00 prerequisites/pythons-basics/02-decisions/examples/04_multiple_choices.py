confidence = 0.72

if confidence >= 0.80:
    level = "high"
elif confidence >= 0.50:
    level = "medium"
else:
    level = "low"

print(f"Confidence: {level}")

