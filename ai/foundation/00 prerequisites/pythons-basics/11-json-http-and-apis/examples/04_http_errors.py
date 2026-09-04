import httpx


def handle_request(request: httpx.Request) -> httpx.Response:
    return httpx.Response(404, json={"detail": "Task not found"})


transport = httpx.MockTransport(handle_request)

try:
    with httpx.Client(transport=transport) as client:
        response = client.get("https://api.example.test/tasks/99")
        response.raise_for_status()
except httpx.HTTPStatusError as error:
    print(f"Request failed with status {error.response.status_code}.")

