"""
desktop_login.py - How a MOBILE or DESKTOP (native) app logs in.

Authorization Code flow + PKCE, done by hand so you can SEE every step.
(Real mobile apps use a library such as AppAuth; the steps are identical.)

Run:  pip install requests
      python desktop_login.py
Then log in as alice / alice123 in the browser window that opens.
"""
import base64, hashlib, secrets, threading, urllib.parse, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

KEYCLOAK_URL = "http://localhost:8080"
REALM = "acme"
CLIENT_ID = "acme-mobile"
REDIRECT_URI = "http://localhost:8765/callback"     # a real phone app uses com.acme.mobile://callback
ISSUER = f"{KEYCLOAK_URL}/realms/{REALM}"

# ---- Step 1: PKCE - create a random secret (verifier) and its hash (challenge) ---------------
code_verifier = secrets.token_urlsafe(64)
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).rstrip(b"=").decode()
state = secrets.token_urlsafe(16)          # protects against CSRF

# ---- Step 2: send the user to Keycloak's login page ----------------------------------------
auth_url = f"{ISSUER}/protocol/openid-connect/auth?" + urllib.parse.urlencode({
    "client_id": CLIENT_ID,
    "response_type": "code",
    "scope": "openid profile email",
    "redirect_uri": REDIRECT_URI,
    "state": state,
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
})
print("Opening browser:\n ", auth_url, "\n")
webbrowser.open(auth_url)

# ---- Step 3: catch the redirect back that carries the one-time 'code' ----------------------
received = {}

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        received.update({k: v[0] for k, v in qs.items()})
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Logged in! You can close this tab.</h2>")
    def log_message(self, *a):  # silence the default request logging
        pass

server = HTTPServer(("localhost", 8765), CallbackHandler)
server.handle_request()                     # handle exactly ONE request, then continue
assert received.get("state") == state, "state mismatch - possible CSRF!"
code = received["code"]

# ---- Step 4: exchange code + verifier for tokens (no client secret needed - PKCE proves it's us)
tokens = requests.post(f"{ISSUER}/protocol/openid-connect/token", data={
    "grant_type": "authorization_code",
    "client_id": CLIENT_ID,
    "code": code,
    "redirect_uri": REDIRECT_URI,
    "code_verifier": code_verifier,
}).json()

print("access_token :", tokens["access_token"][:40], "...")
print("refresh_token:", tokens["refresh_token"][:40], "...")
print("id_token     :", tokens["id_token"][:40], "...")

# ---- Step 5: use the access token ---------------------------------------------------------
me = requests.get(f"{ISSUER}/protocol/openid-connect/userinfo",
                  headers={"Authorization": f"Bearer {tokens['access_token']}"}).json()
print("\nWho am I?", me)
