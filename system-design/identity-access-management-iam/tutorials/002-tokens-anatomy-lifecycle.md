# Tokens: What They Are, Anatomy & Lifecycle: Complete Tutorial

> Last updated: 2026-08-30 | Applicable to: the field as of August 2026
> Difficulty: Beginner | Estimated time: 60 minutes reading, plus 30 minutes optional hands-on

## Tutorial Overview

This tutorial covers **tokens** from zero: what a token is and why systems hand them out instead
of re-checking your password, the two families of tokens (opaque and self-contained), the anatomy
of a JSON Web Token (JWT) piece by piece with a real decoded example, the three token types you
will meet (access, refresh, ID), how to validate a token correctly, the full token lifecycle from
issuance to revocation, and the basics of transporting and storing tokens without leaking them. It
closes with a decision guide, an optional hands-on track where you decode and sign real tokens,
and the classic beginner pitfalls.

*Where this sits in the series:* this is Part 2 of eight, and it builds on Part 1
(`001-iam-foundations-user-management.md`), which gave you the vocabulary: principal, credential,
claim, role. This part explains the artifact every later protocol moves around: the token. Part 3
(`003-single-sign-on-sso.md`) then shows the user-facing goal (SSO), and Parts 4 and 5 (OAuth 2.0
and OIDC) show the protocols that issue and deliver tokens. Nothing here requires any of those
later parts.

After completing this tutorial, you will be able to:

- Explain what a token is and how it differs from a credential.
- Distinguish opaque tokens from self-contained tokens, and state what each one costs.
- Read a JWT by hand: header, payload, signature, and every claim inside.
- Tell access tokens, refresh tokens, and ID tokens apart, and say who consumes each.
- Validate a token correctly, and explain why decoding is not verifying.
- Describe the token lifecycle, including why stateless tokens are hard to revoke.

**How to read it:** Part 1 is sequential, each section builds on the one before. Part 2 is a
skimmable survey of token formats. Part 3 is practical: a decision guide, an optional hands-on
track, and pitfalls worth reading even if you skip the hands-on. Part 4 and the Appendix are
reference material to return to later.

---

## Table of Contents

- Part 1: Foundations
  - 1. What is a token?
  - 2. Opaque tokens vs self-contained tokens
  - 3. JWT anatomy: header, payload, signature
  - 4. Token types: access, refresh, ID
  - 5. Validating a token correctly
  - 6. The token lifecycle (the honest part)
  - 7. Transport and storage basics
- Part 2: The Landscape (token formats)
  - 8. The map: three lanes
  - 9. Lane A: JWT
  - 10. Lane B: Opaque (reference) tokens
  - 11. Honorable mentions
- Part 3: Putting It Into Practice
  - 12. How to choose: JWT vs opaque
  - 13. Optional hands-on track: decode a JWT by hand, then sign and verify one
  - 14. Common misconceptions and pitfalls
- Part 4: Reference
  - 15. Advanced topics and learning path
  - 16. Cheatsheet
  - Appendix: Glossary and sources

---

# Part 1: Foundations

## 1. What is a token?

**Objective:** give a correct one-sentence definition of a token and explain why systems issue
tokens instead of re-checking credentials.

A **token** is a portable, tamper-evident proof that an authentication already happened: a string
the issuer creates once, the holder presents many times, and the receiver can check without
re-running the login.

The one-sentence mental model:

> A token is a festival wristband: issued once at the gate after your ticket was checked, then
> checked cheaply at every stage inside, and hard to fake convincingly.

**A real-life picture: the music festival.** You arrive with your ticket and your ID. At the
entrance gate, staff compare your face to the ID, scan the ticket, and then they do something
important: they do *not* keep checking your ID for the rest of the weekend. Instead they strap a
wristband on you. From then on, every staff member inside, at every stage and every bar, glances
at the wristband and waves you through. Mapping each element back:

- **The ID-and-ticket check at the gate is authentication.** Credentials presented once, at one
  place, by one party (Part 1 of this series, `001-iam-foundations-user-management.md`, Section
  2). In software this is your login at the identity provider.
- **The wristband is the token.** Proof you carry around afterward and present to everyone else.
- **The print on the wristband is the claims.** The color (day pass vs VIP) and the date are
  facts any staff member can read at a glance. In a JWT these are key-value pairs like
  `role: nurse`.
- **The hologram seal is the signature.** Anyone can read the print, but only the festival can
  produce the seal. Photocopying the band gives you the text without the seal, and staff are
  trained to check the seal.
- **Stage staff checking the band locally is stateless validation.** They do not phone the box
  office for every guest; the seal and the print are enough. This is what makes token-based
  systems fast, and it creates the revocation problem of Section 6.
- **The band stops being valid when the festival ends.** Tokens expire too (`exp`, Section 3).
  To come back tomorrow you queue at the gate again (re-authenticate) or visit the re-issue desk
  (refresh, Section 6).

Why not just re-check the password on every request? Three reasons:

- **The credential is too dangerous to spray around.** Your password should be seen by exactly
  one party, the issuer. Sending it to every API you call multiplies the copies an attacker can
  steal (Section 6 of Part 1 of this series showed what stolen credentials cost).
- **The check is too expensive to repeat.** Verifying a password means a deliberately slow hash
  computation (Section 13 of Part 1 of this series). Doing that on every API call would melt the
  login server.
- **The token can say more than "logged in".** It carries claims, so the API learns *who* and
  *what is allowed* from the same string, without a database lookup.

Keep the two artifacts straight for the rest of the series: a **credential** is what you present
to *log in*; a token is what you *get back* and present afterward. The credential is long-lived
and shown to one party. The token is short-lived and shown to many.

