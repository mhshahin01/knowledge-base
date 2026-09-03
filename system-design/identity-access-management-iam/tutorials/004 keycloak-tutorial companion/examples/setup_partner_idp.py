"""
setup_partner_idp.py - Identity brokering demo.

Creates a SECOND realm called "partner-corp" (pretend it is a completely different
company's login system) and registers it inside "acme" as an Identity Provider.
Result: the acme login page shows a "Login with Partner Corp" button.

Run:  python setup_partner_idp.py   (after setup_realm.py)
"""
import requests

KEYCLOAK = "http://localhost:8080"

tok = requests.post(f"{KEYCLOAK}/realms/master/protocol/openid-connect/token", data={
    "grant_type": "password", "client_id": "admin-cli", "username": "admin", "password": "admin"}).json()
H = {"Authorization": f"Bearer {tok['access_token']}", "Content-Type": "application/json"}
API = f"{KEYCLOAK}/admin/realms"

def post(path, payload):
    r = requests.post(f"{API}{path}", json=payload, headers=H)
    if r.status_code not in (201, 204, 409):
        raise SystemExit(f"POST {path} failed: {r.status_code} {r.text}")

# 1. The "other company": realm partner-corp with one user
requests.post(API, json={"realm": "partner-corp", "enabled": True, "displayName": "Partner Corp"}, headers=H)
post("/partner-corp/users", {
    "username": "dave", "firstName": "Dave", "lastName": "Davis", "email": "dave@partner.test",
    "emailVerified": True, "enabled": True,
    "credentials": [{"type": "password", "value": "dave123", "temporary": False}],
})

# 2. In partner-corp, register ACME as a client (ACME is the app that wants to log people in)
post("/partner-corp/clients", {
    "clientId": "acme-broker",
    "publicClient": False,
    "secret": "broker-secret-change-me",
    "standardFlowEnabled": True,
    # Keycloak's broker callback URL is always: <server>/realms/<realm>/broker/<idp-alias>/endpoint
    "redirectUris": [f"{KEYCLOAK}/realms/acme/broker/partner-corp/endpoint*"],
})

# 3. In acme, add partner-corp as an Identity Provider (generic OpenID Connect)
post("/acme/identity-provider/instances", {
    "alias": "partner-corp",
    "displayName": "Partner Corp",
    "providerId": "oidc",                    # generic OIDC; also: "keycloak-oidc", "google", "github", "saml" ...
    "enabled": True,
    "trustEmail": True,
    "firstBrokerLoginFlowAlias": "first broker login",
    "config": {
        "clientId": "acme-broker",
        "clientSecret": "broker-secret-change-me",
        "authorizationUrl": f"{KEYCLOAK}/realms/partner-corp/protocol/openid-connect/auth",
        "tokenUrl":         f"{KEYCLOAK}/realms/partner-corp/protocol/openid-connect/token",
        "userInfoUrl":      f"{KEYCLOAK}/realms/partner-corp/protocol/openid-connect/userinfo",
        "logoutUrl":        f"{KEYCLOAK}/realms/partner-corp/protocol/openid-connect/logout",
        "jwksUrl":          f"{KEYCLOAK}/realms/partner-corp/protocol/openid-connect/certs",
        "issuer":           f"{KEYCLOAK}/realms/partner-corp",
        "validateSignature": "true",
        "useJwksUrl": "true",
        "defaultScope": "openid profile email",
        "syncMode": "IMPORT",
    },
})

# 4. Everyone who logs in via Partner Corp automatically gets the 'employee' realm role
post("/acme/identity-provider/instances/partner-corp/mappers", {
    "name": "partner-employee-role",
    "identityProviderAlias": "partner-corp",
    "identityProviderMapper": "oidc-hardcoded-role-idp-mapper",
    "config": {"role": "employee", "syncMode": "INHERIT"},
})

print("Done. Open http://localhost:8080/realms/acme/account and click 'Partner Corp'. Log in as dave / dave123.")
