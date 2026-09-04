import json

import httpx


def handle_request(request: httpx.Request) -> httpx.Response:
    received_data = json.loads(request.content)
    return httpx.Response(201, json={"id": 1, **received_data})


transport = httpx.MockTransport(handle_request)

with httpx.Client(transport=transport) as client:
    response = client.post(
        "https://api.example.test/prompts",
        json={"prompt": "Explain async Python."},
    )

response.raise_for_status()
saved_data = response.json()

print(f"Status: {response.status_code}")
print(f"Saved prompt: {saved_data['prompt']}")

