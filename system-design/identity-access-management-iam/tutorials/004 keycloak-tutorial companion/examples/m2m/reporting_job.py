"""
reporting_job.py - Machine-to-machine example (Client Credentials grant).

No human. No browser. No password. Just a client_id + client_secret
that Keycloak exchanges for an access token.

Run:  pip install requests
      python reporting_job.py
"""
import requests

KEYCLOAK_URL = "http://localhost:8080"
REALM = "acme"
CLIENT_ID = "acme-reporting-job"
CLIENT_SECRET = "reporting-secret-change-me"   # in real life: read from env var / vault
API_URL = "http://localhost:8000"

# Step 1 - ask Keycloak for a token
token_resp = requests.post(
    f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token",
    data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
)
token_resp.raise_for_status()
access_token = token_resp.json()["access_token"]
print("Got a token, expires in", token_resp.json()["expires_in"], "seconds")

# Step 2 - call the API with it
headers = {"Authorization": f"Bearer {access_token}"}

print("GET /orders ->", requests.get(f"{API_URL}/orders", headers=headers).json())

# The service account only has orders:read, so this must FAIL with 403:
r = requests.post(f"{API_URL}/orders", json={"item": "Anvil", "qty": 3}, headers=headers)
print("POST /orders ->", r.status_code, r.json())
