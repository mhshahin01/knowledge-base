# Keycloak from Zero: A Foundational Tutorial

*For absolute beginners. No prior knowledge of IAM, SSO, OAuth or Keycloak assumed.*
*Tested against Keycloak 26.7.3 on Docker. Commands are written for Windows PowerShell.*

---

## Table of contents

**Part A – The ideas (read first, no computer needed)**

1. [What problem does Keycloak solve?](#1-what-problem-does-keycloak-solve)
2. [The vocabulary you cannot skip](#2-the-vocabulary-you-cannot-skip)
3. [The building blocks, one by one](#3-the-building-blocks-one-by-one)
   - 3.1 Realms · 3.2 Users · 3.3 Groups · 3.4 Roles (realm roles & client roles) · 3.5 Clients · 3.6 Client scopes · 3.7 Sessions · 3.8 Events · 3.9 Realm settings · 3.10 Authentication (flows) · 3.11 Identity providers · 3.12 User federation
4. [How the blocks fit together (one picture)](#4-how-the-blocks-fit-together)
5. [Tokens: what your app actually receives](#5-tokens-what-your-app-actually-receives)

**Part B – Hands on (Docker + PowerShell)**

6. [Install Docker and run Keycloak](#6-install-docker-and-run-keycloak)
7. [Your first realm, user and login (clicking in the Admin Console)](#7-your-first-realm-user-and-login)
8. [Build the "ACME Corp" realm with a script](#8-build-the-acme-corp-realm-with-a-script)
9. [Client types, one by one, with working Python code](#9-client-types-one-by-one)
   - 9.1 Backend REST API · 9.2 Single-Page App · 9.3 Mobile / desktop app · 9.4 Server-side web app · 9.5 Machine-to-machine · 9.6 CLI tools & device flow · 9.7 "API keys" · 9.8 Cheat sheet
10. [Real-world use cases and which blocks they touch](#10-real-world-use-cases)
11. [Identity providers & user federation in practice](#11-identity-providers--user-federation-in-practice)
12. [Integrating with ELK (Elasticsearch, Logstash, Kibana)](#12-integrating-with-elk)
13. [Production checklist](#13-production-checklist)
14. [Troubleshooting](#14-troubleshooting)
15. [Glossary](#15-glossary)

Companion files (in the `examples/` and `docker/` folders next to this document):

| File | What it is |
|---|---|
| `examples/setup_realm.py` | Builds the whole ACME realm in 5 seconds (users, groups, roles, 6 clients, scopes) |
| `examples/setup_partner_idp.py` | Adds a second realm and wires it in as an Identity Provider |
| `examples/api/main.py` | FastAPI backend that verifies tokens (the "resource server") |
| `examples/spa/index.html` | Single-page app using the official `keycloak-js` adapter |
| `examples/native/desktop_login.py` | Mobile/desktop login done by hand (Authorization Code + PKCE) |
| `examples/m2m/reporting_job.py` | Machine-to-machine (Client Credentials) |
| `docker/keycloak/docker-compose.yml` | Keycloak + PostgreSQL |
| `docker/elk/docker-compose.yml`, `filebeat.yml`, `logstash.conf` | Keycloak + full ELK stack |

---

# Part A – The ideas

## 1. What problem does Keycloak solve?

Imagine you build three things for your company, ACME Corp: a web portal, a mobile app, and a backend API. Every one of them needs to answer two questions about each request:

**Who are you?** (authentication) and **What are you allowed to do?** (authorization).

The naive approach is to write a login form, a users table, password hashing, "forgot password" emails, session handling, 2-factor auth, account lockout… in *every* application. Then the company buys another product that needs its own login, and a partner company wants its staff to log in too, and HR wants the corporate Active Directory to be the source of truth. It becomes a mess, and every copy of that mess is a security risk.

**Keycloak is a server whose only job is identity.** You install it once. Your apps stop having login pages of their own; they *redirect* the user to Keycloak, Keycloak does the login (password, 2FA, Google, corporate LDAP, whatever you configured), and hands back a signed **token** that says "this is Alice, she is a manager, this token is valid until 10:05". Your apps just read the token.

This category of software is called **IAM** (Identity and Access Management). Because one login at Keycloak works for every app connected to it, you get **SSO** (Single Sign-On) for free: log in to the portal, open the mobile app, you are already in.

Keycloak is open source (Red Hat / CNCF), free, and speaks the industry-standard protocols (OpenID Connect, OAuth 2.0, SAML), so every language and framework already has libraries for it.

## 2. The vocabulary you cannot skip

Nine words. Everything else in this tutorial is built from them.

| Word | Plain meaning |
|---|---|
| **Authentication (AuthN)** | Proving *who* you are. Password, fingerprint, Google login. |
| **Authorization (AuthZ)** | Deciding *what* you may do. "Managers can approve orders." |
| **Identity Provider (IdP)** | The system that does the authentication and vouches for you. Keycloak is an IdP. So is Google, Azure AD, Okta. |
| **OAuth 2.0** | A protocol for handing out *access tokens* so one app can call another on your behalf. It is about *authorization*. |
| **OpenID Connect (OIDC)** | A thin layer on top of OAuth 2.0 that adds *identity* (who the user is). This is what "Login with Google" uses, and what you will use 95% of the time. |
| **SAML** | An older, XML-based protocol for the same purpose. You meet it when integrating with enterprise/legacy systems. |
| **Token** | A signed string Keycloak hands to your app after login. Your app trusts it because it can verify the signature. |
| **JWT** | *JSON Web Token* – the concrete format of those tokens: three base64 parts (`header.payload.signature`). You can paste one into https://jwt.io and read it. |
| **SSO** | Log in once, be logged in everywhere that trusts the same IdP. |

A useful mental model: **Keycloak is the passport office.** It checks your documents once, issues a passport (token) with your name and stamps (roles), and every border (app/API) trusts the passport because they recognise the office's seal (signature). Borders never call the passport office for every traveller – they just check the seal.

## 3. The building blocks, one by one

Each block below follows the same pattern: *what* it is, *why* it exists, *when* you use it, and a concrete ACME example. The hands-on part later builds exactly this ACME setup.

### 3.1 Realms

**What:** A realm is a completely isolated space inside Keycloak. It has its own users, roles, clients, login page, settings, even its own signing keys. Two realms know nothing about each other.

**Why:** Isolation. ACME's employees and ACME's customers should not live in the same user pool with the same password policy and the same apps.

**When to create a new one:**

- Different *audiences* (employees vs. customers vs. partners).
- Different *tenants* if you build SaaS and each customer wants their own users, branding and rules.
- Different *environments* if you run one Keycloak for dev/test (in production you'd rather run separate servers).

**Do not** create a realm per application. Applications are *clients* inside a realm (next sections). The whole point of SSO is many apps in one realm.

**The `master` realm** is special: it exists only to administer Keycloak itself. Your `admin` user lives there. Best practice: never put real users or apps in `master`; create a realm like `acme` and work there.

**ACME example:** realm `acme` for employees; later maybe realm `acme-customers` for the public shop.

### 3.2 Users

**What:** A person (or, for machine clients, a hidden "service account") that can log in. A user has a username, email, first/last name, *attributes* (any extra key/value such as `department=Sales`), *credentials* (password, OTP, passkey), *role mappings*, and *group memberships*.

**Why:** Somebody has to log in.

**Where users come from:** three options, and you can mix them:

1. **Created in Keycloak** (admin creates them, or users self-register). Stored in Keycloak's database.
2. **Federated** from an existing directory (LDAP / Active Directory) – Keycloak reads them from there. See 3.12.
3. **Brokered** from another identity provider (Google, GitHub, a partner's Keycloak, Azure AD) – the user logs in *there*, and Keycloak creates a linked local user the first time. See 3.11.

**User profile (Keycloak 24+):** the realm defines *which* attributes are allowed (`Realm settings → User profile`). If you want a custom attribute like `department`, you declare it once, then you can set it per user and show it on registration forms. The tutorial script does this.

**ACME example:** `alice` (Sales), `bob` (Engineering), `carol` (Management).

### 3.3 Groups

**What:** A named bucket of users. Groups can be nested (`/Engineering/Backend`). Groups can have *role mappings*: any user in the group automatically gets those roles. Groups can also carry attributes.

**Why:** Managing permissions per user does not scale. You want "everyone in Management gets `manager`", not 40 manual edits.

**When:** Whenever more than one person should share a set of permissions, or when an org structure exists. Groups map naturally onto LDAP organisational units, so federation loves them.

**Groups vs. roles (the classic confusion):** a *group* is about *who you are with* (org structure); a *role* is about *what you may do*. Groups hand out roles. Your API should check **roles**, not groups; the group is just the convenient way to assign them. (Your token *can* contain group names if you add a mapper – we do that in the tutorial for illustration.)

**ACME example:** groups `Sales`, `Engineering`, `Management`. Every group grants the realm role `employee`; `Management` additionally grants `manager`.

### 3.4 Roles

**What:** A label meaning "is allowed to do X". Roles end up inside the token, and your apps make decisions by looking for them. There are two kinds:

- **Realm roles** live at realm level and are meaningful across all apps. Example: `employee`, `manager`, `admin`.
- **Client roles** belong to one specific client and only make sense for it. Example: on the client `acme-api`, the roles `orders:read` and `orders:write`.

**Why two kinds?** Because "manager" is a fact about the person, while "may write orders in the Orders API" is a fact about one system. Keeping the second kind inside the client avoids a realm polluted with hundreds of `orders-api-write`, `hr-app-approve`, `wiki-edit` roles.

**Composite roles:** a role that contains other roles. Give `admin` the composite of `manager` + `employee` + `orders:write`, and anyone with `admin` has all of them. Useful; don't overdo it.

**Default roles:** every realm has a role `default-roles-<realm>` that every new user gets. It contains `offline_access` and `uma_authorization` by default. You can add your own (e.g. make every new user an `employee`).

**Where roles appear in the token:**

```json
"realm_access":    { "roles": ["employee", "manager"] },
"resource_access": { "acme-api": { "roles": ["orders:read", "orders:write"] } }
```

**ACME example:** realm roles `employee`, `manager`, `admin`; client roles `orders:read`, `orders:write` on `acme-api`.

### 3.5 Clients

**What:** A client is *an application that is registered with the realm*. Every app that wants to log people in, or wants to verify tokens, must be a client. The client has a **Client ID** (a string like `acme-spa`), a type, allowed redirect URLs, and settings describing how it is allowed to obtain tokens.

**Why:** Keycloak must know which apps are allowed to ask it for tokens and where it is allowed to send users back to after login (otherwise anyone could build a fake app and harvest tokens).

The two most important switches on a client:

**Client authentication ON / OFF** (in older docs: "confidential" vs "public"):

- **OFF = public client.** The app runs *in the user's hands* (browser JavaScript, mobile app, desktop app) and therefore *cannot keep a secret* – anyone can read the source. No client secret is used. Security comes from strict redirect URIs and **PKCE** (explained in 9.3).
- **ON = confidential client.** The app runs *on a server you control* (backend web app, batch job, another microservice). It gets a **client secret** (or a certificate) and must present it when talking to Keycloak.

**Authentication flows** (which "grant types" the client may use):

| Flow (Admin Console name) | OAuth name | Who uses it |
|---|---|---|
| Standard flow | Authorization Code | Anything with a human and a browser: SPA, mobile, server web app |
| Direct access grants | Resource Owner Password | Legacy/CLI tools that collect the password themselves. Avoid for new apps. |
| Service accounts roles | Client Credentials | Machine-to-machine, no human |
| OAuth 2.0 Device Authorization Grant | Device flow | Smart TVs, CLIs on machines without a browser |
| Implicit flow | Implicit | **Deprecated**. Never enable. |

Plus important fields:

- **Valid redirect URIs** – exact list of URLs Keycloak may send the browser back to after login. Wildcards allowed at the end only (`http://localhost:3000/*`). This is your main defence against token theft; keep it tight.
- **Valid post logout redirect URIs** – same idea for logout.
- **Web origins** – CORS: which browser origins may call Keycloak's endpoints directly (needed for SPAs).
- **Front channel logout / Backchannel logout URL** – how Keycloak tells your app "the user logged out elsewhere".

**A client that never logs anyone in:** your backend REST API. It only *receives* tokens and verifies them. Register it as a client anyway (so you can attach client roles to it and set it as the token's *audience*), with all flows switched off. Older Keycloak versions called this "bearer-only".

**ACME example (six clients, all built in Part B):**

| Client ID | Type | Purpose |
|---|---|---|
| `acme-spa` | public, standard flow | React/Vue web portal |
| `acme-mobile` | public, standard flow, custom-scheme redirect | iOS/Android app |
| `acme-webapp` | confidential, standard flow | Classic server-rendered Flask/Django app |
| `acme-reporting-job` | confidential, service account | Nightly batch job (M2M) |
| `acme-api` | confidential, no flows | The REST API; owns `orders:*` roles |
| `acme-cli` | public, direct access + device flow | Command-line tool |

### 3.6 Client scopes

**What:** A reusable, named bundle of *what goes into the token* (claims) and *what the client is asking permission for* (the `scope` parameter). A client scope contains **protocol mappers** – small rules such as "copy user attribute `department` into a claim called `department`" or "put the user's groups into a `groups` claim" or "add `acme-api` to the audience".

**Why:** Without them you would configure the same mappers on every client. Also, OAuth's `scope=openid profile email` concept has to map to something – each of those words is a client scope in Keycloak.

**Default vs optional:** on each client you attach scopes as *default* (always applied) or *optional* (applied only if the app asks for it via `scope=...`). Keycloak ships with `profile`, `email`, `roles`, `web-origins`, `offline_access`, `phone`, `address`, `microprofile-jwt`, `acr`, `basic`, and more.

**When to create your own:**

- You need a custom claim in the token (very common: `department`, `tenant_id`, `groups`).
- You need the **audience** claim set so your API can reject tokens meant for other APIs (very important, see 9.1).
- You want consent screens that list meaningful permissions ("This app wants to: read your orders").

**ACME example:** scope `acme-profile` adds `department` and `groups` claims; scope `acme-api-audience` adds `aud: acme-api`.

### 3.7 Sessions

**What:** When a user logs in, Keycloak creates a **user session** (the SSO session) – "Alice is logged in from this browser since 09:00". Each app she opens adds a **client session** under it. Tokens are *derived* from the session: the refresh token is tied to it, and if the session is gone, the refresh token stops working.

**Why:** Sessions are what make SSO and logout possible. Log in once → session → every client gets tokens without re-entering a password. Admin clicks "Sign out" on a user → session gone → apps lose the ability to refresh.

**Timeouts (Realm settings → Sessions and → Tokens):**

| Setting | Meaning | Typical |
|---|---|---|
| SSO Session Idle | Log out if the user does nothing for this long | 30 min |
| SSO Session Max | Absolute lifetime of the session, however active | 10 h |
| Client Session Idle/Max | Same, per client (optional override) | – |
| Access Token Lifespan | How long an access token is valid. Short! Apps refresh silently. | 5 min |
| Offline Session Idle | For `offline_access` refresh tokens (mobile "stay logged in for 30 days") | 30 days |
| Login timeout | How long the login page may sit unfinished | 30 min |

**Important beginner insight:** an *access token* is valid until it expires **even if the session is revoked** – your API verifies it offline and never asks Keycloak. That is exactly why access tokens are short (minutes). If you need instant revocation, use *token introspection* (9.1) at the cost of a network call.

**Where to look:** left menu `Sessions` (all live sessions in the realm), or `Users → alice → Sessions`. Buttons: *Sign out* one session, *Sign out all sessions*, and *Revocation → Not before* (invalidate every token issued before now).

### 3.8 Events

**What:** Keycloak records two kinds of events:

- **User events:** LOGIN, LOGIN_ERROR, LOGOUT, REGISTER, UPDATE_PASSWORD, CODE_TO_TOKEN, REFRESH_TOKEN, CLIENT_LOGIN (M2M), USER_INFO_REQUEST, … about 100 types.
- **Admin events:** somebody changed configuration – "CREATE CLIENT acme-spa by admin from 10.0.0.5", with the full JSON representation if *Include representation* is on.

**Why:** Security monitoring (failed logins, brute force), audit ("who gave Bob the admin role?"), debugging ("why does Alice's login fail?"), and business metrics (logins per app).

**Where they go – event listeners:** each realm has a list of listeners. Two ship built-in:

- `jboss-logging` – writes each event to the server log. **This is the bridge to ELK** (Part 12).
- `email` – emails the user about suspicious events (login from new device, password change).

**Storing vs. logging:** `Realm settings → Events → User events settings → Save events` stores them in the database so the Admin Console `Events` page can show them (set an *Expiration* – 7–30 days – or your DB grows forever). Logging via `jboss-logging` is independent and is what you ship to Elastic.

**ACME example:** save user & admin events for 7 days, listeners `jboss-logging` + `email`, and forward the log to ELK.

### 3.9 Realm settings

The `Realm settings` page is where per-realm policy lives. What matters at the beginning:

| Tab | What you set there |
|---|---|
| **General** | Display name, whether the realm is enabled, *frontend URL*, the well-known "OpenID Endpoint Configuration" link (bookmark it – every URL your apps need is in there). |
| **Login** | Turn on user registration, "Forgot password", "Remember me", email as username, login with email, verify email. |
| **Email** | SMTP server so Keycloak can send verification / reset / event emails. Nothing email-related works until this is set. |
| **Themes** | Pick a look for login/account/admin pages, default language, internationalisation. |
| **Keys** | The signing keys behind every token. Keycloak rotates them; your apps fetch public keys from the JWKS URL automatically. |
| **Events** | See 3.8. |
| **Localization** | Extra languages, custom message overrides. |
| **Security defenses** | Headers (CSP, X-Frame-Options) and **Brute force detection** (lock after N failures). Turn brute force on. |
| **Sessions / Tokens** | The timeouts from 3.7, token signature algorithm, refresh-token reuse rules. |
| **Client policies** | Realm-wide rules for clients ("every public client must use PKCE"). Great for governance. |
| **User profile** | The list of allowed user attributes and their validation. |
| **User registration** | Default roles and default groups for new users. |

### 3.10 Authentication (flows, policies, required actions)

**What:** `Authentication` is the page where you define *how* a login actually happens. A **flow** is an ordered list of steps (*executions*) such as "Cookie → Identity Provider redirector → Username/password form → OTP form". Each step is *Required*, *Alternative*, *Conditional* or *Disabled*.

Built-in flows you will meet:

- **browser** – the normal interactive login (cookie check, IdP button, username+password, optional OTP).
- **direct grant** – for the Resource Owner Password grant (no browser).
- **registration** – the self-registration form (profile fields, password, reCAPTCHA, terms).
- **reset credentials** – "forgot password".
- **first broker login** – what happens the first time somebody arrives via an external IdP (review profile, link to existing account by email, …).
- **clients** – how *clients* authenticate (secret, JWT, mTLS).

**Why you'd touch it:**

- Force **2FA/OTP** for everyone or only for `admin`s (duplicate `browser`, set *OTP Form* to Required, or use a *Condition – user role* sub-flow).
- Add **passkeys / WebAuthn** as a passwordless option.
- Add **reCAPTCHA** to registration.
- Change **password policy** (`Authentication → Policies → Password policy`: length, digits, not-username, history, expiry).
- Configure **OTP policy** (TOTP vs HOTP, digits, algorithm) and **WebAuthn policy**.
- Define **Required actions** – things a user must do at next login: verify email, update password, configure OTP, accept terms.

**Golden rule:** never edit the built-in flows in place. *Duplicate*, edit the copy, then *bind* it (Action → Bind flow → Browser flow). That way you can always switch back.

### 3.11 Identity providers (identity brokering)

**What:** An *external* place users can log in with, shown as a button on the Keycloak login page: "Login with Google / GitHub / Microsoft / Facebook / Apple / any OIDC or SAML server / another Keycloak". Keycloak acts as a **broker**: your apps only ever talk to Keycloak; Keycloak talks to Google.

**Why:** Users don't want another password; partners want their own staff to use their own corporate login; you don't want to integrate Google, Azure AD and Okta into five separate apps.

**How it works:** user clicks the button → Keycloak redirects to the external IdP → user logs in there → IdP sends the user back to Keycloak's *broker endpoint* (`/realms/acme/broker/<alias>/endpoint`) with an identity → Keycloak runs the *first broker login* flow → creates (or links) a local user → issues its *own* tokens to your app. Your app never sees Google's token unless you ask for it.

**Identity provider mappers** turn external data into local data: "attribute `department` from SAML → user attribute", "everyone from this IdP gets role `partner`", "SAML group `Admins` → Keycloak role `admin`".

**When:** social login for customers; B2B partner access; enterprise SSO where the company already has Azure AD / Okta / ADFS; migrating from another IdP gradually.

**ACME example (built in Part 11):** realm `partner-corp` (pretend it's a different company's system) registered in `acme` as IdP "Partner Corp"; every brokered user gets `employee`.

### 3.12 User federation

**What:** A connection to an existing user *store* – primarily **LDAP** and **Active Directory** (and Kerberos). Users stay in LDAP; Keycloak reads them (and optionally writes back). When Alice logs in, Keycloak checks the password *against LDAP*, then issues normal tokens.

**Why:** Corporations already have AD with 10,000 users, groups and password policies. You do not migrate that; you point Keycloak at it.

**Federation vs. brokering (the second classic confusion):**

| | User federation (LDAP) | Identity brokering (IdP) |
|---|---|---|
| Who checks the password? | Keycloak, by binding to LDAP | The external IdP on its own login page |
| What does the user see? | Keycloak's login page | A "Login with …" button, then the external page |
| Where is the user record? | LDAP (Keycloak imports/caches a copy) | External IdP (Keycloak creates a linked local user) |
| Typical use | Corporate AD | Google, Azure AD via OIDC/SAML, partner Keycloaks |

Key settings: *Edit mode* (READ_ONLY / WRITABLE / UNSYNCED), *Users DN*, *Bind DN/credential*, *Import users* (copy into Keycloak DB for speed), *Periodic sync*, and **LDAP mappers** (username ↔ `sAMAccountName`, email ↔ `mail`, LDAP groups ↔ Keycloak groups, LDAP roles ↔ roles).

## 4. How the blocks fit together

```
┌──────────────────────────────── Keycloak server ────────────────────────────────┐
│                                                                                 │
│  Realm: master   (only for administering Keycloak itself)                       │
│                                                                                 │
│  Realm: acme                                                                    │
│  ┌──────────────────────────┐   ┌───────────────────────────────────────────┐   │
│  │ Where users come from    │   │ Users                                     │   │
│  │  • created locally       │──▶│  alice  bob  carol  service-account-…     │   │
│  │  • User federation (LDAP)│   │  attributes: department=Sales …           │   │
│  │  • Identity providers    │   └────────────┬──────────────────────────────┘   │
│  │    (Google, partner IdP) │                │ member of                        │
│  └──────────────────────────┘   ┌────────────▼──────────────┐                   │
│                                 │ Groups: Sales, Eng, Mgmt  │                   │
│                                 └────────────┬──────────────┘                   │
│                                              │ grant                            │
│                       ┌──────────────────────▼─────────────────────┐            │
│                       │ Roles                                      │            │
│                       │  realm:  employee  manager  admin          │            │
│                       │  client: acme-api ▸ orders:read/write      │            │
│                       └──────────────────────┬─────────────────────┘            │
│                                              │ appear in tokens via             │
│                       ┌──────────────────────▼─────────────────────┐            │
│                       │ Client scopes (+ protocol mappers)         │            │
│                       │  profile  email  roles  acme-profile  aud  │            │
│                       └──────────────────────┬─────────────────────┘            │
│                                              │ attached to                      │
│   ┌──────────────────────────────────────────▼───────────────────────────────┐  │
│   │ Clients                                                                  │  │
│   │  acme-spa  acme-mobile  acme-webapp  acme-reporting-job  acme-api  cli   │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│   Authentication flows ─ how login happens (password, OTP, passkey, IdP button) │
│   Sessions ─ who is logged in right now         Events ─ what happened (→ ELK)  │
│   Realm settings ─ policies, timeouts, email, themes, keys                      │
└─────────────────────────────────────────────────────────────────────────────────┘
        ▲ redirect to login                       │ token (JWT)
        │                                         ▼
   Your apps (clients) ──────── Bearer token ─────▶ Your API verifies signature + roles
```

Read it bottom-up for a login: a **client** sends the user to Keycloak; **authentication flow** decides how they prove identity (local password, LDAP, or an **identity provider**); Keycloak finds the **user**, collects roles from the user, their **groups** and composite **roles**; the client's **client scopes** decide which of that ends up in the **token**; a **session** is created; **events** are recorded; the token goes back to the app.

## 5. Tokens: what your app actually receives

After a successful login the client receives three tokens:

| Token | Who reads it | Purpose | Lifetime |
|---|---|---|---|
| **Access token** | Your **API** | "This caller may do X". Sent as `Authorization: Bearer …` on every API call. | Minutes |
| **ID token** | Your **front-end** | "The logged-in user is Alice, email …". Never send it to APIs. | Minutes |
| **Refresh token** | The **client** only | Get new access/ID tokens silently without a login page. Tied to the session. | Session length |

A real (shortened) access token from the tutorial, decoded – this is what your Python API sees:

```json
{
  "exp": 1788428724,                       // expires (unix time)
  "iat": 1788428424,                       // issued at
  "iss": "http://localhost:8080/realms/acme",   // who issued it  → check this
  "aud": ["acme-api", "account"],          // who it is FOR      → check this
  "sub": "4fb6aa21-9151-4103-8f56-0671f20d162b",  // stable user id
  "typ": "Bearer",
  "azp": "acme-spa",                       // which client asked for it
  "sid": "zZeoH7XphjI78MNl9Ud9X4CV",       // session id
  "realm_access":    { "roles": ["employee", "default-roles-acme", "offline_access", "uma_authorization"] },
  "resource_access": { "acme-api": { "roles": ["orders:read"] } },
  "scope": "openid acme-profile email profile",
  "preferred_username": "alice",
  "email": "alice@acme.test",
  "name": "Alice Anderson",
  "department": "Sales",                   // ← our custom mapper
  "groups": ["Sales"]                      // ← our custom mapper
}
```

How your API verifies it, in words: fetch Keycloak's public keys once from `…/realms/acme/protocol/openid-connect/certs` (the JWKS), check the signature, check `exp`, check `iss` equals your realm URL, check `aud` contains *your* API's client id, then read roles. No network call per request. Code in 9.1.

**The discovery document** – bookmark this, it lists every URL your apps need:
`http://localhost:8080/realms/acme/.well-known/openid-configuration`

---

# Part B – Hands on

## 6. Install Docker and run Keycloak

### 6.1 Install Docker Desktop (Windows)

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/ and install it. Accept the default *WSL 2* backend. Reboot if asked.
2. Start Docker Desktop and wait until the whale icon in the tray stops animating.
3. Open **PowerShell** (Windows Terminal is fine) and check:

```powershell
docker --version
docker compose version
```

### 6.2 The one-liner (quick experiments)

```powershell
docker run --name keycloak -p 8080:8080 `
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin `
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin `
  quay.io/keycloak/keycloak:26.7.3 start-dev
```

(The backtick `` ` `` is PowerShell's line-continuation character. Type it at the end of a line, no space after it.)

What the pieces mean:

- `-p 8080:8080` – expose Keycloak's port on your machine.
- `KC_BOOTSTRAP_ADMIN_USERNAME/PASSWORD` – creates the very first admin the *first* time the (empty) database starts. Later runs ignore it.
- `quay.io/keycloak/keycloak:26.7.3` – the official image. Check the newest tag at https://quay.io/repository/keycloak/keycloak?tab=tags (or https://www.keycloak.org/downloads).
- `start-dev` – development mode: plain HTTP, no hostname/TLS configuration required, in-memory-ish H2 database file. **Never use `start-dev` in production.**

Wait for the line `Keycloak 26.7.3 on JVM … started in …s. Listening on: http://0.0.0.0:8080`, then open http://localhost:8080 and log in with `admin` / `admin`.

Useful follow-ups:

```powershell
docker logs -f keycloak        # follow the log (Ctrl+C to stop following)
docker stop keycloak           # stop
docker start keycloak          # start again, data kept
docker rm -f keycloak          # delete container AND its data
```

### 6.3 The proper way: Docker Compose with PostgreSQL

The one-liner stores data inside the container. For anything you want to keep, use a real database. Create a folder, e.g. `C:\keycloak-lab\docker\keycloak`, and put the file `docker/keycloak/docker-compose.yml` from the companion files in it. Its important lines:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: keycloak-db-password
    volumes: [pgdata:/var/lib/postgresql/data]

  keycloak:
    image: quay.io/keycloak/keycloak:26.7.3
    command: start-dev
    environment:
      KC_BOOTSTRAP_ADMIN_USERNAME: admin
      KC_BOOTSTRAP_ADMIN_PASSWORD: admin
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: keycloak-db-password
      KC_HEALTH_ENABLED: "true"
      KC_METRICS_ENABLED: "true"
    ports: ["8080:8080", "9000:9000"]
```

Run it:

```powershell
cd C:\keycloak-lab\docker\keycloak
docker compose up -d           # start in the background
docker compose logs -f keycloak
```

Health check (management port 9000): http://localhost:9000/health/ready → `{"status":"UP"}`.

**Every Keycloak option can be set three ways**, and they mean the same thing: a CLI flag `--db=postgres`, an environment variable `KC_DB=postgres`, or a line `db=postgres` in `conf/keycloak.conf`. The rule: uppercase, `KC_` prefix, dashes become underscores. The full list is at https://www.keycloak.org/server/all-config.

### 6.4 The admin CLI (`kcadm`) from PowerShell

The image contains a CLI. Run it *inside* the container with `docker exec`:

```powershell
# log in once (the session is stored inside the container)
docker exec keycloak /opt/keycloak/bin/kcadm.sh config credentials `
  --server http://localhost:8080 --realm master --user admin --password admin

# list realms
docker exec keycloak /opt/keycloak/bin/kcadm.sh get realms --fields realm,enabled

# list users in a realm
docker exec keycloak /opt/keycloak/bin/kcadm.sh get users -r acme --fields username,email

# create a user
docker exec keycloak /opt/keycloak/bin/kcadm.sh create users -r acme -s username=dan -s enabled=true
docker exec keycloak /opt/keycloak/bin/kcadm.sh set-password -r acme --username dan --new-password dan123

# last 5 events
docker exec keycloak /opt/keycloak/bin/kcadm.sh get events -r acme --limit 5
```

(With Compose the container is named `keycloak` too because of `container_name`; otherwise use `docker compose exec keycloak …`.)

### 6.5 Backup / restore a realm (export & import)

```powershell
# export realm 'acme' (with users) to a folder inside the container, then copy it out
# (works while the server runs when you use PostgreSQL; with the dev-file H2 database stop the server first)
docker exec keycloak /opt/keycloak/bin/kc.sh export --dir /tmp/export --realm acme --users realm_file
docker cp keycloak:/tmp/export/acme-realm.json .\acme-realm.json

# import on a fresh server: put the file in /opt/keycloak/data/import and start with --import-realm
docker run --name keycloak -p 8080:8080 `
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin `
  -v ${PWD}\acme-realm.json:/opt/keycloak/data/import/acme-realm.json `
  quay.io/keycloak/keycloak:26.7.3 start-dev --import-realm
```

## 7. Your first realm, user and login

Do this once by clicking so the Admin Console stops being scary. Everything after uses a script.

1. Open http://localhost:8080 → log in `admin` / `admin`.
2. Top-left realm dropdown says **master**. Click it → **Create realm** → Realm name `playground` → **Create**. You are now inside `playground`.
3. **Users** → **Create new user** → Username `test`, Email `test@example.com`, First/Last name anything, tick *Email verified* → **Create**.
4. On the new user, tab **Credentials** → **Set password** → type a password twice, switch *Temporary* **off** → **Save**.
5. Open a private/incognito window: http://localhost:8080/realms/playground/account → **Sign in** → `test` + password. You are looking at the **Account Console**: the self-service page every user of your realm gets (profile, password, 2FA, sessions, linked accounts). Congratulations, that is your first Keycloak login.
6. Back in the admin window: **Sessions** in the left menu now shows `test`'s session. Click the ⋮ → **Sign out** and refresh the private window: the user is logged out.
7. **Realm settings → Events → User events settings**: switch *Save events* on → **Save**. Log in again in the private window, then look at **Events** in the left menu: you see `LOGIN`. Click it to see details (client `account-console`, IP, …).
8. **Clients** → look at the pre-made clients: `account`, `account-console`, `admin-cli`, `broker`, `realm-management`, `security-admin-console`. Keycloak's own UI is itself a client – the same machinery you will use.

That's a realm, a user, a session, an event, and clients. Delete `playground` later if you like (Realm settings → Action ▾ → Delete).

## 8. Build the "ACME Corp" realm with a script

Clicking is fine for learning, but you will rebuild realms many times. The companion script `examples/setup_realm.py` uses Keycloak's **Admin REST API** to create the whole ACME realm described in Part A. Read the script – every block is commented and maps 1:1 to a section in Part A.

### 8.1 Set up Python

```powershell
python --version                  # need 3.10+; install from https://www.python.org if missing
cd C:\keycloak-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install requests "pyjwt[crypto]" fastapi uvicorn
```

### 8.2 Run it

```powershell
python examples\setup_realm.py
```

Expected output:

```
Realm 'acme' ready
Realm roles: employee, manager, admin
Groups: Sales, Engineering, Management (with roles attached)
Users: alice (Sales), bob (Engineering), carol (Management)
Client scope: acme-profile
Clients: acme-spa, acme-mobile, acme-webapp, acme-reporting-job, acme-api, acme-cli
API client roles: orders:read, orders:write (mapped to groups + service account)

Done!  Admin console: http://localhost:8080/admin/master/console/#/acme
```

The script is *idempotent* – run it again any time; existing objects are skipped.

### 8.3 What it did, and where to see it

| Script section | Admin Console location | Part A |
|---|---|---|
| Realm with login/brute-force/events/timeouts settings | Realm settings → General / Login / Security defenses / Events / Sessions / Tokens | 3.1, 3.9 |
| Realm roles `employee`, `manager`, `admin` | Realm roles | 3.4 |
| Groups with role mappings | Groups → Management → Role mapping | 3.3 |
| Users with passwords, group membership, `department` attribute | Users → alice → Attributes / Groups | 3.2 |
| User profile attribute `department` | Realm settings → User profile | 3.2 |
| Client scope `acme-profile` with two mappers | Client scopes → acme-profile → Mappers | 3.6 |
| Client scope `acme-api-audience` | Client scopes → acme-api-audience | 3.6 |
| Six clients | Clients | 3.5 |
| Client roles `orders:read/write` on `acme-api` | Clients → acme-api → Roles | 3.4 |
| Service account of the M2M client gets `orders:read` | Clients → acme-reporting-job → Service account roles | 3.5, 9.5 |

**How the script authenticates:** it asks the `master` realm for a token using the built-in `admin-cli` client and the admin's password (Direct Access Grant), then calls `http://localhost:8080/admin/realms/...` with `Authorization: Bearer <token>`. This is exactly what the Admin Console and `kcadm` do. For automation in real life, create a confidential client in `master` with a service account and give it the `admin` role (or the fine-grained `realm-management` roles inside the target realm) instead of using a human's password.

### 8.4 Look at a token by hand

```powershell
# ask for a token as carol via the CLI client (password grant is enabled on acme-cli only)
$r = Invoke-RestMethod -Method Post -Uri http://localhost:8080/realms/acme/protocol/openid-connect/token `
       -Body @{ grant_type='password'; client_id='acme-cli'; username='carol'; password='carol123'; scope='openid' }
$r.access_token
```

Paste the access token into https://jwt.io. You will see `realm_access.roles` containing `manager` and `employee` (from her group), `resource_access.acme-api.roles` containing `orders:read` and `orders:write`, `department: "Management"`, `groups: ["Management"]` and `aud: ["acme-api", "account"]`.

Two more endpoints worth calling:

```powershell
# who am I?  (userinfo)
Invoke-RestMethod -Uri http://localhost:8080/realms/acme/protocol/openid-connect/userinfo `
  -Headers @{ Authorization = "Bearer $($r.access_token)" }

# get a fresh access token using the refresh token
Invoke-RestMethod -Method Post -Uri http://localhost:8080/realms/acme/protocol/openid-connect/token `
  -Body @{ grant_type='refresh_token'; client_id='acme-cli'; refresh_token=$r.refresh_token }
```

## 9. Client types, one by one

Every example below was run against the realm the script builds. Start the API first (9.1); the others call it.

### 9.1 The backend REST API (resource server)

**Which blocks:** client `acme-api` (no login flows, owns client roles `orders:read/write`), client scope `acme-api-audience` (puts `acme-api` in `aud`), roles in the token.

**What it does:** reads the `Authorization: Bearer` header, verifies the JWT *offline* using Keycloak's public keys, checks issuer and audience, then checks roles per endpoint. File: `examples/api/main.py`. The core:

```python
from fastapi import FastAPI, Depends, HTTPException, Request
import jwt
from jwt import PyJWKClient

ISSUER   = "http://localhost:8080/realms/acme"
AUDIENCE = "acme-api"
jwks_client = PyJWKClient(f"{ISSUER}/protocol/openid-connect/certs", cache_keys=True)

def current_user(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing Bearer token")
    token = auth[7:]
    try:
        key = jwks_client.get_signing_key_from_jwt(token)      # picks the key by 'kid' in the header
        return jwt.decode(token, key.key, algorithms=["RS256"],
                          audience=AUDIENCE, issuer=ISSUER)   # signature + exp + aud + iss
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.PyJWTError as e:
        raise HTTPException(401, f"Invalid token: {e}")

def require_client_role(role: str):
    def checker(claims: dict = Depends(current_user)):
        if role not in claims.get("resource_access", {}).get(AUDIENCE, {}).get("roles", []):
            raise HTTPException(403, f"Requires role '{role}'")
        return claims
    return checker

@app.get("/orders")
def list_orders(claims=Depends(require_client_role("orders:read"))): ...

@app.post("/orders")
def create_order(order: dict, claims=Depends(require_client_role("orders:write"))): ...
```

Run and test:

```powershell
cd C:\keycloak-lab\examples\api
uvicorn main:app --port 8000
```

In a second PowerShell:

```powershell
$t = (Invoke-RestMethod -Method Post -Uri http://localhost:8080/realms/acme/protocol/openid-connect/token `
       -Body @{ grant_type='password'; client_id='acme-cli'; username='alice'; password='alice123' }).access_token

Invoke-RestMethod http://localhost:8000/me     -Headers @{ Authorization="Bearer $t" }   # 200, alice, Sales
Invoke-RestMethod http://localhost:8000/orders -Headers @{ Authorization="Bearer $t" }   # 200, alice has orders:read
# alice is not a manager -> orders:write missing -> 403:
Invoke-RestMethod -Method Post http://localhost:8000/orders -Headers @{ Authorization="Bearer $t" } `
  -ContentType application/json -Body '{"item":"Anvil","qty":1}'
```

Repeat with `carol` – she is in `Management`, so the POST succeeds. No token → 401.

**Why the audience check matters:** without it, a token issued for a completely different API (or for the `account` console) would be accepted by yours. That is why the script created the `acme-api-audience` scope and attached it to every client that should be allowed to call this API.

**Alternative: token introspection (online check).** If you need revocation to take effect instantly, ask Keycloak whether the token is still alive. The API client needs *Client authentication ON* and a secret for this (the script sets `api-secret-change-me`):

```python
r = requests.post(f"{ISSUER}/protocol/openid-connect/token/introspect",
                  data={"token": token}, auth=("acme-api", "api-secret-change-me")).json()
if not r["active"]: raise HTTPException(401)
```

One network call per request; use it for sensitive endpoints or with a short cache.

**CORS note:** the API enables CORS for `http://localhost:3000` because the SPA (9.2) calls it from the browser. Keycloak's own CORS setting (client → *Web origins*) is a separate thing and only concerns calls *to Keycloak*.

### 9.2 Single-Page App (React / Vue / Angular / plain JS)

**Which blocks:** client `acme-spa` – *public*, Standard flow, PKCE S256, `Valid redirect URIs = http://localhost:3000/*`, `Web origins = http://localhost:3000`, default scopes `acme-profile` + `acme-api-audience`.

**Why public:** the browser can read every byte of your JavaScript, so a secret would be pointless. Security comes from (a) Keycloak only redirecting to your whitelisted URL and (b) PKCE, which stops a stolen authorization code from being exchanged by someone else.

**The flow, in words:** app loads → `keycloak-js` checks for an existing SSO session → user clicks *Login* → browser goes to Keycloak's login page → user logs in → Keycloak redirects back to `http://localhost:3000/?code=…` → the adapter exchanges the code for tokens (with PKCE) → tokens live in memory → the app calls the API with `Authorization: Bearer` → the adapter refreshes silently before expiry.

File: `examples/spa/index.html` (no build tools needed). The essence:

```html
<script type="module">
  import Keycloak from "https://cdn.jsdelivr.net/npm/keycloak-js@26.2.4/lib/keycloak.js";
  // in a React/Vue project: npm install keycloak-js ; import Keycloak from "keycloak-js";

  const kc = new Keycloak({ url: "http://localhost:8080", realm: "acme", clientId: "acme-spa" });

  const authenticated = await kc.init({ onLoad: "check-sso", pkceMethod: "S256" });
  // onLoad: "login-required" would force a login immediately instead

  document.getElementById("login").onclick  = () => kc.login();
  document.getElementById("logout").onclick = () => kc.logout({ redirectUri: location.origin });

  document.getElementById("call").onclick = async () => {
    await kc.updateToken(30);                              // refresh if it expires within 30 s
    const r = await fetch("http://localhost:8000/orders",
                          { headers: { Authorization: "Bearer " + kc.token } });
    console.log(r.status, await r.text());
  };
  // kc.tokenParsed  -> decoded access token (roles, department, ...)
  // kc.idTokenParsed -> decoded ID token (name, email)
</script>
```

Run it:

```powershell
cd C:\keycloak-lab\examples\spa
python -m http.server 3000
```

Open http://localhost:3000 → *Login* → `alice` / `alice123` → you see "Logged in as alice (department: Sales)" and the decoded token. Click *Call /orders API* → `200 [...]`. Click *My account* → the Account Console, without logging in again (that's SSO). Open the admin console's **Sessions** page: Alice's session lists client `acme-spa` (and `account-console` if you opened it).

**Don't** store tokens in `localStorage` (XSS can steal them); keep them in memory as the adapter does. **Don't** enable *Implicit flow*. **Do** keep redirect URIs exact in production (`https://portal.acme.com/*`, not `*`).

### 9.3 Mobile app / desktop app (native)

**Which blocks:** client `acme-mobile` – *public*, Standard flow, PKCE, redirect URI `com.acme.mobile://callback` (custom scheme) plus `http://localhost:8765/*` for the desktop demo.

Native apps are public clients like SPAs, but the "browser" is the system browser or an in-app browser tab, and the redirect back is a custom URL scheme (`com.acme.mobile://…`) or a Universal/App Link that the OS routes to your app. **Never embed a WebView with your own login form** – use the system browser (Apple and Google both require this for their own logins, and it is what makes SSO and passkeys work).

Real apps use a library: **AppAuth** (iOS/Android), `flutter_appauth`, `react-native-app-auth`, `expo-auth-session`, MSAL, etc. They all do the same five steps. `examples/native/desktop_login.py` performs those steps by hand so you can see them:

```python
# 1. PKCE: random secret (verifier) and its SHA-256 hash (challenge)
code_verifier  = secrets.token_urlsafe(64)
code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b"=").decode()

# 2. open the system browser at Keycloak's /auth endpoint with the challenge
auth_url = f"{ISSUER}/protocol/openid-connect/auth?" + urlencode({
    "client_id": "acme-mobile", "response_type": "code", "scope": "openid profile email",
    "redirect_uri": "http://localhost:8765/callback", "state": state,
    "code_challenge": code_challenge, "code_challenge_method": "S256"})
webbrowser.open(auth_url)

# 3. a tiny local HTTP server catches the redirect and reads ?code=...&state=...
#    (a phone app registers the custom scheme instead)

# 4. exchange code + verifier for tokens - no client secret, PKCE proves we started the flow
tokens = requests.post(f"{ISSUER}/protocol/openid-connect/token", data={
    "grant_type": "authorization_code", "client_id": "acme-mobile",
    "code": code, "redirect_uri": REDIRECT_URI, "code_verifier": code_verifier}).json()

# 5. use tokens["access_token"] against the API; store tokens["refresh_token"] in the OS keychain
```

```powershell
python examples\native\desktop_login.py
```

A browser opens on Keycloak's login page; log in as `alice`; the script prints the three tokens and calls `userinfo`.

**Mobile specifics:** request the `offline_access` scope so the refresh token survives for the *Offline Session Idle* period (30 days by default) and the user stays logged in; store refresh tokens in Keychain/Keystore; enable *Front channel logout* or just discard tokens and call the `/logout` endpoint with the refresh token.

### 9.4 Server-side web app (Flask / Django / ASP.NET / Spring)

**Which blocks:** client `acme-webapp` – *confidential* (Client authentication ON, secret `webapp-secret-change-me`), Standard flow, redirect `http://localhost:5000/*`.

Same Authorization Code flow, but the code→token exchange happens on the server, which presents the client secret. Tokens stay on the server in the user's session cookie; the browser never sees them. In Python the libraries are **Authlib** (Flask/Django/FastAPI) or `mozilla-django-oidc`. Sketch with Authlib + Flask:

```python
from flask import Flask, session, redirect, url_for
from authlib.integrations.flask_client import OAuth

app = Flask(__name__); app.secret_key = "change-me"
oauth = OAuth(app)
oauth.register(
    name="keycloak",
    client_id="acme-webapp",
    client_secret="webapp-secret-change-me",
    server_metadata_url="http://localhost:8080/realms/acme/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
)

@app.route("/login")
def login():
    return oauth.keycloak.authorize_redirect(url_for("callback", _external=True))

@app.route("/callback")
def callback():
    token = oauth.keycloak.authorize_access_token()   # exchanges code (+secret) for tokens
    session["user"] = token["userinfo"]                 # from the ID token
    session["access_token"] = token["access_token"]     # use it to call acme-api
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("http://localhost:8080/realms/acme/protocol/openid-connect/logout"
                    "?post_logout_redirect_uri=http://localhost:5000/&client_id=acme-webapp")
```

(`pip install authlib flask`; run with `flask --app webapp run --port 5000`.)

### 9.5 Machine-to-machine (service, cron job, microservice)

**Which blocks:** client `acme-reporting-job` – *confidential*, **Service accounts roles ON** (= Client Credentials grant), Standard flow OFF. Keycloak creates a hidden user `service-account-acme-reporting-job`; the script gives it the client role `orders:read` on `acme-api` (Admin Console: Clients → acme-reporting-job → *Service account roles* tab).

No human, no browser, no password. The job sends its id + secret, gets an access token, calls the API. File: `examples/m2m/reporting_job.py`:

```python
token = requests.post(f"{KEYCLOAK}/realms/acme/protocol/openid-connect/token", data={
    "grant_type": "client_credentials",
    "client_id": "acme-reporting-job",
    "client_secret": "reporting-secret-change-me",      # from env var / vault in real life
}).json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}
requests.get("http://localhost:8000/orders", headers=headers)                     # 200
requests.post("http://localhost:8000/orders", json={...}, headers=headers)        # 403 - only orders:read
```

```powershell
python examples\m2m\reporting_job.py
```

In the token you will see `preferred_username: service-account-acme-reporting-job`, `azp: acme-reporting-job`, and `resource_access.acme-api.roles: ["orders:read"]`. The API code from 9.1 works unchanged – it does not care whether the caller is a human or a machine; it checks roles.

**Better than a shared secret** for high-security setups: *Client authenticator = Signed JWT* (the job signs a JWT with its private key; Keycloak holds the public key) or mutual TLS. Same grant type, different proof.

### 9.6 CLI tools and the device flow

**Which blocks:** client `acme-cli` – public, *Direct access grants* ON, *OAuth 2.0 Device Authorization Grant* ON.

Two options for command-line tools:

**(a) Direct access grant (Resource Owner Password).** The CLI asks for username/password itself and posts them to the token endpoint – what we used in 8.4 for quick testing. Simple, but the app sees the password, MFA/passkeys/IdP buttons don't work, and it is deprecated in OAuth 2.1. Use only for legacy/test tooling.

**(b) Device Authorization Grant** – how `gh auth login`, `az login`, Netflix on a TV work. The CLI asks Keycloak for a code, shows the user a URL, polls until the user finishes in any browser:

```python
d = requests.post(f"{ISSUER}/protocol/openid-connect/auth/device",
                  data={"client_id": "acme-cli", "scope": "openid"}).json()
print("Open", d["verification_uri_complete"], "and approve")   # e.g. http://localhost:8080/realms/acme/device?user_code=GRRN-AQRL
while True:
    time.sleep(d["interval"])
    r = requests.post(f"{ISSUER}/protocol/openid-connect/token", data={
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "client_id": "acme-cli", "device_code": d["device_code"]})
    if r.status_code == 200:
        tokens = r.json(); break
    # 400 with error "authorization_pending" means keep waiting
```

### 9.7 "API keys" – how Keycloak thinks about them

Keycloak does not issue classic long-lived opaque API keys, and that is deliberate: a key that never expires and carries no signature is exactly what tokens fix. The equivalents, from best to worst:

| You want… | Do this |
|---|---|
| A partner/system to call your API without a human | Give them a **confidential client with a service account** (9.5). Their "API key" is `client_id` + `client_secret`; they trade it for short-lived tokens. You can rotate the secret, scope it with client roles, and see every call as a `CLIENT_LOGIN` event. |
| A key that a *user* owns for scripts | Issue an **offline token**: the user logs in once with `scope=offline_access`; the refresh token then lives for *Offline Session Idle* (30 d, renewed on use). The script stores it and exchanges it for access tokens. Users can see and revoke them in the Account Console → *Applications*. |
| Really, a static string in a header | Put an **API gateway** (Kong, APISIX, NGINX, Traefik) in front. The gateway maps the key to a client and does the token exchange with Keycloak, so your API still only sees JWTs. |

### 9.8 Cheat sheet

| App type | Client auth | Flow | PKCE | Secret? | Token storage | Python library |
|---|---|---|---|---|---|---|
| SPA | OFF (public) | Standard (Auth Code) | yes | no | memory | (JS) keycloak-js, oidc-client-ts |
| Mobile / desktop | OFF (public) | Standard (Auth Code) | yes | no | OS keychain | AppAuth family |
| Server web app | ON (confidential) | Standard (Auth Code) | optional | yes | server session | Authlib |
| Backend API | ON, no flows | – (verifies only) | – | only for introspection | – | PyJWT / Authlib |
| Service / job | ON (confidential) | Client Credentials | – | yes (or signed JWT / mTLS) | memory | requests |
| CLI | OFF (public) | Device flow (or password, legacy) | – | no | OS keychain | requests |

## 10. Real-world use cases

Each scenario names the building blocks you would touch, in the order you would touch them.

**Use case 1 – Company intranet: portal + API + SSO for employees.**
Realm `acme` → *User federation* to the corporate Active Directory (users and groups arrive automatically) → LDAP group mappers turn AD groups into Keycloak *groups* → groups grant *realm roles* → clients `acme-spa` and `acme-api` → client scope with audience mapper → *Authentication*: duplicate the browser flow, make OTP required for the `admin` role → *Realm settings*: brute-force on, 30-min idle session, corporate theme → *Events* to ELK for the security team. This is exactly the ACME realm plus LDAP.

**Use case 2 – Public SaaS with social login and self-registration.**
Separate realm `acme-customers` (different audience, different rules) → *Realm settings → Login*: registration on, verify email on, SMTP configured → *Identity providers*: Google, Apple, GitHub → *first broker login* flow tweaked to skip the profile review → *Authentication → Registration* flow with reCAPTCHA and Terms & Conditions required action → client `shop-spa` public + `shop-api` → *Client scopes* adding `tenant_id` from a user attribute → *Sessions*: long offline sessions for the mobile app.

**Use case 3 – B2B: partner companies' staff use your app with their own corporate login.**
*Identity providers*: one SAML or OIDC IdP per partner (Azure AD, Okta, another Keycloak – Part 11 builds one) → *IdP mappers*: hard-code role `partner`, map their `department` claim → *Authentication → browser flow*: an *Identity Provider Redirector* execution can auto-send users from `@partner.com` emails straight to their IdP (or use the Organizations feature, which does this per email domain out of the box) → your API checks role `partner`. No passwords stored on your side.

**Use case 4 – Microservices calling each other.**
Each service gets a *confidential client with a service account* → client roles on the callee (`inventory-api` has `stock:read`) assigned to the caller's service account → callers use *Client Credentials* → callees verify JWT + audience + roles. For "service A acts on behalf of user U", look at *token exchange* (Standard token exchange is stable in Keycloak 26).

**Use case 5 – Legacy app that can't do OIDC.**
Put a reverse proxy that speaks OIDC in front of it: *oauth2-proxy*, NGINX with `lua-resty-openidc`, Traefik/Envoy plugins, or Keycloak's own *Gatekeeper*-style tools. The proxy is a *confidential client*, does the login, and forwards user headers to the legacy app. Blocks touched: one client, one scope with the headers you need, nothing else.

**Use case 6 – Security team: "Alert me on failed logins and admin changes".**
*Realm settings → Events*: save user + admin events, listener `jboss-logging` → Keycloak logs JSON → Filebeat → Elasticsearch → Kibana alert rule on `keycloak.event.type: LOGIN_ERROR` count > 20 per 5 min per `ipAddress`, and a dashboard of admin events by `operationType` (Part 12).

**Use case 7 – Multi-tenant SaaS where every customer wants their own users, branding and IdP.**
One *realm per tenant* (simple, hard isolation, but hundreds of realms get heavy) **or** one realm with **Organizations** (Keycloak 26 feature: each organization has its own members, email domains and identity providers inside one realm). Most new projects should start with Organizations.

## 11. Identity providers & user federation in practice

### 11.1 Brokering demo: a partner company's Keycloak (works entirely on your laptop)

`examples/setup_partner_idp.py` creates a *second* realm `partner-corp` with user `dave`, registers a client `acme-broker` inside it (because from partner-corp's point of view, ACME is just an application asking to log people in), and then adds `partner-corp` to `acme` as a generic **OpenID Connect** identity provider with a mapper that grants every brokered user the `employee` role.

```powershell
python examples\setup_partner_idp.py
```

Now open http://localhost:3000 (the SPA) in a fresh private window and click *Login*: the ACME login page shows a new button **Partner Corp**. Click it → you land on Partner Corp's login page → `dave` / `dave123` → you are back in the ACME SPA as `dave`. Look at **Users** in the `acme` admin console: `dave` now exists locally, and under *Identity provider links* you see he is linked to `partner-corp`. Under *Role mapping* he has `employee` from the IdP mapper.

Doing the same by clicking (for Google, GitHub, Microsoft etc.): **Identity providers → Add provider → Google** → paste the *Client ID* and *Client secret* you created in Google Cloud Console, and register Keycloak's *Redirect URI* (shown on that page, `…/realms/acme/broker/google/endpoint`) in Google. Same shape for every provider.

The settings you will actually tune: *Trust email* (skip verification if the IdP says it's verified), *Sync mode* (IMPORT = copy once, FORCE = update user on every login), *First login flow*, *Hide on login page* (when you redirect programmatically with `kc_idp_hint=partner-corp`), and mappers.

### 11.2 Federation demo: LDAP with Docker

Add an OpenLDAP container next to Keycloak (append to your Compose file):

```yaml
  ldap:
    image: bitnamilegacy/openldap:2.6      # free community image (Bitnami's current images are subscription-only)
    environment:
      LDAP_ROOT: dc=acme,dc=test
      LDAP_ADMIN_USERNAME: admin
      LDAP_ADMIN_PASSWORD: ldap-admin-password
      LDAP_USERS: erin,frank               # creates cn=erin,ou=users,dc=acme,dc=test  etc.
      LDAP_PASSWORDS: erin123,frank123
      LDAP_GROUP: engineers                # creates cn=engineers,ou=groups,dc=acme,dc=test with both members
    ports: ["1389:1389"]
```

`docker compose up -d ldap`, then in the `acme` realm: **User federation → Add LDAP providers**:

| Field | Value |
|---|---|
| Vendor | Other |
| Connection URL | `ldap://ldap:1389` (container name – Keycloak and LDAP are on the same Compose network) |
| Bind type | simple |
| Bind DN | `cn=admin,dc=acme,dc=test` |
| Bind credentials | `ldap-admin-password` |
| Edit mode | READ_ONLY |
| Users DN | `ou=users,dc=acme,dc=test` |
| Username LDAP attribute | `uid` (`sAMAccountName` for Active Directory) |
| RDN LDAP attribute | `cn` (this image names entries `cn=erin,…`; `cn` for AD too) |
| UUID LDAP attribute | `entryUUID` (`objectGUID` for AD) |
| User object classes | `inetOrgPerson` (`person, organizationalPerson, user` for AD) |
| Import users | On |

Click *Test connection* and *Test authentication*, then **Save**, then *Action ▾ → Sync all users*. `erin` and `frank` appear under **Users** with a "federated" marker, and `erin` can log in to the SPA with `erin123` even though Keycloak never stored her password. In the provider's **Mappers** tab, add a *group-ldap-mapper* with `LDAP Groups DN = ou=groups,dc=acme,dc=test`, `Group Object Classes = groupOfNames`, `Membership LDAP Attribute = member`, then *Sync LDAP groups to Keycloak*: the `engineers` group appears under **Groups** and you map roles to it as usual. For Active Directory choose *Vendor: Active Directory* and the fields pre-fill.

## 12. Integrating with ELK

### 12.1 The idea

Keycloak does not push anything to Elasticsearch itself. The clean, supported path is:

```
Keycloak ──(jboss-logging event listener)──▶ log line per event
        ──(--log=file, JSON, ECS format)──▶ /opt/keycloak/data/log/keycloak.log
        ──(shared Docker volume)──▶ Filebeat ──▶ Elasticsearch ──▶ Kibana
                                        └──▶ (optional) Logstash ──▶ Elasticsearch
```

Three Keycloak settings make this work, all already in `docker/elk/docker-compose.yml`:

```yaml
KC_LOG: console,file                       # human-readable console + a file for shipping
KC_LOG_FILE: /opt/keycloak/data/log/keycloak.log
KC_LOG_FILE_OUTPUT: json
KC_LOG_FILE_JSON_FORMAT: ecs               # Elastic Common Schema: @timestamp, log.level, log.logger, message ...
KC_SPI_EVENTS_LISTENER__JBOSS_LOGGING__SUCCESS_LEVEL: info   # successful events are DEBUG by default
```

(Error events such as `LOGIN_ERROR` are logged at WARN by default. The equivalent CLI flag is `--spi-events-listener--jboss-logging--success-level=info`. In older docs you'll see a single-dash form; both work in 26.)

And in the realm: **Realm settings → Events → Event listeners** must contain `jboss-logging` (it does by default, and the setup script sets it explicitly). Admin events are logged by the same listener when *Admin events → Save events* is on.

A real line Keycloak writes with these settings (one JSON object per line):

```json
{"@timestamp":"2026-09-03T09:44:40.575Z","log.logger":"org.keycloak.events","log.level":"INFO",
 "message":"type=\"LOGIN\", realmId=\"2aa96d1d-…\", realmName=\"acme\", clientId=\"acme-cli\", userId=\"4fb6aa21-…\", sessionId=\"Cvhp0I8G…\", ipAddress=\"127.0.0.1\", auth_method=\"openid-connect\", grant_type=\"password\", username=\"alice\"",
 "process.thread.name":"executor-thread-1","service.name":"keycloak","service.environment":"dev","host.hostname":"…"}
```

Notice that the event details are a `key="value", key="value"` string inside `message`. Filebeat (or Logstash) splits that into fields so you can filter on `keycloak.event.type`, `keycloak.event.username`, etc.

### 12.2 Run the whole stack

Copy the `docker/elk` folder to e.g. `C:\keycloak-lab\docker\elk`. It contains `docker-compose.yml`, `filebeat.yml` and `logstash.conf`. Elasticsearch needs memory: in Docker Desktop → Settings → Resources give it at least 4 GB (the file caps Elasticsearch at 1 GB heap). If you get `vm.max_map_count` errors on WSL2, run once:

```powershell
wsl -d docker-desktop -e sysctl -w vm.max_map_count=262144
```

Then:

```powershell
cd C:\keycloak-lab\docker\elk
docker compose up -d
docker compose ps                 # wait until elasticsearch is 'healthy' and kibana is 'running'
docker compose logs -f filebeat   # should end with 'Connection to backoff(elasticsearch(http://elasticsearch:9200)) established'
```

Security is turned off on Elasticsearch/Kibana in this Compose file to keep the tutorial short – acceptable on a laptop, never on a server.

Now generate some events: run `python examples\setup_realm.py` (the realm is new because this is a new database), log in to the SPA a few times, try a wrong password, run the M2M job.

### 12.3 What Filebeat does (`filebeat.yml`)

```yaml
filebeat.inputs:
  - type: filestream
    id: keycloak-logs
    paths: [/var/log/keycloak/keycloak.log*]     # the shared volume
    parsers:
      - ndjson: { target: "", overwrite_keys: true, add_error_key: true }   # each line is JSON → fields

processors:
  - script:                # only for org.keycloak.events lines: parse key="value" pairs into keycloak.event.*
      when.equals.log.logger: org.keycloak.events
      lang: javascript
      source: >
        function process(event) {
          var msg = event.Get("message"); if (!msg) return;
          var re = /(\w+)="([^"]*)"/g, m;
          while ((m = re.exec(msg)) !== null) event.Put("keycloak.event." + m[1], m[2]);
        }

output.elasticsearch:
  hosts: ["http://elasticsearch:9200"]
  index: "keycloak-%{+yyyy.MM.dd}"
setup.template.name: "keycloak"
setup.template.pattern: "keycloak-*"
setup.ilm.enabled: false
```

Result: every Keycloak log line becomes a document with `@timestamp`, `log.level`, `log.logger`, `message`, plus – for event lines – `keycloak.event.type`, `keycloak.event.realmName`, `keycloak.event.clientId`, `keycloak.event.username`, `keycloak.event.ipAddress`, `keycloak.event.error`, and so on.

### 12.4 Optional: Logstash in the middle

If you prefer parsing/enriching in Logstash (GeoIP on the client IP, dropping noisy `REFRESH_TOKEN` events, routing to different indices), uncomment the `logstash` service in the Compose file, switch Filebeat's output to `output.logstash: hosts: ["logstash:5044"]`, and use the provided `logstash.conf`:

```
filter {
  if [log][logger] == "org.keycloak.events" {
    kv { source => "message"  field_split => ", "  value_split => "="  trim_value => "\""  target => "[keycloak][event]" }
    geoip { source => "[keycloak][event][ipAddress]"  target => "[keycloak][geo]" }
    if [keycloak][event][type] =~ /_ERROR$/ { mutate { add_field => { "[keycloak][outcome]" => "failure" } } }
  }
}
output { elasticsearch { hosts => ["http://elasticsearch:9200"]  index => "keycloak-%{+YYYY.MM.dd}" } }
```

### 12.5 See it in Kibana

1. Open http://localhost:5601 → **Discover** (menu ☰ → Analytics → Discover).
2. Create a data view: name `keycloak`, index pattern `keycloak-*`, timestamp field `@timestamp` → Save.
3. Try these KQL queries in the search bar:
   - `log.logger : "org.keycloak.events"` – all user/admin events
   - `keycloak.event.type : "LOGIN_ERROR"` – failed logins
   - `keycloak.event.type : "LOGIN" and keycloak.event.clientId : "acme-spa"` – portal logins
   - `keycloak.event.username : "alice"` – everything Alice did
   - `keycloak.event.type : "CLIENT_LOGIN"` – machine-to-machine token requests
   - `log.level : "ERROR"` – server problems
4. Build a dashboard (**Dashboards → Create**): a bar chart of `keycloak.event.type` over time, a pie of `keycloak.event.clientId`, a table of top `keycloak.event.ipAddress` for `LOGIN_ERROR`.
5. Alerting (**Observability → Alerts → Create rule → Elasticsearch query**): query `keycloak.event.type : "LOGIN_ERROR"`, threshold "more than 20 in 5 minutes", action: email/Slack.

### 12.6 Alternatives worth knowing

- **Elastic's official Keycloak integration** (Fleet / Elastic Agent) ships a ready-made pipeline and dashboard for Keycloak logs; point it at the same log file. Same idea, less YAML, but needs Fleet set up.
- **Syslog straight to Logstash** with no file/Filebeat: `KC_LOG=console,syslog`, `KC_LOG_SYSLOG_ENDPOINT=logstash:5514`, `KC_LOG_SYSLOG_PROTOCOL=tcp`, `KC_LOG_SYSLOG_OUTPUT=json`, and a `syslog`/`tcp` input in Logstash.
- **OpenTelemetry**: `KC_TELEMETRY_LOGS_ENABLED=true` + an OTel collector that exports to Elasticsearch (and also carries Keycloak's traces and metrics). The modern route when you already run a collector.
- **Metrics**: `KC_METRICS_ENABLED=true` exposes Prometheus metrics at `http://localhost:9000/metrics` (logins, token requests, DB pool, JVM). Elastic Agent's Prometheus integration can scrape it.
- **Custom event listener SPI**: a small Java extension that posts every event directly to Elasticsearch/Kafka/webhook. Most flexible, but you now maintain a plugin; only go there when the log route isn't enough.

## 13. Production checklist

Short, because it's a beginner tutorial, but you should know what changes:

1. **`start`, not `start-dev`.** Production mode requires HTTPS and a hostname: `KC_HOSTNAME=https://auth.acme.com`, either TLS certs on Keycloak (`KC_HTTPS_CERTIFICATE_FILE/KEY_FILE`) or a reverse proxy terminating TLS with `KC_HTTP_ENABLED=true` + `KC_PROXY_HEADERS=xforwarded`. Build an optimised image (`kc.sh build`) or set build-time options via env vars.
2. **Real database** (PostgreSQL) with backups. Never the default dev-file DB.
3. **Delete the bootstrap admin** after creating a proper admin with 2FA; enable OTP/passkeys for everyone in `master`.
4. **Client hygiene:** exact redirect URIs, PKCE enforced via a client policy, no implicit flow, no direct access grants unless justified, rotate secrets, prefer signed-JWT/mTLS client auth for services.
5. **Short access tokens** (5–15 min), sensible session idle/max, refresh-token rotation (*Revoke refresh token* on).
6. **Brute force detection on**, password policy set, email verification on, SMTP configured.
7. **Events** saved with expiration, `jboss-logging` on, shipped to ELK with alerts on `LOGIN_ERROR` bursts and admin events.
8. **Themes**: brand the login page so users recognise phishing.
9. **High availability**: 2+ Keycloak nodes behind a load balancer (Keycloak 26 clusters over the DB and Infinispan; use the Operator on Kubernetes).
10. **Upgrade plan**: minor versions are frequent; read the *Upgrading guide* and test realm export/import before upgrading.

## 14. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `Invalid parameter: redirect_uri` on the login page | The client's *Valid redirect URIs* doesn't match exactly (scheme, host, port, path, trailing slash). Add the URL or `http://localhost:3000/*`. |
| SPA gets CORS error calling Keycloak | Client → *Web origins* must contain the SPA's origin (`http://localhost:3000`, no path, no trailing slash). |
| SPA gets CORS error calling *your* API | That's your API's CORS config, not Keycloak's. |
| API says `Invalid audience` | Token's `aud` doesn't contain your API's client id. Attach an *Audience* mapper (client scope) to the calling client, as the script does. |
| API says `Invalid issuer` | The token's `iss` (e.g. `http://localhost:8080/realms/acme`) must equal the URL your API expects. Container-internal hostnames vs `localhost` are the usual mismatch; set `KC_HOSTNAME` consistently. |
| `401 unauthorized_client` on client_credentials | *Service accounts roles* is off, or wrong secret, or the client is public. |
| `Account is not fully set up` | The user has a pending required action (verify email, update password). Clear it under Users → Required actions, or configure SMTP. |
| No events in Kibana | Check: realm listener `jboss-logging` present; `KC_SPI_EVENTS_LISTENER__JBOSS_LOGGING__SUCCESS_LEVEL=info` set (else successes are DEBUG and filtered out); `docker compose logs filebeat` for connection errors; index pattern `keycloak-*` exists (`curl http://localhost:9200/_cat/indices`). |
| Admin console loads but login loops / "HTTPS required" | You ran `start` without hostname/TLS, or `start-dev` behind a proxy. For local work always `start-dev`. |
| Bootstrap admin didn't get created | The DB already existed. Either wipe the volume (`docker compose down -v`) or create a temporary admin with `kc.sh bootstrap-admin user`. |
| Elasticsearch exits with `max virtual memory areas vm.max_map_count [65530] is too low` | `wsl -d docker-desktop -e sysctl -w vm.max_map_count=262144` |

## 15. Glossary

**Access token** – short-lived JWT your API accepts. **Audience (`aud`)** – who a token is for. **Authorization code** – one-time code exchanged for tokens. **Bearer token** – "whoever holds this can use it"; hence short lifetimes and HTTPS. **Broker** – Keycloak acting as a middleman to external IdPs. **Claim** – one key/value inside a token. **Client** – an app registered in a realm. **Client scope** – a bundle of mappers/claims. **Confidential / public client** – can / cannot keep a secret. **Discovery document** – `/.well-known/openid-configuration`. **Federation** – reading users from LDAP/AD. **Grant type / flow** – the way a client obtains tokens. **ID token** – JWT describing the logged-in user, for the front-end. **Introspection** – asking Keycloak online whether a token is valid. **JWKS** – Keycloak's public keys endpoint. **JWT** – signed JSON token format. **Mapper** – rule that copies data into tokens (protocol mapper), from IdPs (IdP mapper) or from LDAP (LDAP mapper). **Offline token** – long-lived refresh token for "keep me signed in". **PKCE** – proof-key extension making public clients safe. **Realm** – isolated tenant in Keycloak. **Refresh token** – gets new tokens silently. **Required action** – a task a user must complete at next login. **Resource server** – an API that verifies tokens. **Role** – permission label (realm-wide or per client). **Service account** – the hidden user behind a machine client. **Session** – server-side record that a user is logged in. **SSO** – one login, many apps.

---

### Sources and further reading

- Keycloak docs: server guides https://www.keycloak.org/guides, Docker getting started https://www.keycloak.org/getting-started/getting-started-docker, all configuration options https://www.keycloak.org/server/all-config, logging https://www.keycloak.org/server/logging, containers https://www.keycloak.org/server/containers, Server administration guide https://www.keycloak.org/docs/latest/server_admin/, Securing applications https://www.keycloak.org/docs/latest/securing_apps/, Admin REST API https://www.keycloak.org/docs-api/latest/rest-api/.
- Release notes: Keycloak 26.7 https://www.keycloak.org/2026/07/keycloak-2670-released.
- Elastic: Keycloak integration https://www.elastic.co/docs/reference/integrations/keycloak, Filebeat filestream input and processors https://www.elastic.co/docs/reference/beats/filebeat.
- OAuth 2.0 / OIDC background in plain language: https://oauth.net/2/ and https://openid.net/developers/how-connect-works/.
