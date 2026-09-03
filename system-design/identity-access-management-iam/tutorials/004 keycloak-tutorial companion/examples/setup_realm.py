"""
setup_realm.py  -  Builds the whole "acme" tutorial realm with the Keycloak Admin REST API.

Run:  python setup_realm.py
Needs: pip install requests

Everything this script does can also be clicked through in the Admin Console.
The script exists so you can rebuild the realm in 5 seconds instead of 15 minutes.
"""
import requests

KEYCLOAK = "http://localhost:8080"
ADMIN_USER, ADMIN_PASS = "admin", "admin"
REALM = "acme"

# ---------------------------------------------------------------------------
# 1. Log in as the Keycloak admin (we get a token from the *master* realm)
# ---------------------------------------------------------------------------
resp = requests.post(
    f"{KEYCLOAK}/realms/master/protocol/openid-connect/token",
    data={
        "grant_type": "password",
        "client_id": "admin-cli",
        "username": ADMIN_USER,
        "password": ADMIN_PASS,
    },
)
resp.raise_for_status()
admin_token = resp.json()["access_token"]
H = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
API = f"{KEYCLOAK}/admin/realms"


def post(path, payload):
    """POST helper that ignores '409 already exists' so the script is re-runnable."""
    r = requests.post(f"{API}{path}", json=payload, headers=H)
    if r.status_code not in (201, 204, 409):
        raise SystemExit(f"POST {path} failed: {r.status_code} {r.text}")
    return r


def get(path):
    r = requests.get(f"{API}{path}", headers=H)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# 2. Realm  (a realm = one isolated "world" of users, apps and settings)
# ---------------------------------------------------------------------------
r = requests.post(
    API,
    json={
        "realm": REALM,
        "enabled": True,
        "displayName": "ACME Corp",
        "registrationAllowed": True,          # show "Register" link on the login page
        "resetPasswordAllowed": True,         # show "Forgot password?" link
        "rememberMe": True,
        "loginWithEmailAllowed": True,
        "bruteForceProtected": True,          # lock accounts after repeated failures
        "accessTokenLifespan": 300,           # 5 minutes
        "ssoSessionIdleTimeout": 1800,        # 30 min idle -> session dies
        "ssoSessionMaxLifespan": 36000,       # 10 hours absolute max
        "eventsEnabled": True,                # record user events (LOGIN, LOGOUT ...)
        "eventsExpiration": 604800,           # keep them 7 days
        "enabledEventTypes": [],              # empty list = ALL event types
        "adminEventsEnabled": True,           # record admin events (who changed what)
        "adminEventsDetailsEnabled": True,
        "eventsListeners": ["jboss-logging"], # also write every event to the server log
    },
    headers=H,
)
if r.status_code not in (201, 409):
    raise SystemExit(f"Create realm failed: {r.status_code} {r.text}")
print(f"Realm '{REALM}' ready")

# ---------------------------------------------------------------------------
# 3. Realm roles  (a role = a label describing WHAT someone may do)
# ---------------------------------------------------------------------------
for role in ["employee", "manager", "admin"]:
    post(f"/{REALM}/roles", {"name": role, "description": f"ACME {role}"})
print("Realm roles: employee, manager, admin")

# ---------------------------------------------------------------------------
# 4. Groups  (a group = a bucket of users that hands out roles automatically)
# ---------------------------------------------------------------------------
for group in ["Sales", "Engineering", "Management"]:
    post(f"/{REALM}/groups", {"name": group})

groups = {g["name"]: g["id"] for g in get(f"/{REALM}/groups")}
roles = {r["name"]: r for r in get(f"/{REALM}/roles")}

def map_role_to_group(group_name, role_name):
    role = roles[role_name]
    post(f"/{REALM}/groups/{groups[group_name]}/role-mappings/realm",
         [{"id": role["id"], "name": role["name"]}])

map_role_to_group("Sales", "employee")
map_role_to_group("Engineering", "employee")
map_role_to_group("Management", "employee")
map_role_to_group("Management", "manager")
print("Groups: Sales, Engineering, Management (with roles attached)")

# ---------------------------------------------------------------------------
# 5. Users
# ---------------------------------------------------------------------------
USERS = [
    # username     first     last       email                  password     groups
    ("alice",     "Alice",  "Anderson", "alice@acme.test",     "alice123",  ["Sales"]),
    ("bob",       "Bob",    "Brown",    "bob@acme.test",       "bob123",    ["Engineering"]),
    ("carol",     "Carol",  "Clark",    "carol@acme.test",     "carol123",  ["Management"]),
]
for username, first, last, email, password, user_groups in USERS:
    post(f"/{REALM}/users", {
        "username": username,
        "firstName": first,
        "lastName": last,
        "email": email,
        "emailVerified": True,
        "enabled": True,
        "credentials": [{"type": "password", "value": password, "temporary": False}],
        "groups": [f"/{g}" for g in user_groups],
    })
