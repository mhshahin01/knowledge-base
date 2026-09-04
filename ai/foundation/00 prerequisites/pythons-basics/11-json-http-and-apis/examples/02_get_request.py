import httpx


url = "https://jsonplaceholder.typicode.com/todos/1"
response = httpx.get(url, timeout=10.0)
response.raise_for_status()
task = response.json()

print(f"Status: {response.status_code}")
print(f"Title: {task['title']}")
print(f"Completed: {task['completed']}")

