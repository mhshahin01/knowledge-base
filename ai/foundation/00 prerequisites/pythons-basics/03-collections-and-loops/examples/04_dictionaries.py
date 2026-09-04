response = {
    "model": "example-model",
    "status": "pending",
}

response["tokens"] = 42
response["status"] = "complete"

print(f"Model: {response['model']}")
print(f"Status: {response['status']}")
print(f"Tokens: {response['tokens']}")