**Self-check:** An API receives a request carrying a token. Which of IAM's three questions is the
token answering, and which one does the API still answer itself? (The token carries the result of
authentication, "who you are", plus claims. The API still answers authorization, "what may you
do", by evaluating those claims. Re-read Section 2 of Part 1 of this series if this felt shaky.)

---

## 2. Opaque tokens vs self-contained tokens

**Objective:** distinguish the two token families and state the validation cost, revocation
behavior, payload visibility, and size of each.

All tokens come in one of two families, and the difference is where the *meaning* lives.

- **Opaque token** (also called a **reference token**): a random-looking string like
  `7f3a9c1e...` with no readable content. It means nothing by itself; it is a *reference* to a
  record stored at the issuer. To learn anything from it, you must ask the issuer.
- **Self-contained token**: the token itself carries the claims, plus a signature protecting
  them. The receiver reads and checks it locally, no phone call home. The dominant format is the
  JWT of Section 3.

| | Opaque (reference) | Self-contained (JWT) |
|---|---|---|
| **What the receiver sees** | A meaningless random string | Readable claims plus a signature |
| **Validation cost** | A network call to the issuer on (nearly) every request | Local signature check, microseconds, works offline |
| **Revocation** | Immediate: delete the record, the token dies | Hard: the token stays valid until it expires (Section 6) |
| **Payload visibility** | Nothing leaks to whoever holds the token | Anyone holding it can read every claim (Base64URL is encoding, not encryption) |
| **Size** | Tiny, 20 to 50 characters | Hundreds of bytes; grows with every claim you add |
| **Issuer load** | High: every validation hits the issuer's store | Low: the issuer signs once and is not involved afterward |

Neither family is "the modern one". Both are everywhere, and many systems use each where it fits.

### Real use cases per family

**Opaque: appropriate when revocation speed and secrecy of the payload matter more than
validation cost.**

1. *A banking API.* When a customer reports a stolen phone, the bank kills the session record and
   every token referencing it dies in the same second. The cost: the issuer's token store is now
   on the critical path of every API call, so it needs caching and high availability.
2. *Third-party API tokens you copy from a dashboard.* Most "personal access tokens" for hosted
   services are opaque strings. The provider wants to log, throttle, and revoke per token, which a
   record lookup makes trivial.
3. *A token that might carry sensitive attributes.* If the claims could include medical or HR
   data, an opaque token keeps them off the wire entirely: the holder sees only randomness.

**Self-contained: appropriate when validation must be fast, local, and independent of the
issuer's uptime.**

1. *A microservices cluster with thousands of requests per second.* Each service verifies the
   signature itself; the identity server is not a runtime dependency of every call. The cost:
   revocation lag, which Section 6 prices honestly.
2. *Mobile apps in flaky networks.* The app can check expiry and read claims with no
   connectivity. The cost: everything needed to forge trust must be protected client-side.
3. *Short-lived access tokens between internal services.* Five-minute tokens make the revocation
   problem small enough to live with, and local validation keeps latency near zero.

### The same request, both families: a worked comparison

A hospital records API receives one request: "show the chart for patient 4002". Compare the work:

1. **With an opaque token.** The API extracts `7f3a9c1e...` from the header, calls the identity
   server's introspection endpoint ("is this token active, and what does it carry?"), waits for
   the network round trip, gets back `active: true, sub: usr_01HZX9YQ4E, role: nurse,
   department: cardiology`, then applies its rules. Total added latency: one network call,
   typically 5 to 50 ms. If the identity server is down, the API is down too.
2. **With a JWT.** The API verifies the signature locally (microseconds), reads the same claims
   out of the payload, and applies its rules. No network call. But if the nurse was fired two
   minutes ago, this token still works until its `exp` passes, because nothing about the string
   changed.

**The deciding factors, in order:**

1. *Must revocation take effect in seconds?* Yes points to opaque, or to self-contained with very
   short expiry (the common compromise, Section 6).
2. *Can every consumer afford a network call to the issuer per request?* No points to
   self-contained.
3. *Would readable claims in the token be a data leak?* Yes points to opaque, or to keeping
   sensitive claims out of the JWT.

**Self-check:** Your identity provider has an outage. Which family of already-issued tokens keeps
working during the outage? (Self-contained: validation is local. Opaque tokens fail closed,
because validating them requires asking the downed issuer.)

---

## 3. JWT anatomy: header, payload, signature

**Objective:** read a JWT by hand, part by part and claim by claim, and explain what the
signature does and does not protect.

A **JSON Web Token (JWT)** (RFC 7519, May 2015) is the standard self-contained token format. It
is one string made of three parts joined by dots:

```text
header . payload . signature
eyJhbGci... . eyJpc3Mi... . K8G57Ds7...
```

Each part is **Base64URL**-encoded. Base64URL is ordinary Base64 with two characters swapped
(`-` and `_` replace `+` and `/`) and the padding (`=`) dropped, so the result is safe to put in
a URL or an HTTP header. Crucially: Base64URL is *encoding, not encryption*. Anyone who holds the
token can decode the first two parts with any online decoder or one line of code (you will do it
by hand in Section 13). A JWT is a signed document in a glass envelope: everyone can read it,
nobody can alter it undetected.

Here is a complete, real JWT, which the rest of this section takes apart line by line:

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2lkLmNvcnAuZXhhbXBsZSIsInN1YiI6InVzcl8wMUhaWDlZUTRFIiwiYXVkIjoicGF0aWVudC1yZWNvcmRzIiwiZXhwIjoxNzg4MDAwOTAwLCJpYXQiOjE3ODgwMDAwMDAsIm5hbWUiOiJBZGEgTG92ZWxhY2UiLCJyb2xlIjoibnVyc2UiLCJkZXBhcnRtZW50IjoiY2FyZGlvbG9neSJ9.K8G57Ds7YulgLKYx5MmZJtBwHsBZaz7VUxH-m7BA9U0
```

### Reading it, part by part

**Part 1, the header.** Decoded, the first segment is a small JSON object:

```json
{ "alg": "HS256", "typ": "JWT" }
```

- **`alg`** names the algorithm the signature was made with. `HS256` is HMAC with SHA-256, a
  shared-secret scheme: the same secret signs and verifies. `RS256` (RSA) and `ES256` (ECDSA) are
  the asymmetric schemes: the issuer signs with a private key, everyone verifies with a public
  key. Identity providers use asymmetric schemes so that APIs never hold a secret that could
  sign.
- **`typ`** is just a label saying this is a JWT.

**Part 2, the payload.** Decoded, the second segment is the **claim set**, the actual content:

```json
{
  "iss": "https://id.corp.example",
  "sub": "usr_01HZX9YQ4E",
  "aud": "patient-records",
  "exp": 1788000900,
  "iat": 1788000000,
  "name": "Ada Lovelace",
  "role": "nurse",
  "department": "cardiology"
}
```

Every entry is a **claim** (Section 3 of Part 1 of this series): one asserted fact about the principal. Line by
line:

| Claim | Full name | What it says here |
|---|---|---|
| `iss` | **issuer** | "The identity server at id.corp.example created me" |
| `sub` | **subject** | "This token is about usr_01HZX9YQ4E", the stable internal identifier, not the email (Section 3 of Part 1 of this series) |
| `aud` | **audience** | "I am meant for the patient-records API"; any other recipient should reject me |
| `exp` | **expiration time** | "I stop being valid at Unix time 1788000900", 15 minutes after issue |
| `iat` | **issued at** | "I was created at Unix time 1788000000" |
| `name` | (private claim) | A display name, agreed between this issuer and its consumers |
| `role` | (private claim) | The role claim from the vocabulary of Part 1 of this series, now traveling inside the token |
| `department` | (private claim) | Another private claim, "cardiology" |

The two timestamp claims are plain integers: seconds since 1970-01-01 UTC. `exp - iat = 900`
seconds, a typical 15-minute access token lifetime (Section 6 shows real defaults).

**Part 3, the signature.** The third segment is **not** JSON and does not decode to anything
readable. It is the output of running the `alg` algorithm over the first two segments plus a key:

```text
signature = HS256( base64url(header) + "." + base64url(payload), secret )
```

The signature binds the exact bytes of header and payload. Change one character of the payload
(say, `nurse` to `admin`) and the signature no longer matches, so a verifier rejects the token.
That is the tamper-evidence the wristband analogy promised. What the signature does *not* do:
hide the content. The payload above is readable by anyone, signed or not.

### The three kinds of claims

RFC 7519 sorts claims into three buckets:

- **Registered claims**: the seven names the standard pre-defines so everyone uses them the same
  way: `iss`, `sub`, `aud`, `exp`, `nbf` (not before), `iat`, `jti` (a unique token ID). None is
  mandatory, but when they appear they must mean what the standard says.
- **Public claims**: names anyone may define, but they should be collision-resistant, typically
  a URI like `https://corp.example/claims/department`, so two organizations never invent the same
  name with different meanings.
- **Private claims**: names agreed privately between one issuer and its consumers, like our
  `role` and `department`. Convenient, but they are a contract between specific parties: another
  issuer's `role` may mean something else entirely.

Three practical things to know as a beginner:

- **The payload is public.** Never put secrets, passwords, or personal data you would not print
  on a wristband into a JWT. (There is an encrypted variant, **JWE**, JSON Web Encryption; most
  systems simply keep sensitive claims out instead.)
- **The header is attacker-controlled input.** `alg` tells you how the token *claims* to be
  signed, not how you should verify. Section 5 and Pitfall 2 explain why verifiers must pin the
  algorithm themselves.
- **The signature segment proves origin, not freshness alone.** A perfectly signed token can
  still be expired (`exp` passed) or meant for someone else (`aud` mismatch). Validation is more
  than the signature; that is Section 5.

The signing layer itself has its own standard, **JWS** (JSON Web Signature, RFC 7515); a JWT you
meet in the wild is almost always a JWS carrying a claim set. The two names blur together in
casual speech; "JWT" is what everyone says.

**Self-check:** An attacker steals a JWT from a log file. Can they read the payload? Can they
change `role` to `admin` and keep the token valid? (Read: yes, Base64URL is encoding. Change: no,
any edit breaks the signature, so a correct verifier rejects it. The real risks of stolen tokens
are replay and expiry, covered in Sections 6 and 7.)

---

## 4. Token types: access, refresh, ID

**Objective:** tell the three token types apart and name who consumes each one.

One login usually produces more than one token. The three you will meet constantly, in the order
you will meet them in this series:

| | **Access token** | **Refresh token** | **ID token** |
|---|---|---|---|
| **Answers** | "May this request happen?" | "May I have a new access token?" | "Who just logged in, and how?" |
| **Consumed by** | The API (resource server) | The issuer's token endpoint only | The client app that ran the login |
| **Typical lifetime** | Minutes (5 to 60) | Hours to weeks | Minutes |
| **Typical format** | JWT or opaque | Usually opaque | JWT, always (OIDC, Part 5) |
| **Presented as** | `Authorization: Bearer <token>` header | One-time exchange, server to issuer | Parsed locally, never sent to APIs |

### Details

#### Access token, in detail: the one the API checks

The **access token** is the working credential of every API call after login. It is a **bearer
token** (RFC 6750): like cash, whoever bears it can spend it. Nothing ties it to the holder's
machine beyond possession, which is why theft and storage (Section 7) matter so much. The API
validates it (Section 5) and then authorizes using the claims inside: "token says
`role: nurse`, patient 4002 is in cardiology, allowed".

#### Refresh token, in detail: the one that is never shown to APIs

When the 15-minute access token dies, logging the user in again every 15 minutes would be
unusable. The **refresh token** solves this: a long-lived token the client sends only to the
issuer's **token endpoint** to get a fresh access token (and usually a fresh refresh token).
Because it is long-lived and powerful, it gets the strictest handling: stored as safely as the
client can manage, sent to exactly one URL, and rotated on every use in modern setups (Section
6). An API that receives a refresh token should refuse it; it is not for them.

#### ID token, in detail: the one that proves a login happened

The **ID token** is defined by OpenID Connect (Part 5) and is always a JWT with a fixed claim
set. Its audience is the *client application*, not an API: it tells the app "the person who just
logged in is usr_01HZX9YQ4E, authenticated with MFA, at this time". The beginner mistake is
sending it to APIs as proof of authorization. It is not that; the access token is for APIs. Depth
(its claims, `nonce`, validation rules) is deferred to Part 5, Section 3; for now, file it as
"the login receipt".

### Real use cases

1. *SPA calling a orders API.* The browser holds an access token and sends it on every request;
   a refresh token quietly renews it in the background. The ID token told the SPA who logged in
   so it can render "Hi, Ada".
2. *CLI tool talking to a cloud API.* The CLI exchanges a refresh token for a short-lived access
   token at startup, so a stolen access token from a shell history is useless in minutes.
3. *Counter-example, a dashboard "API key".* That long random string you paste into a config
   file is none of the three: it is a long-lived opaque credential identifying an application,
   not a user session. Part 8 of this series is entirely about that case.

**Self-check:** A request to the records API carries a token in the `Authorization` header. Which
of the three types should it be, and where should the other two be at that moment? (The access
token. The refresh token should only ever travel between the client and the issuer's token
endpoint; the ID token's job ended when the app learned who logged in.)

---

## 5. Validating a token correctly

**Objective:** list the checks a correct validator performs, in order, and explain why "decoding"
is not one of them.

Receiving a JWT and *reading* it takes one line of code, which is exactly the trap. Reading is
decoding; trusting requires verifying. A correct validator runs these checks and rejects the
token if any fails:

1. **Verify the signature** against a key you obtained out of band (a shared secret you
   configured, or the issuer's public key from its published key set). Until this passes, every
   claim in the payload is unverified gossip.
2. **Pin the algorithm.** Accept only the algorithm you expect (for example `algorithms=
   ["RS256"]`), never the one the token's header suggests. Pitfall 2 shows the attack this
   blocks.
3. **Check the times.** `exp` must be in the future; if present, `nbf` must be in the past;
   `iat` should be sane. Allow a small clock skew (30 to 60 seconds) because no two servers agree
   perfectly on the time.
4. **Check `iss`.** The issuer must be exactly the identity server you trust, string-equal.
5. **Check `aud`.** Your own identifier must appear in the audience, otherwise the token was
   minted for a different service and you are the victim of token replay between APIs.

Only after all five does the payload become trustworthy input to authorization.

Bad-then-good, using the Python `PyJWT` library you will run in Section 13:

```python
# Bad: decoding without verifying. This reads attacker-controlled bytes and trusts them.
claims = jwt.decode(token, options={"verify_signature": False})
if claims["role"] == "admin":      # anyone can write "admin" into an unsigned payload
    allow()

# Good: verify signature, algorithm, expiry, audience, and issuer first.
claims = jwt.decode(
    token, key,
    algorithms=["RS256"],
    audience="patient-records",
    issuer="https://id.corp.example",
)
if claims["role"] == "admin":      # now the claim is backed by the issuer's signature
    allow()
```

The Bad version is not an exotic mistake; it is the single most common JWT error, because every
stack overflow answer about "reading" a token looks almost identical to the correct code. It is
Pitfall 1 in Section 14.

One more honesty note: with asymmetric algorithms (`RS256`, `ES256`) the verifier needs the
issuer's *public* key, which identity servers publish at a **JWKS** endpoint (a JSON Web Key
Set). Fetching and caching those keys is plumbing your JWT library or framework does for you;
the endpoint itself is explained in Part 5, Section 4, and exercised in Part 6. You do not need
it for Section 13, which uses a shared-secret demo key.

**Self-check:** A token has a valid signature, a future `exp`, and the right `iss`, but its `aud`
is `billing-api` and you are `patient-records`. Accept or reject? (Reject: a token minted for one
API must not unlock another. This is what `aud` exists for.)

---

## 6. The token lifecycle (the honest part)

**Objective:** describe the five lifecycle stages and state, with real numbers, why revocation is
the price stateless tokens charge for their speed.

A token is not a static artifact; it has a life. The five stages:

| Stage | What happens | What can go wrong |
|---|---|---|
| **Issuance** | The issuer authenticates the user, builds the claim set, signs it | Over-stuffed claims (token bloat), wrong `aud` |
| **Transport and use** | The client attaches the token to requests | Leakage in logs, URLs, browser history (Section 7) |
| **Expiry** | `exp` passes; verifiers reject the token from then on | Too-long lifetimes turn every theft into a long incident |
| **Refresh** | The client trades the refresh token for a new access token | Stolen refresh token mints access tokens at will |
| **Revocation** | The issuer declares a token dead *before* its `exp` | With stateless JWTs, there is nothing to delete |

### Expiry and refresh: the standard compromise

Short-lived access tokens plus a refresh token is the industry compromise between Section 2's two
rows: you get local, fast validation of access tokens, and revocation that takes effect within
one access-token lifetime, because the issuer can simply refuse the next refresh. Real defaults,
so you can calibrate (as of August 2026; both are configurable, verify before building):

- **Keycloak 26.x** (the self-hosted IdP this series uses from Part 4 on): access token lifespan
  **5 minutes** per realm default; SSO session idle timeout 30 minutes, max 10 hours, which bounds
  how long refresh tokens keep working.
- **AWS Cognito**: access and ID tokens **1 hour** by default (configurable from 5 minutes to 1
  day); refresh token **30 days** by default (configurable from 1 hour to 10 years).

The security guidance agrees with the short end: RFC 9700, the OAuth 2.0 Security Best Current
Practice (January 2025), recommends keeping access-token lifetimes short, minutes rather than
hours, precisely to shrink the revocation window.

**Refresh token rotation** hardens the refresh stage: every refresh exchange returns a *new*
refresh token and invalidates the old one. If an attacker and the real user both try to spend the
same refresh token, the issuer sees the second use of a dead token, concludes theft, and kills
the whole family. Cost: a client that loses the newest refresh token (crashed before saving it)
is logged out.

### The revocation problem, honestly priced

Here is the cost the marketing leaves out of "stateless validation is fast": **a self-contained
token cannot be recalled.** The festival cannot un-print a wristband; it can only tell gate staff
a serial number to watch for. In software you have exactly three options, and each reintroduces
part of what statelessness saved you from:

1. **Short expiry plus refresh refusal.** Do nothing per-token; let `exp` be the kill switch and
   control everything at the refresh exchange. Cost: a revoked user keeps working access for up
   to one access-token lifetime. With a 60-minute token, that is up to **60 minutes of access
   after you pressed "disable"**, an eternity for the leaver scenario of Section 5 of Part 1 of
   this series. With
   a 5-minute token, the worst case is 5 minutes, which most systems accept.
2. **A denylist.** Verifiers check each incoming `jti` against a list of revoked token IDs. Works
   instantly, but now every validation needs a fast lookup against shared state: you rebuilt a
   slice of the opaque token's architecture. Mitigations: the list only needs entries younger
   than the max token lifetime, and it lives in a cache like Redis.
3. **Introspection for high-risk operations.** Keep stateless validation for ordinary requests,
   but call the issuer before sensitive ones (large payments, admin actions). Cost: the issuer is
   back on the critical path for exactly the calls you most care about.

This is why Section 2 refused to crown a winner: "JWT vs opaque" is really "which revocation
window can you tolerate, and what will you pay to shrink it".

**Self-check:** An admin disables a contractor at 14:00. The system uses 15-minute access tokens
and refresh rotation. What is the latest moment the contractor's already-issued access token can
still work, and what stops the damage from continuing after that? (14:15 at the latest, when the
last issued token expires. After that, renewal requires the refresh token, which the issuer now
refuses.)

---

## 7. Transport and storage basics

**Objective:** state the non-negotiable transport rules and name the browser storage options with
their one-line trade-offs, ahead of the full treatment in Part 6.

Tokens are bearer instruments (Section 4): a copy is as good as the original. So the rules of
moving and keeping them are short and strict.

**Transport rules:**

- **TLS, always.** Tokens cross the network only over HTTPS. RFC 6750 makes this a hard
  requirement, not a suggestion: without **TLS** (Transport Layer Security), anyone on the network
  path can lift the token and replay it.
- **Headers, not URLs.** Send tokens in the `Authorization: Bearer <token>` header. URLs get
  written into server logs, browser history, proxy logs, and `Referer` headers, each one a copy
  of your token in a place you do not control.

**Storage, the preview.** Where a browser app keeps its tokens is genuinely hard, and Part 6,
Section 6 spends a full section on it. For now, the one-line map:

| Option | The catch |
|---|---|
| **Memory only** (a JS variable) | Safest against theft, but a page reload logs the user out unless you refresh silently |
| **`localStorage`** | Survives reloads, but any **cross-site scripting (XSS)** hole in your page hands the token to injected JavaScript |
| **`HttpOnly` cookie** | JavaScript cannot read it (XSS-resistant), but it is sent automatically, so you must defend against **cross-site request forgery (CSRF)** instead |

The scale of the leakage problem, so the rules do not feel pedantic: GitGuardian's 2024 *State of
Secrets Sprawl* report found **12.8 million** new secrets (API keys, tokens, credentials) exposed
in public GitHub commits in 2023 alone. Tokens leak less through cryptographic failure than
through boring places: logs, URLs, screenshots, and repos. Treat every copy as a liability and
every lifetime as a countdown.

**Self-check:** A developer moves tokens from URLs into headers and from plaintext config into an
environment variable. Which of the two leak channels from this section did each change close?
(URLs to headers: logs, history, and referers. Config to env var: accidental commits of the
secret into source control.)

---

# Part 2: The Landscape (token formats)

Tokens are not all JWTs. This Part surveys the formats you will actually meet, version-stamped as
of August 2026, because this Part goes stale first.

## 8. The map: three lanes

| Lane | What it is | Where you meet it |
|---|---|---|
| **A. JWT** | The standard self-contained, signed token format | Modern IdPs (Keycloak, Entra ID, Cognito), OIDC, most new APIs |
| **B. Opaque (reference) tokens** | Random strings whose meaning lives at the issuer | Third-party API tokens, refresh tokens, high-security banking flows |
| **C. Alternative formats** | Newer or older designs solving JWT's irritations | PASETO in security-sensitive niches; SAML assertions in enterprise SSO |

The lanes coexist inside one system more often than not: a typical OIDC login issues a JWT access
token, an opaque refresh token, and a JWT ID token at the same time.

---

## 9. Lane A: JWT

**What it is.** The format of Section 3: three Base64URL parts, signed claims, defined by RFC
7519 (2015) with the signing layer in RFC 7515 (JWS) and an encrypted variant in RFC 7516 (JWE).
The operational rules that make it safe in practice are collected in RFC 8725, *JSON Web Token
Best Current Practices* (February 2025).

**Who it is for.** Any system where verifiers should validate locally without calling the issuer:
distributed APIs, microservices, mobile clients, and every OIDC deployment (ID tokens are always
JWTs).

**What it costs you.** The revocation window of Section 6, payload visibility (no secrets in
claims), size that grows with your claim appetite, and a verification step that is easy to get
subtly wrong (Pitfalls 1 and 2). Use a maintained library; never hand-roll the cryptography.

**Version landmarks (as of August 2026).** RFC 7519 (2015) is unchanged and stable; RFC 8725
(2025) is the current best-practice document; PyJWT 2.x, `jose` (JavaScript) 5.x/6.x, and
Spring Security's resource-server support are the maintained library lines this series uses.

Flavor sketch, the artifact itself:

```text
eyJhbGci...   <- header:   {"alg":"RS256","typ":"JWT"}
.eyJpc3Mi...  <- payload:  {"iss","sub","aud","exp",...}
.K8G57Ds7...  <- signature over the first two parts; not JSON, not readable
```

---

## 10. Lane B: Opaque (reference) tokens

**What it is.** A random string with enough entropy to be unguessable (128 bits minimum is the
common rule), stored hashed or indexed at the issuer alongside its claims. Verifiers resolve it
through **token introspection** (RFC 7662, October 2015): an HTTP call that returns
`active: true` plus the claims, or `active: false`.

**Who it is for.** Systems where immediate revocation beats validation cost: banking and payment
APIs, third-party developer tokens, and nearly every refresh token in existence (the refresh
token only ever talks to its issuer anyway, so local validation buys it nothing).

**What it costs you.** A network dependency and a hot lookup store on every validation, plus the
issuer's availability becoming your availability (Section 2's worked comparison priced this at 5
to 50 ms and a shared failure domain).

**Version landmarks (as of August 2026).** RFC 7662 introspection is the stable standard; major
providers (Auth0, Keycloak, Cognito) all expose it. GitHub's fine-grained personal access tokens
and Stripe's API keys are visible real-world examples of the pattern.

Flavor sketch, an introspection exchange:

```http
POST /introspect                <- verifier asks the issuer
token=7f3a9c1e...

{ "active": true,               <- issuer answers
  "sub": "usr_01HZX9YQ4E",
  "role": "nurse",
  "exp": 1788000900 }
```

---

## 11. Honorable mentions

- **PASETO** (Platform-Agnostic Security Tokens). JWT's security-conscious redesign: instead of a
  free-for-all `alg` header, you pick a versioned suite (like `v4.public`), so the `alg=none` and
  algorithm-confusion bugs of Pitfall 2 are impossible by construction. The cost: a much smaller
  ecosystem and library selection than JWT's. Worth knowing; rarely the default.
- **SAML assertions.** XML documents, signed, carrying identity and attribute claims: the
  token-like artifact of enterprise SSO since 2005. Conceptually they are self-contained tokens
  wearing XML; Part 3 of this series positions SAML against the modern protocols.
- **JWE (encrypted JWTs).** When the payload itself must be confidential, not just signed. Rare
  in practice: most systems instead keep sensitive claims out of the token.
- **Macaroons and Biscuit tokens.** Research-grade formats where the holder can *attenuate* a
  token (add restrictions) before passing it on. Elegant, small adoption; file under "good to
  recognize".

---

# Part 3: Putting It Into Practice

## 12. How to choose: JWT vs opaque

| Your situation | Start with |
|---|---|
| Internal microservices, high request rate, one trust domain | **JWT**: local validation keeps the IdP off the hot path; keep lifetimes at 5 to 15 minutes |
| Banking, payments, admin consoles, anything where "disable now" must mean now | **Opaque**, or JWT plus introspection on the sensitive calls |
| Third-party developers calling your public API | **Opaque**: per-token logging, throttling, and instant revocation are the product (depth in Part 8) |
| OIDC login for a user-facing app | **JWT**, no choice: the ID token is a JWT by definition (Part 5) |
| Refresh tokens, always | **Opaque**: they only talk to the issuer, so self-containment buys nothing |
| Claims would contain data you must not show the client | **Opaque**, or JWT with the sensitive claims removed |

Two practical truths:

1. **You will run both.** Real systems mix families per token type (JWT access, opaque refresh)
   and per risk level (stateless for reads, introspection for dangerous writes). Choosing a
   family is a per-artifact decision, not a company tattoo.
2. **Lifetime is a security control, not a performance knob.** Every minute on an access token's
   `exp` is a minute added to your worst-case revocation window (Section 6). Set the lifetime
   from your tolerance for stale access, then let refresh tokens absorb the convenience cost.

---

## 13. Optional hands-on track: decode a JWT by hand, then sign and verify one

**Objective:** prove to yourself that anyone can read a JWT, and that verifying is a separate,
library-backed step. Project root: `hands-on/part-02/`.

You will decode the Section 3 token using nothing but Python's standard library, then sign and
verify tokens with a real library, and finally watch a correct validator reject a tampered token
and an expired one.

### Step 1: Set up the environment

Requires Python 3.10 or newer.

```bash
mkdir -p hands-on/part-02 && cd hands-on/part-02
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install PyJWT
```

Verify the installation:

```bash
python -c "import jwt; print(jwt.__version__)"
# Expected output: a version like 2.10.x or newer (any 2.x is fine)
```

### Step 2: Decode by hand, no library (this is why payloads are public)

Create `decode_by_hand.py`:

```python
# Decode a JWT with nothing but the standard library. No verification happens here.
import base64, json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2lkLmNvcnAuZXhhbXBsZSIsInN1YiI6InVzcl8wMUhaWDlZUTRFIiwiYXVkIjoicGF0aWVudC1yZWNvcmRzIiwiZXhwIjoxNzg4MDAwOTAwLCJpYXQiOjE3ODgwMDAwMDAsIm5hbWUiOiJBZGEgTG92ZWxhY2UiLCJyb2xlIjoibnVyc2UiLCJkZXBhcnRtZW50IjoiY2FyZGlvbG9neSJ9.K8G57Ds7YulgLKYx5MmZJtBwHsBZaz7VUxH-m7BA9U0"

header_b64, payload_b64, signature_b64 = token.split(".")

def decode_segment(segment):
    segment += "=" * (-len(segment) % 4)  # restore the padding Base64URL omits
    return json.loads(base64.urlsafe_b64decode(segment))

print("header: ", decode_segment(header_b64))
print("payload:", decode_segment(payload_b64))
print("signature (not JSON, stays Base64URL):", signature_b64)
```

Run it:

```bash
python decode_by_hand.py
# Expected output:
# header:  {'alg': 'HS256', 'typ': 'JWT'}
# payload: {'iss': 'https://id.corp.example', 'sub': 'usr_01HZX9YQ4E', 'aud': 'patient-records', 'exp': 1788000900, 'iat': 1788000000, 'name': 'Ada Lovelace', 'role': 'nurse', 'department': 'cardiology'}
# signature (not JSON, stays Base64URL): K8G57Ds7YulgLKYx5MmZJtBwHsBZaz7VUxH-m7BA9U0
```

That is the entire "glass envelope" lesson: five lines of standard library, no key, no
permission, full contents. Decoding is not verifying.

### Step 3: Sign and verify with a real library

Create `make_token.py`:

```python
# Sign and verify a JWT with a real library. Verification IS the point of this step.
import time
import jwt

secret = "demo-secret-key-for-the-hands-on-track-01"  # demo only; real keys live in a vault
now = int(time.time())
payload = {
    "iss": "https://id.corp.example",
    "sub": "usr_01HZX9YQ4E",
    "aud": "patient-records",
    "iat": now,
    "exp": now + 900,  # 15-minute access token
    "name": "Ada Lovelace",
    "role": "nurse",
    "department": "cardiology",
}

token = jwt.encode(payload, secret, algorithm="HS256")
print("token:", token)

claims = jwt.decode(
    token, secret,
    algorithms=["HS256"],              # pin the algorithm, never read it from the token
    audience="patient-records",        # we are the API this token is meant for
    issuer="https://id.corp.example",  # and this is who we trust to issue it
)  # verifies signature, exp, aud, and iss in one call
print("verified:", claims["sub"], "|", claims["name"], "| role:", claims["role"])
```

Run it:

```bash
python make_token.py
# Expected output (your token, iat, and exp differ, they are stamped at runtime):
# token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.<payload>.<signature>
# verified: usr_01HZX9YQ4E | Ada Lovelace | role: nurse
```

Note what the `jwt.decode` call enforced for free: signature, algorithm pinning, expiry, `aud`,
and `iss`. Try deleting the `audience=` argument and rerunning: PyJWT refuses the token with
`InvalidAudienceError`, because a token carrying `aud` must be checked against it. That is
Section 5's checklist working.

### Step 4: Break it on purpose, and watch the validator refuse

Create `break_token.py`:

```python
# Two ways a token must fail. If either test prints "ACCEPTED", the validator is broken.
import jwt

secret = "demo-secret-key-for-the-hands-on-track-01"

# Test 1: a valid token with ONE character of the signature changed
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2lkLmNvcnAuZXhhbXBsZSIsInN1YiI6InVzcl8wMUhaWDlZUTRFIiwiYXVkIjoicGF0aWVudC1yZWNvcmRzIiwiZXhwIjoxNzg4MDAwOTAwLCJpYXQiOjE3ODgwMDAwMDAsIm5hbWUiOiJBZGEgTG92ZWxhY2UiLCJyb2xlIjoibnVyc2UiLCJkZXBhcnRtZW50IjoiY2FyZGlvbG9neSJ9.K8G57Ds7YulgLKYx5MmZJtBwHsBZaz7VUxH-m7BA9U0"
tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
try:
    jwt.decode(tampered, secret, algorithms=["HS256"])
    print("tampered token: ACCEPTED (this should never happen)")
except jwt.InvalidSignatureError as e:
    print("tampered token: rejected -", e)

# Test 2: a correctly signed token whose exp lies in the past
expired = jwt.encode(
    {"sub": "usr_01HZX9YQ4E", "iat": 1699999000, "exp": 1700000000},
    secret, algorithm="HS256",
)
try:
    jwt.decode(expired, secret, algorithms=["HS256"])
    print("expired token: ACCEPTED (this should never happen)")
except jwt.ExpiredSignatureError as e:
    print("expired token: rejected -", e)
```

Run it:

```bash
python break_token.py
# Expected output:
# tampered token: rejected - Signature verification failed
# expired token: rejected - Signature has expired
```

One changed character, and the token is garbage; one second past `exp`, and the same. If you want
the full experience, paste the Step 3 token into a browser decoder (for example the jwt.io
debugger) and edit `role` to `admin` in the payload: the site instantly flags the signature as
invalid. You have now done, by hand, everything Section 5 demands of a production validator.

---

## 14. Common misconceptions and pitfalls

**Pitfall 1: "I decoded the token, so it is verified."**
Symptom: anyone can mint a "token" with `role: admin` and your API believes it. Cause: the code
called a decode/read function (or passed `verify_signature: False`) and treated the result as
trusted. Fix: one decode call that verifies signature, algorithm, `exp`, `aud`, and `iss`, as in
Section 13 Step 3; re-read Section 5.

**Pitfall 2: "The token's header tells me how to verify it."**
Symptom: tokens signed with `alg: none`, or with the *public* key misused as an HMAC secret, pass
validation. Cause: the verifier trusted the attacker-controlled `alg` header instead of pinning
its own algorithm list; this is the `alg=none` and **algorithm confusion** family, which RFC 8725
exists specifically to kill. Fix: always pass an explicit allow-list, for example
`algorithms=["RS256"]`, and never accept `none`; re-read Section 5.

**Pitfall 3: "localStorage is a fine place for tokens."**
Symptom: one XSS hole anywhere in the frontend (a vulnerable dependency, an unescaped template)
exfiltrates every user's tokens. Cause: anything in `localStorage` is readable by any JavaScript
running on the page. Fix: prefer memory or an `HttpOnly` cookie with CSRF defenses; the full
trade-off table is Part 6, Section 6; re-read Section 7.

**Pitfall 4: "Just add one more claim to the token."**
Symptom: requests start failing with `431 Request Header Fields Too Large`, or login breaks for
users with many roles. Cause: JWTs travel in HTTP headers, and common server defaults cap header
blocks around 8 KB (nginx) to 16 KB; browsers cap cookies near 4 KB each. A token carrying every
role and permission can outgrow the pipe that carries it. Fix: keep tokens lean (identity plus
coarse roles) and put fine-grained permissions in the application, which is exactly Part 7's
subject; re-read Section 3.

**Pitfall 5: "Long-lived tokens are more convenient, so set exp to 30 days."**
Symptom: a stolen token or a departed contractor keeps working for weeks after you acted. Cause:
`exp` is the only kill switch a stateless token has; you traded your entire revocation window for
fewer refreshes. Fix: short access tokens (minutes), refresh tokens for continuity, rotation to
detect theft; re-read Section 6.

---

# Part 4: Reference

## 15. Advanced topics and learning path

**Recommended learning order:** Part 3 of this series (SSO) to Part 4 (OAuth 2.0) to Part 5
(OIDC). You now understand the artifact; next you learn the user-facing goal that needs it (one
login, many apps), then the protocol that issues tokens (OAuth), then the layer that proves who
logged in (OIDC).

**Direction 1: Single sign-on** | Difficulty: Beginner
The very next part, `003-single-sign-on-sso.md`: how one login at a central identity provider
unlocks many applications, and what it costs when that one account is compromised.

**Direction 2: The specs behind this tutorial** | Difficulty: Intermediate
RFC 7519 (JWT) is short and readable, and RFC 8725 (JWT Best Current Practices, 2025) reads like
a guided tour of every way Section 5 can go wrong. Reading both after this tutorial is a few
hours well spent.

**Direction 3: Encrypted and attenuated tokens** | Difficulty: Advanced
JWE (RFC 7516) for confidential payloads, and macaroons/Biscuits for tokens the holder can
restrict before passing on. Niche today, but they answer real limitations you met in Sections 3
and 11.

**Hands-on project suggestions:**

1. **Extend Section 13**: add `nbf` and `jti` to the payload, then write a 20-line denylist check
   that rejects a revoked `jti` even when the signature and `exp` are valid. Concepts: Sections 3,
   5, 6.
2. **Lifetime experiment**: set `exp` to 10 seconds in `make_token.py`, sleep 11 seconds, and
   verify. Concepts: Section 6, clock skew.
3. **Claim diet audit**: take any JWT from a system you use (paste it into a local decoder, never
   an online one for production tokens) and list which claims an API actually needs vs which are
   ballast. Concepts: Sections 3, Pitfall 4.

**Best practices:**

- Verify before you trust: signature, pinned algorithm, `exp`/`nbf`, `iss`, `aud`, in one
  library call, on every request.
- Keep access tokens short (minutes) and let refresh tokens carry continuity.
- Never put secrets or sensitive personal data in a JWT payload; it is signed, not sealed.
- Transport tokens only over TLS, in headers, never in URLs.
- Use a maintained JWT library; never hand-roll signature code.
- Treat any token copy in a log, URL, or repo as a live credential and rotate accordingly.

---

## 16. Cheatsheet

**Definition:** A token is a portable, tamper-evident proof that an authentication already
happened: a string the issuer creates once, the holder presents many times, and the receiver can
check without re-running the login.

**JWT anatomy:**

```text
header.payload.signature, each part Base64URL-encoded (encoding, NOT encryption)
header  = {"alg":"RS256","typ":"JWT"}        # how it was signed
payload = {"iss","sub","aud","exp",...}      # the claims, readable by anyone
signature = sign(header + "." + payload, key) # tamper-evidence only, hides nothing
```

**Validation checklist (all five, every request):**

```text
1. signature valid against YOUR key?   4. iss == the issuer you trust?
2. algorithm == your pinned allow-list? 5. your identifier in aud?
3. exp in future, nbf in past (skew ok)   fail any -> reject
```

**Token types:** access (for APIs, minutes, bearer) - refresh (for the issuer only, long-lived,
rotate it) - ID (for the client app, proof of login, JWT, Part 5).

**Lifecycle:** issue - use - expire - refresh - revoke. Stateless JWTs cannot be recalled;
revocation = short `exp` + refuse refresh, or a denylist, or introspection.

**Key number:** 12.8 million secrets leaked in public GitHub commits in 2023 alone (GitGuardian
2024); and a 60-minute access token means up to 60 minutes of access after you press "disable",
which is why Keycloak defaults to 5.

**Version landmarks (as of August 2026):**

| Thing | Milestone |
|---|---|
| JWT / JWS / JWE | RFC 7519 / 7515 / 7516 (May 2015), stable |
| Bearer tokens in requests | RFC 6750 (October 2012): TLS mandatory, headers not URLs |
| Token introspection | RFC 7662 (October 2015) |
| JWT best practices | RFC 8725 (February 2025): pin algorithms, never `none` |
| OAuth 2.0 Security BCP | RFC 9700 (January 2025): short-lived access tokens |
| Keycloak | 26.x: access token default 5 min, SSO session idle 30 min (verify before building) |
| AWS Cognito | access/ID default 1 hour, refresh default 30 days (verify before building) |
| PyJWT | 2.x, the library used in Section 13 |

**Quick troubleshooting:**

| Symptom | Likely cause | Quick fix |
|---|---|---|
| API accepts forged claims | Decode without verify | Verify signature + pin algorithm; re-read Section 5 |
| `InvalidAudienceError` / 401 with valid-looking token | `aud` not checked, or token minted for another API | Pass `audience=`; re-read Section 5 |
| Tokens accepted with `alg: none` | Verifier trusts the header's `alg` | Allow-list algorithms; re-read Pitfall 2 |
| 431 errors, login fails for users with many roles | Token too big for header limits | Slim the claims; re-read Pitfall 4 |
| Disabled user keeps access for minutes/hours | Stateless JWT revocation window | Shorten `exp`, refuse refresh, denylist for hot cases; re-read Section 6 |
| Token found in server logs or browser history | Token in URL | Move to `Authorization` header, rotate the leaked token; re-read Section 7 |

---

## Appendix

### Glossary

| Term | Definition |
|---|---|
| **Token** | A portable, tamper-evident proof that an authentication already happened, presented to systems that did not run the login |
| **Credential** | The secret presented to authenticate (password, key); a token is what you get back afterward (Section 3 of Part 1 of this series) |
| **Opaque token (reference token)** | A random string with no readable content; validating it requires asking the issuer |
| **Self-contained token** | A token carrying its claims and a signature, validatable locally without calling the issuer |
| **Token introspection** | The RFC 7662 call a verifier makes to ask the issuer whether an opaque token is active and what it carries |
| **JSON Web Token (JWT)** | The standard self-contained token format (RFC 7519): header.payload.signature, Base64URL-encoded |
| **Base64URL** | URL-safe Base64 (`-` and `_` replace `+` and `/`, no padding); encoding, not encryption |
| **Header** | The first JWT segment: JSON naming the signing algorithm and type |
| **`alg`** | The header field naming the signing algorithm the token *claims* to use; verifiers must ignore it and pin their own allow-list |
| **`typ`** | The header field labeling the token type, almost always `JWT` |
| **Payload (claim set)** | The second JWT segment: the JSON claims the token asserts |
| **Signature** | The third JWT segment: the cryptographic output binding header and payload to a key; tamper-evidence, not confidentiality |
| **Claim** | One asserted fact about a principal inside a token (`role: nurse`), trustworthy only after signature verification |
| **Registered claim** | One of the seven claim names pre-defined by RFC 7519: `iss`, `sub`, `aud`, `exp`, `nbf`, `iat`, `jti` |
| **Public claim** | A claim name anyone may define, expected to be collision-resistant (typically a URI) |
| **Private claim** | A claim name agreed privately between one issuer and its consumers, like `department` |
| **Issuer (`iss`)** | The registered claim naming who created and signed the token |
| **Subject (`sub`)** | The registered claim naming who the token is about, ideally a stable internal identifier |
| **Audience (`aud`)** | The registered claim naming who the token is intended for; other recipients must reject it |
| **Expiration time (`exp`)** | The registered claim giving the Unix timestamp after which the token must be rejected |
| **Not before (`nbf`)** | The registered claim giving the Unix timestamp before which the token must be rejected |
| **Issued at (`iat`)** | The registered claim giving the Unix timestamp when the token was created |
| **`jti`** | The registered claim carrying a unique token ID, used by denylists |
| **JWS (JSON Web Signature)** | RFC 7515, the signing layer under the JWTs you actually meet |
| **JWE (JSON Web Encryption)** | RFC 7516, the encrypted JWT variant for confidential payloads |
| **JWKS** | JSON Web Key Set, the published set of issuer public keys a verifier fetches to check signatures (depth in Part 5) |
| **Access token** | The token presented to APIs on each request; short-lived, usually a bearer token |
| **Refresh token** | The long-lived token exchanged only with the issuer's token endpoint for new access tokens |
| **ID token** | The OIDC token proving to the client app who logged in; always a JWT; depth in Part 5 |
| **Bearer token** | A token usable by whoever holds it, like cash (RFC 6750) |
| **Token endpoint** | The issuer's URL where refresh tokens are exchanged and new tokens are issued |
| **Token lifecycle** | The five stages: issuance, transport/use, expiry, refresh, revocation |
| **Refresh token rotation** | Issuing a new refresh token on every use and invalidating the old one, so reuse signals theft |
| **Revocation** | Declaring a token dead before its `exp`; trivial for opaque tokens, impossible for stateless JWTs without extra machinery |
| **Denylist** | A shared list of revoked token IDs (`jti`) that verifiers consult, restoring instant revocation at the cost of shared state |
| **Algorithm confusion** | The attack where a verifier trusts the token's `alg` header, letting attackers downgrade to `none` or misuse public keys as HMAC secrets |
| **TLS (Transport Layer Security)** | The encrypted transport (HTTPS) tokens must never cross the network without |
| **`localStorage`** | Browser key-value storage readable by any JavaScript on the page, hence exposed to XSS |
| **HttpOnly cookie** | A cookie JavaScript cannot read, shipped automatically with requests, hence exposed to CSRF instead |
| **Cross-site scripting (XSS)** | Attacker JavaScript running in your page's origin, able to read anything the page's scripts can read |
| **Cross-site request forgery (CSRF)** | Tricking a browser into sending its automatic credentials (cookies) to your site from a malicious one |
| **PASETO** | Platform-Agnostic Security Tokens: a JWT alternative with versioned algorithm suites instead of a free-form `alg` header |
| **SAML assertion** | The signed XML identity artifact of enterprise SSO; conceptually a self-contained token in XML |

### Sources (as referenced in this tutorial)

- IETF, RFC 7519, "JSON Web Token (JWT)" (May 2015): the format, the seven registered claims, the
  three claim buckets.
- IETF, RFC 7515, "JSON Web Signature (JWS)" and RFC 7516, "JSON Web Encryption (JWE)" (May
  2015): the signing and encryption layers.
- IETF, RFC 6750, "The OAuth 2.0 Authorization Framework: Bearer Token Usage" (October 2012):
  bearer semantics, TLS requirement, the `Authorization` header.
- IETF, RFC 7662, "OAuth 2.0 Token Introspection" (October 2015): the opaque-token validation
  call.
- IETF, RFC 8725, "JSON Web Token Best Current Practices" (February 2025): pin algorithms, never
  accept `none`, explicit key typing.
- IETF, RFC 9700, "Best Current Practice for OAuth 2.0 Security" (January 2025): short-lived
  access tokens, refresh token rotation and sender-constraining.
- Keycloak, "Server Administration Guide", 26.x (accessed August 2026): default access token
  lifespan 5 minutes, SSO session idle 30 minutes, max 10 hours.
- AWS, "Amazon Cognito Developer Guide" (accessed August 2026): access and ID token default
  validity 1 hour, refresh token default 30 days, configurable ranges.
- GitGuardian, "State of Secrets Sprawl 2024" (March 2024): 12.8 million new secrets detected in
  public GitHub commits in 2023.
- Paragon Initiative Enterprises, "PASETO: Platform-Agnostic Security Tokens" (paseto.io,
  accessed August 2026): versioned protocol suites as the alternative to JWT's `alg` header.

*Note: this tutorial reflects the field as of August 2026. Product defaults (Keycloak, Cognito)
and library versions drift, and the GitGuardian figure is republished annually; verify
version-specific claims against official documentation before building on them.*
