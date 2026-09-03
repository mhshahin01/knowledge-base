#!/usr/bin/env bash
# 004-keycloak-token.sh
# Runs the full authorization code flow with PKCE from tutorial 004, Section 15,
# with no browser: PKCE pair -> login as alice (simulated browser) -> code -> tokens.
# Requires: curl, openssl. Optional: python (for pretty-printing / payload decode).
# Usage: bash 004-keycloak-token.sh

set -euo pipefail

# --- Configuration (matches hands-on/part-04/realm-export.json) ----------------
BASE_URL="http://localhost:8080"
REALM="iam-demo"
CLIENT_ID="curl-demo"
REDIRECT_URI="http://localhost:8088/callback"
SCOPE="profile"
USERNAME="alice"
PASSWORD="alice-password"

COOKIE_JAR=$(mktemp)
trap 'rm -f "$COOKIE_JAR"' EXIT

echo "== Step 0: is the stack up?"
ISSUER=$(curl -s --max-time 5 "$BASE_URL/realms/$REALM/.well-known/openid-configuration" | head -c 40)
if [[ "$ISSUER" != "{\"issuer\""* ]]; then
  echo "ERROR: Keycloak is not answering at $BASE_URL (or still booting). Run: cd hands-on && docker compose up -d" >&2
  exit 1
fi
echo "   OK: $ISSUER..."

echo "== Step 1: generate the PKCE pair (Section 15, Step 3)"
VERIFIER=$(openssl rand -base64 48 | tr '+/' '-_' | tr -d '=' | cut -c1-43)
CHALLENGE=$(printf '%s' "$VERIFIER" | openssl dgst -sha256 -binary | openssl base64 | tr '+/' '-_' | tr -d '=')
echo "   verifier:  $VERIFIER"
echo "   challenge: $CHALLENGE"

echo "== Step 2: hit the authorization endpoint (Section 15, Step 4, front channel)"
AUTH_URL="$BASE_URL/realms/$REALM/protocol/openid-connect/auth?response_type=code&client_id=$CLIENT_ID&redirect_uri=$REDIRECT_URI&scope=$SCOPE&state=demo-state-123&code_challenge=$CHALLENGE&code_challenge_method=S256"
LOGIN_PAGE=$(curl -s -c "$COOKIE_JAR" "$AUTH_URL")
FORM_ACTION=$(printf '%s' "$LOGIN_PAGE" | grep -o 'action="[^"]*"' | head -1 | sed 's/^action="//; s/"$//' | sed 's/&amp;/\&/g')
if [[ -z "$FORM_ACTION" ]]; then
  echo "ERROR: no login form found. Keycloak may have rejected the request; check the authorize URL parameters." >&2
  exit 1
fi
echo "   login form received, posting credentials as $USERNAME"

echo "== Step 3: log in (what the browser does when alice types her password)"
LOCATION=$(curl -s -b "$COOKIE_JAR" -c "$COOKIE_JAR" -D - -o /dev/null -X POST "$FORM_ACTION" \
  --data-urlencode "username=$USERNAME" --data-urlencode "password=$PASSWORD" | grep -i '^location:' | tr -d '\r' | cut -d' ' -f2)
CODE=$(printf '%s' "$LOCATION" | grep -o 'code=[^&]*' | cut -d= -f2)
if [[ -z "$CODE" ]]; then
  echo "ERROR: no code in the redirect. Got: $LOCATION" >&2
  exit 1
fi
echo "   code: $CODE"

echo "== Step 4: exchange the code for tokens (Section 15, Step 5, back channel)"
RESPONSE=$(curl -s -X POST "$BASE_URL/realms/$REALM/protocol/openid-connect/token" \
  -d grant_type=authorization_code \
  -d client_id="$CLIENT_ID" \
  -d redirect_uri="$REDIRECT_URI" \
  -d code="$CODE" \
  -d code_verifier="$VERIFIER")

if printf '%s' "$RESPONSE" | grep -q '"error"'; then
  echo "ERROR: token exchange failed:" >&2
  printf '%s\n' "$RESPONSE" >&2
  exit 1
fi

if command -v python >/dev/null 2>&1; then
  printf '%s' "$RESPONSE" | python -c "
import sys, json, base64
d = json.load(sys.stdin)
print('   token_type:', d['token_type'], '| expires_in:', d['expires_in'], '| refresh_expires_in:', d.get('refresh_expires_in'), '| scope:', d.get('scope'))
p = d['access_token'].split('.')[1]
payload = json.loads(base64.urlsafe_b64decode(p + '=' * (-len(p) % 4)))
print('   decoded access token payload:')
print(json.dumps(payload, indent=2))
"
else
  echo "   raw token response:"
  printf '%s\n' "$RESPONSE"
fi

echo "== Done. Access + refresh tokens issued for $USERNAME (one-time code consumed; rerun the script for a fresh pair)."
