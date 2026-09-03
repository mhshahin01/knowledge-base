"""
main.py - The ACME Orders API (a "resource server").

It never shows a login page. It only checks the Bearer token that callers send.

Run:   pip install fastapi uvicorn pyjwt[crypto] requests
       uvicorn main:app --port 8000 --reload
"""
from fastapi import FastAPI, Depends, HTTPException, Request
import jwt                      # PyJWT
from jwt import PyJWKClient

KEYCLOAK_URL = "http://localhost:8080"
REALM = "acme"
ISSUER = f"{KEYCLOAK_URL}/realms/{REALM}"
AUDIENCE = "acme-api"            # tokens must be intended FOR this API
JWKS_URL = f"{ISSUER}/protocol/openid-connect/certs"

# Downloads Keycloak's public keys once and caches them.
# The API can now verify signatures OFFLINE - no call to Keycloak per request.
jwks_client = PyJWKClient(JWKS_URL, cache_keys=True)

app = FastAPI(title="ACME Orders API")

# CORS: the browser (SPA on :3000) is a *different origin* than this API (:8000).
# Without this, the browser blocks the SPA's fetch() before it even reaches us.
# (Keycloak has its own, separate CORS setting: the client's "Web origins" field.)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

ORDERS = [
    {"id": 1, "item": "Rocket skates", "qty": 2},
    {"id": 2, "item": "Giant magnet", "qty": 1},
]


def current_user(request: Request) -> dict:
    """Reads 'Authorization: Bearer <token>', verifies it, returns the claims."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing Bearer token")
    token = auth[len("Bearer "):]

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)   # picks key by 'kid'
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AUDIENCE,      # rejects tokens meant for other APIs
            issuer=ISSUER,          # rejects tokens from other realms/servers
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.PyJWTError as e:
        raise HTTPException(401, f"Invalid token: {e}")
    return claims


def require_client_role(role: str):
    """Dependency factory: the token must carry <role> under resource_access.acme-api."""
    def checker(claims: dict = Depends(current_user)) -> dict:
        roles = claims.get("resource_access", {}).get(AUDIENCE, {}).get("roles", [])
        if role not in roles:
            raise HTTPException(403, f"Requires role '{role}'")
        return claims
    return checker


@app.get("/public")
def public():
    return {"message": "Anyone can see this. No token needed."}


@app.get("/me")
def me(claims: dict = Depends(current_user)):
    return {
        "username": claims.get("preferred_username"),
        "email": claims.get("email"),
        "department": claims.get("department"),
        "groups": claims.get("groups"),
        "realm_roles": claims.get("realm_access", {}).get("roles"),
        "api_roles": claims.get("resource_access", {}).get(AUDIENCE, {}).get("roles"),
        "called_from_client": claims.get("azp"),
    }


@app.get("/orders")
def list_orders(claims: dict = Depends(require_client_role("orders:read"))):
    return ORDERS


@app.post("/orders")
def create_order(order: dict, claims: dict = Depends(require_client_role("orders:write"))):
    order["id"] = len(ORDERS) + 1
    order["created_by"] = claims.get("preferred_username")
    ORDERS.append(order)
    return order