print("Users: alice (Sales), bob (Engineering), carol (Management)")

# ---------------------------------------------------------------------------
# 6. Client scope  (a reusable bundle of claims a client can ask for)
# ---------------------------------------------------------------------------
post(f"/{REALM}/client-scopes", {
    "name": "acme-profile",
    "description": "Adds department + realm roles to tokens",
    "protocol": "openid-connect",
    "attributes": {"include.in.token.scope": "true", "display.on.consent.screen": "true"},
    "protocolMappers": [
        {   # copy the user attribute 'department' into the token as a claim
            "name": "department",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-usermodel-attribute-mapper",
            "config": {
                "user.attribute": "department",
                "claim.name": "department",
                "jsonType.label": "String",
                "id.token.claim": "true",
                "access.token.claim": "true",
                "userinfo.token.claim": "true",
            },
        },
        {   # put the user's groups into the token
            "name": "groups",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-group-membership-mapper",
            "config": {
                "claim.name": "groups",
                "full.path": "false",
                "id.token.claim": "true",
                "access.token.claim": "true",
                "userinfo.token.claim": "true",
            },
        },
    ],
})
scope_id = [s for s in get(f"/{REALM}/client-scopes") if s["name"] == "acme-profile"][0]["id"]
print("Client scope: acme-profile")

# ---------------------------------------------------------------------------
# 7. Clients  (a client = an application that trusts this realm to log people in)
# ---------------------------------------------------------------------------
CLIENTS = [
    {   # (a) Browser Single-Page App (React/Vue/Angular). PUBLIC client + PKCE.
        "clientId": "acme-spa",
        "name": "ACME Web Portal (SPA)",
        "protocol": "openid-connect",
        "publicClient": True,                      # cannot keep a secret -> no secret
        "standardFlowEnabled": True,               # Authorization Code flow
        "directAccessGrantsEnabled": False,
        "serviceAccountsEnabled": False,
        "rootUrl": "http://localhost:3000",
        "redirectUris": ["http://localhost:3000/*"],
        "webOrigins": ["http://localhost:3000"],   # CORS
        "attributes": {"pkce.code.challenge.method": "S256",
                       "post.logout.redirect.uris": "http://localhost:3000/*"},
    },
    {   # (b) Mobile app (iOS/Android). Also PUBLIC + PKCE, custom-scheme redirect.
        "clientId": "acme-mobile",
        "name": "ACME Mobile App",
        "protocol": "openid-connect",
        "publicClient": True,
        "standardFlowEnabled": True,
        "directAccessGrantsEnabled": False,
        "redirectUris": ["com.acme.mobile://callback", "http://localhost:8765/*"],
        "attributes": {"pkce.code.challenge.method": "S256",
                       "post.logout.redirect.uris": "com.acme.mobile://logout"},
    },
    {   # (c) Traditional server-side web app (Django/Flask with sessions). CONFIDENTIAL.
        "clientId": "acme-webapp",
        "name": "ACME Classic Web App",
        "protocol": "openid-connect",
        "publicClient": False,                     # server keeps a client secret
        "secret": "webapp-secret-change-me",
        "standardFlowEnabled": True,
        "directAccessGrantsEnabled": False,
        "rootUrl": "http://localhost:5000",
        "redirectUris": ["http://localhost:5000/*"],
        "webOrigins": ["http://localhost:5000"],
        "attributes": {"post.logout.redirect.uris": "http://localhost:5000/*"},
    },
    {   # (d) Machine-to-machine: a cron job / another service. CONFIDENTIAL + service account.
        "clientId": "acme-reporting-job",
        "name": "Nightly Reporting Job (M2M)",
        "protocol": "openid-connect",
        "publicClient": False,
        "secret": "reporting-secret-change-me",
        "standardFlowEnabled": False,              # no humans -> no browser login
        "directAccessGrantsEnabled": False,
        "serviceAccountsEnabled": True,            # Client Credentials grant
    },
    {   # (e) The backend REST API. It never logs anyone in; it only VERIFIES tokens.
        "clientId": "acme-api",
        "name": "ACME Orders API",
        "protocol": "openid-connect",
        "publicClient": False,
        "secret": "api-secret-change-me",         # only used for token introspection
        "standardFlowEnabled": False,
        "directAccessGrantsEnabled": False,
        "serviceAccountsEnabled": False,
        # Client roles: permissions that only make sense INSIDE this API
        "defaultRoles": [],
    },
    {   # (f) Legacy / testing client that allows username+password directly (no browser).
        "clientId": "acme-cli",
        "name": "ACME CLI tool (Direct Access Grant)",
        "protocol": "openid-connect",
        "publicClient": True,
        "standardFlowEnabled": False,
        "directAccessGrantsEnabled": True,         # Resource Owner Password grant
        "attributes": {"oauth2.device.authorization.grant.enabled": "true"},  # Device flow too
    },
]
for c in CLIENTS:
    post(f"/{REALM}/clients", c)
clients = {c["clientId"]: c["id"] for c in get(f"/{REALM}/clients")}
print("Clients: acme-spa, acme-mobile, acme-webapp, acme-reporting-job, acme-api, acme-cli")

# attach our custom scope as a DEFAULT scope to the human-facing clients
for cid in ["acme-spa", "acme-mobile", "acme-webapp", "acme-cli"]:
    requests.put(f"{API}/{REALM}/clients/{clients[cid]}/default-client-scopes/{scope_id}", headers=H)

# ---------------------------------------------------------------------------
# 8. Client roles on the API  +  give them to the M2M service account
# ---------------------------------------------------------------------------
api_id = clients["acme-api"]
for role in ["orders:read", "orders:write"]:
    post(f"/{REALM}/clients/{api_id}/roles", {"name": role})
api_roles = {r["name"]: r for r in get(f"/{REALM}/clients/{api_id}/roles")}

# The service account of acme-reporting-job is a hidden user called
# "service-account-acme-reporting-job". Give it orders:read only.
sa_user = get(f"/{REALM}/clients/{clients['acme-reporting-job']}/service-account-user")
post(f"/{REALM}/users/{sa_user['id']}/role-mappings/clients/{api_id}",
     [api_roles["orders:read"]])

# Managers can write orders; every employee can read them
mgmt = groups["Management"]
post(f"/{REALM}/groups/{mgmt}/role-mappings/clients/{api_id}",
     [api_roles["orders:read"], api_roles["orders:write"]])
for g in ["Sales", "Engineering"]:
    post(f"/{REALM}/groups/{groups[g]}/role-mappings/clients/{api_id}", [api_roles["orders:read"]])
print("API client roles: orders:read, orders:write (mapped to groups + service account)")

# Make the 'aud' (audience) claim contain 'acme-api' for tokens issued to the user-facing clients.
post(f"/{REALM}/client-scopes", {
    "name": "acme-api-audience",
    "protocol": "openid-connect",
    "attributes": {"include.in.token.scope": "false"},
    "protocolMappers": [{
        "name": "acme-api audience",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-audience-mapper",
        "config": {"included.client.audience": "acme-api", "access.token.claim": "true"},
    }],
})
aud_id = [s for s in get(f"/{REALM}/client-scopes") if s["name"] == "acme-api-audience"][0]["id"]
for cid in ["acme-spa", "acme-mobile", "acme-webapp", "acme-cli", "acme-reporting-job"]:
    requests.put(f"{API}/{REALM}/clients/{clients[cid]}/default-client-scopes/{aud_id}", headers=H)

# ---------------------------------------------------------------------------
# 9. Give the users a 'department' attribute so the mapper has something to copy
# ---------------------------------------------------------------------------
# First allow the attribute in the realm's user profile (Keycloak 24+ has a strict user profile)
profile = get(f"/{REALM}/users/profile")
if not any(a["name"] == "department" for a in profile["attributes"]):
    profile["attributes"].append({
        "name": "department", "displayName": "Department",
        "permissions": {"view": ["admin", "user"], "edit": ["admin"]},
        "validations": {"length": {"max": 64}},
    })
    requests.put(f"{API}/{REALM}/users/profile", json=profile, headers=H).raise_for_status()

for username, dept in [("alice", "Sales"), ("bob", "Engineering"), ("carol", "Management")]:
    u = get(f"/{REALM}/users?username={username}&exact=true")[0]
    u["attributes"] = {**u.get("attributes", {}), "department": [dept]}
    requests.put(f"{API}/{REALM}/users/{u['id']}", json=u, headers=H).raise_for_status()

print("\nDone!  Admin console: http://localhost:8080/admin/master/console/#/acme")
print("Account console (log in as alice/alice123): http://localhost:8080/realms/acme/account")
