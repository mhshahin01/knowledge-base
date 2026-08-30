# IAM Foundations & User Management: Complete Tutorial

> Last updated: 2026-08-30 | Applicable to: the field as of August 2026
> Difficulty: Beginner | Estimated time: 60 minutes reading, plus 30 minutes optional hands-on

## Tutorial Overview

This tutorial covers **identity and access management (IAM)** from zero: what it is, the three
questions every IAM system answers (authentication, authorization, user management), the core
vocabulary you will reuse in every later part, how authentication factors and methods work, how
user accounts are born, changed, and retired, and where identities are actually stored (LDAP and
Active Directory, application database tables, cloud directories). It closes with a build-vs-buy
decision guide, an optional hands-on track on password hashing, and the classic beginner pitfalls.

*Where this sits in the series:* this is Part 1 of eight, and nothing here assumes any prior
knowledge. It gives you the vocabulary. Part 2 (`002-tokens-anatomy-lifecycle.md`) then explains
tokens, the physical artifacts that protocols like SSO, OAuth 2.0, and OIDC (Parts 3 to 5) move
around. Parts 6 to 8 assemble everything into real login architectures, authorization placement,
and API keys.

After completing this tutorial, you will be able to:

- Explain what IAM is and name the three questions it answers.
- Distinguish authentication from authorization, and both from user management.
- Define the core vocabulary: identity, account, principal, credential, identifier, claim, role,
  permission.
- Describe the three authentication factor types and compare passwords, OTP, biometrics, MFA, and
  passkeys.
- Describe the identity lifecycle (joiner, mover, leaver) and the cost of getting it wrong.
- Choose between building and buying user management, and hash a password correctly yourself.

**How to read it:** Part 1 is sequential, each section builds on the one before. Part 2 is a
skimmable survey of identity stores. Part 3 is practical: a decision guide, an optional hands-on
track, and pitfalls worth reading even if you skip the hands-on. Part 4 and the Appendix are
reference material to return to later.

---

## Table of Contents

- Part 1: Foundations
  - 1. What is IAM?
  - 2. The three questions IAM answers
  - 3. Core vocabulary
  - 4. Authentication factors and methods
  - 5. User management and the identity lifecycle
  - 6. Why IAM is hard (the honest part)
- Part 2: The Landscape (identity stores)
  - 7. The map: three lanes
  - 8. Lane A: LDAP and Active Directory
  - 9. Lane B: Application database tables
  - 10. Lane C: Cloud directories and SaaS identity providers
  - 11. Honorable mentions
- Part 3: Putting It Into Practice
  - 12. How to choose: build vs buy user management
  - 13. Optional hands-on track: a minimal user store with correctly hashed passwords
  - 14. Common misconceptions and pitfalls
- Part 4: Reference
  - 15. Advanced topics and learning path
  - 16. Cheatsheet
  - Appendix: Glossary and sources

---

# Part 1: Foundations

## 1. What is IAM?

**Objective:** give a correct one-sentence definition of IAM and recognize what belongs to it.

**Identity and access management (IAM)** is the discipline of making sure the right people (and
the right programs) can use the right systems and data, and nothing more. It covers both halves
of that sentence: knowing *who* someone is, and controlling *what* they can do.

The one-sentence mental model:

> IAM is the building security office: it keeps the guest list, checks ID at the door, and
> decides which floors each visitor badge can open.

Every digital system you have ever logged into has an IAM layer, even when it is invisible. Some
things IAM handles in practice:

| IAM concern | Concrete example |
|---|---|
| **Who exists** | Your company creates an account for you on your first day |
| **Proving who you are** | You type a password, then approve a prompt on your phone |
| **What you may do** | You can read the team wiki but cannot edit the payroll app |
| **Ending access** | Your accounts are disabled the day you leave the company |

What IAM is *not*: it is not a single product you buy, and it is not only about logging in.
Login is the visible tip. The bulk of IAM is the unglamorous machinery underneath: keeping the
list of users correct, storing credentials safely, and removing access on time.

**Self-check:** A system knows exactly who every user is, but any logged-in user can delete any
file. Is its IAM working? (No: identity is solved, but access control, the second half of the
definition, is missing.)

---

## 2. The three questions IAM answers

**Objective:** name the three questions, and sort any real-world IAM event into the right one.

Almost everything in IAM, and in this whole series, is an answer to one of three questions.
Learn to hear them underneath the jargon.

| The question | The technical name | One-line meaning | Everyday example |
|---|---|---|---|
| Who are you? | **Authentication** (authN) | Proving you are who you claim to be | Showing your passport at the airport |
| What may you do? | **Authorization** (authZ) | Checking what a known user is allowed to do | Your boarding pass says economy, so the lounge says no |
| How do you exist in the system? | **User management** | Creating, updating, and retiring accounts and their data | HR issues your passport years before any airport sees it |

Two things beginners trip over:

- **Authentication comes first, authorization second.** A system can only check what you may do
  once it knows who you are. "Logged in but access denied" is authentication succeeding and
  authorization failing.
- **User management is the quiet third question.** Nobody demos it, but if accounts are created
  late, updated never, or deleted slowly, the first two questions stop mattering, because the
  answers are computed against a wrong list of people.

### Real use cases per question

**Authentication: proving identity matters when the cost of an impostor is high.**

1. *Online banking login.* The bank asks for a password and a phone prompt, because a fake "you"
  can move real money. The cost of skipping this: direct financial theft.
2. *Corporate laptop unlock.* Your fingerprint unlocks the device, because a stolen laptop
  should be a hardware loss, not a data breach.
3. *"Forgot password" email.* Even recovery is authentication: the system proves you control
  the email address before it lets you set a new password.

**Authorization: separating powers matters as soon as more than one kind of user exists.**

1. *A support agent sees tickets but not salaries.* Same company, same login page, different
  permissions. Without authorization, every employee is an admin.
2. *Read-only API access for an analytics tool.* The tool may read orders but not create
  refunds. The cost of skipping this: a buggy dashboard becomes a financial incident.
3. *A customer sees only their own orders.* Authentication says "this is user 48151623";
  authorization says "user 48151623 may only touch orders they own".

**User management: the lifecycle matters wherever people join, move, and leave.**

1. *New hire, day one.* Accounts for email, chat, and the code repository exist before the
  laptop does. Skipping this costs days of idle time per hire.
2. *Promotion to team lead.* The mover case: the person keeps their identity but gains
  permissions on the team's admin tools.
3. *Contractor leaves.* Every account and key is disabled the same day. Skipping this leaves a
  valid login in the hands of someone with no loyalty to you.

### One login, all three questions: a worked example

A nurse starts a shift at a hospital:

1. **User management (before anything happens).** On her first day, HR created her account in
   the hospital directory, with her name, role "nurse", and ward assignment "cardiology".
2. **Authentication (at the workstation).** She taps her badge and types a PIN. The system is
   now confident the person at the keyboard is the account holder.
3. **Authorization (inside the application).** She opens the records system. It lets her see
   cardiology patients, shows orthopedics records as inaccessible, and hides the billing module
   entirely. Same nurse, same login, three different answers.

When she transfers to orthopedics next year, question three (user management) updates her ward,
and question two's answers change automatically. That connection, clean user management feeding
correct authorization, is what "good IAM" means in practice.

**Self-check:** "Invalid password" and "Access denied": which question produced each message?
("Invalid password" is authentication failing, the system does not know who you are. "Access
denied" is authorization failing, the system knows you and still says no.)

---

## 3. Core vocabulary

**Objective:** define the eight terms every later part of this series uses without re-explaining.

These eight words do most of the talking in IAM. Overview first, details below.

- **Identity**: who or what a user or system is, as a set of attributes (name, email, department).
- **Account**: the concrete record in one system that represents an identity there.
- **Principal**: the active party in a request, the "who" the system evaluates (a user, a service).
- **Credential**: the secret or proof used to authenticate (password, key, fingerprint template).
- **Identifier**: the stable name that points at an account (username, user ID, email address).
- **Claim**: a single stated fact about a principal ("department is cardiology"), delivered by
  someone the system trusts.
- **Role**: a named bundle of permissions ("nurse", "team lead") assigned to principals.
- **Permission**: the atomic yes/no answer: may this principal do this action on this thing?

### Details

#### Identity, in detail: the person as data

An identity is the collection of facts a system holds about one entity: name, email, employee
number, department. Three practical things to know as a beginner:

- **One person, many identities.** The same human is "ada@corp.example" at work and
  "ada.lovelace@gmail.example" at home. Identity is per context, not per human.
- **Identity is not proof.** A profile full of correct facts does not prove the person at the
  keyboard owns them. Proof is the credential's job.
- **Programs have identities too.** A backup script or a payment service can be an identity with
  its own account and credentials. IAM is not only about humans.

#### Account, in detail: the record in one system

The account is the row in the database: identifier, credential reference, attributes, status
(active, locked, disabled). The identity is the concept; the account is the paperwork. Deleting
the account ends access in that system even though the person still exists.

#### Principal, in detail: whoever is asking right now

When a request arrives, the system does not evaluate "Ada" the human; it evaluates a principal,
the authenticated subject attached to this specific request. This matters because one account can
produce many principals over time (each login session is a fresh one), and because authorization
rules are always written against principals, never against people.

#### Credential, in detail: the proof, and the thing attackers want

A credential is whatever you present to authenticate: a password, a one-time code, a private key,
a biometric. Two rules follow immediately:

- **Credentials must be protected at rest.** If your user database leaks, the credentials inside
  decide how bad the leak is. This is why Section 13 hashes passwords instead of storing them.
- **Credentials are the most-stolen artifact in the industry.** Section 6 puts a number on it.

#### Identifier, in detail: the pointer, not the person

The identifier is how a system refers to an account: a username, a numeric user ID, an email
address. The one hard rule: identifiers should be stable. If a user changes their email address,
every record keyed on that email now points at a stale string. This is Pitfall 4 in Section 14,
and it is why serious systems use an internal, never-changing ID and treat email as an attribute.

#### Claim, in detail: a fact, asserted by someone trusted

A claim is one statement about a principal: `department: cardiology`, `email_verified: true`.
Claims are everywhere once you reach tokens (Part 2): a token is essentially a signed bundle of
claims. For now, keep the core idea: a claim is only as good as whoever asserts it. The hospital
directory claiming "nurse" is trustworthy; the nurse claiming it herself is not.

#### Role, in detail: permissions in a bundle

Assigning permissions one by one does not scale past a handful of users. A role bundles the
permissions a job needs ("nurse" can read ward records, "team lead" can also approve timesheets),
and you assign the role. The cost: roles drift. People accumulate roles as they change jobs and
rarely lose old ones, so "what can Ada actually do?" becomes hard to answer. That drift is one of
the reasons Part 7 of this series exists.

#### Permission, in detail: the atomic decision

A permission is one checkable statement: principal P may perform action A on resource R.
Authorization (Section 2) is just evaluating permissions, usually through roles. When someone
says "fine-grained" vs "coarse-grained" access control, they mean how small the R is: "can edit
this document" is fine, "is an admin" is coarse.

#### The vocabulary at a glance

| Term | It is the... | Example |
|---|---|---|
| **Identity** | set of facts about who someone is | Ada Lovelace, Engineering, employee #1843 |
| **Account** | record representing that identity in one system | row `ada` in the company directory |
| **Principal** | "who" attached to one request or session | the logged-in session from Ada's laptop |
| **Credential** | proof used to authenticate | her password, her badge tap |
| **Identifier** | stable name pointing at the account | `ada`, or internal ID `usr_01HZX...` |
| **Claim** | one asserted fact about the principal | `department: cardiology` |
| **Role** | named bundle of permissions | `nurse`, `team-lead` |
| **Permission** | one yes/no decision | may read ward records |

**Self-check:** "The token says `role: admin`": which two vocabulary terms appear in that
sentence? (A claim, `role: admin`, asserting that the principal holds the role `admin`.)

---

## 4. Authentication factors and methods

**Objective:** name the three factor types, compare the common authentication methods, and say
what each one costs.

The one-sentence mental model:

> A **factor** is a kind of proof: something you know, something you have, or something you are.

**A real-life picture: the members-only club.** A strict club checks three different things
before letting you in. First, the secret handshake: only members were taught it (something you
know). Second, the membership card: it is a physical object, and knowing the handshake does not
conjure one into your pocket (something you have). Third, the bouncer recognizes your face: it is
part of you and cannot be lent to a friend (something you are). Each check defeats a different
kind of impostor, and demanding two different kinds defeats far more impostors than demanding the
same kind twice.

- **The handshake is a knowledge factor.** Passwords and PINs. Weakness: it can be copied,
  guessed, phished, or written on a sticky note.
- **The membership card is a possession factor.** Your phone, a hardware key, a badge. Weakness:
  it can be lost, stolen, or (for some technologies) cloned.
- **The bouncer's face recognition is an inherence factor.** Fingerprint, face, voice. Weakness:
  it can be spoofed with effort, it cannot be changed if compromised, and it fails for some
  people some of the time (wet fingers, bad lighting).

**Multi-factor authentication (MFA)** means requiring factors from two or more *different* types.
Password plus phone prompt is MFA. Password plus PIN is not: both are knowledge, and an attacker
who phishes one phishes both. The cost of MFA is friction, and organizations that make it
optional discover that most users never opt in.

### The common methods, compared

| Method | Factor type | Cost to you | Main weakness |
|---|---|---|---|
| **Password** | Knowledge | Free to issue, expensive to reset and protect | Reused, guessed, phished |
| **One-time password (OTP)** by authenticator app | Possession (the phone) + knowledge (the code) | User installs an app; you store a shared secret | Phishable in real time by a fake site |
| **OTP by SMS** | Possession (the phone number) | Per-message cost; SIM cards are not strong proof | SIM-swap attacks, intercepted texts |
| **Biometrics** (fingerprint, face) | Inherence | Needs capable hardware; false rejects annoy users | Cannot be revoked; spoofing with effort |
| **Passkeys / passwordless** | Possession (device) + often inherence (local biometric) | Newer stack, device sync questions | Ecosystem still maturing (see below) |
| **MFA (any two different factors)** | Combination | One extra step at login | Users route around it if it is painful |

### Details

#### Passwords, in detail: broken, and still everywhere

Passwords survive because they are free and every user already understands them. Treat them as a
weak first factor, not a wall. Two modern rules from NIST SP 800-63B (revision 4, 2025): do not
force periodic password changes (users respond by making tiny predictable edits), and do not
impose composition rules like "must contain a symbol" (length and breach-screening matter more).
Your job as the system is to store them hashed, never in plaintext (Section 13).

#### One-time passwords, in detail: a code that expires beats a code that lasts

A **one-time password (OTP)** is valid once and briefly, typically a six-digit code that changes
every 30 seconds in an authenticator app. It upgrades "something you know" with "something you
have": stealing the password is no longer enough. Honest cost: a real-time phishing page that
proxies the real site can still relay the code. Hardware-backed methods below resist exactly
that.

#### Biometrics, in detail: convenient, but handle with care

A **biometric** factor measures the person: fingerprint, face, iris. Biometrics are excellent at
*unlocking something local* (your phone, your laptop). They are a poor network credential:
unlike a password, you cannot rotate your fingerprint after a breach. The modern design uses the
biometric only to unlock a key that never leaves the device, which is precisely what passkeys do.

#### Passkeys, in detail: mention only

A **passkey** is a passwordless credential: the device holds a private key, the server holds the
public key, and a local biometric or PIN unlocks it. Nothing secret crosses the network, so there
is nothing to phish or reuse. Depth is deferred: passkeys build directly on the token and
protocol material in Parts 2 to 5. For now: when someone says "passwordless", this is usually
what they mean, and it is where the industry is heading (FIDO Alliance standards).

#### MFA, in detail: the cheapest big win

Requiring any second, different factor blocks the large majority of bulk credential attacks,
because stolen password lists stop being sufficient. Costs to plan for: recovery flows (users
lose phones), support load, and the temptation to exempt "trusted" users, who are exactly the
accounts attackers target.

### Real use cases

1. *Consumer app, millions of users.* Password plus optional authenticator-app OTP. Full MFA
   mandates cause measurable signup abandonment; you trade security for growth, knowingly.
2. *Company email and admin consoles.* Mandatory MFA with hardware keys for admins. The cost of
   an admin account takeover dwarfs the cost of a few $25 keys.
3. *Banking app on a phone.* Device binding (possession) plus fingerprint (inherence). The
   password never leaves the first app install; daily logins are one thumb press.

**Self-check:** A site asks for your password and then your date of birth. Is that MFA? (No:
both are knowledge factors. Two locks of the same type are still one type of lock.)

---

## 5. User management and the identity lifecycle

**Objective:** describe the lifecycle stages of an account and the cost of skipping each.

The one-sentence mental model:

> User management is HR for accounts: every account is hired, promoted or transferred, and
> eventually leaves.

**User management** is everything about how accounts come to exist, stay accurate, and stop
existing. The industry name for the pattern is **joiner, mover, leaver**:

| Stage | What happens | Cost of getting it wrong |
|---|---|---|
| **Joiner** | Account created with the right starting access | New hire sits idle for days, or gets admin access "temporarily" forever |
| **Mover** | Access changes when the role changes | Permissions pile up; after three transfers the user can do almost anything |
| **Leaver** | All access ends at departure | A valid login stays in the hands of an ex-employee or attacker |

The verbs behind the table: **provisioning** is creating accounts and granting access;
**deprovisioning** is removing both. Provisioning is usually semi-automated and celebrated.
Deprovisioning is usually manual, forgotten, and the reason Section 6 exists.

### Details

#### Provisioning, in detail: where accounts come from

Accounts are created in one of three ways: an admin creates them (invite, HR feed), users create
their own (self-registration), or an external system pushes them (a directory sync). Each has a
different failure mode: admins forget, self-registration invites junk and bots, and sync breaks
silently, so the joiner/mover/leaver feed must be monitored like any other production job.

#### Profile management, in detail: keeping the facts true

Email addresses change, names change, departments change. Someone must be able to update these,
and the system must record who changed what. Note the two audiences: the user edits their own
profile (name, photo, phone), while attributes that drive authorization (department, role) must
only be editable by an admin, or every user is one profile edit away from a promotion.

#### Deprovisioning, in detail: the stage everyone underfunds

Deprovisioning means disabling the account, ending sessions, revoking keys, and eventually
deleting the record (retention rules may require keeping audit history). Partial deprovisioning,
where the main login dies but an API token or a secondary app keeps working, is the common real-
world failure. Section 14, Pitfall 3, shows what it looks like in practice.

#### Directories, in detail: one list instead of forty

A **directory** is a central system that stores identities and attributes so that forty
applications do not each keep their own diverging copy. Instead of creating "ada" in email, chat,
and the wiki separately, you create her once in the directory and each application consults it.
This idea, one identity consulted by many applications, is the seed of single sign-on in Part 3.
Part 2 of this tutorial surveys the three kinds of stores you will actually meet.

#### Self-service vs admin-managed, in detail

| | Self-service | Admin-managed |
|---|---|---|
| **What it means** | Users register, reset passwords, edit profiles themselves | Staff create, change, and close accounts |
| **Cost** | You must build safe flows (email verification, reset tokens, bot defenses) | Staff time per request; queue delays |
| **Fits** | Consumer apps, large user bases | Small teams, high-assurance environments |
| **Main risk** | Weak verification lets anyone claim any email | Slow deprovisioning, lingering access |

Most real systems mix both: self-service for registration and password reset, admin-managed for
roles and offboarding.

### Real use cases

1. *SaaS startup.* Full self-service: sign-up with email verification, self-service password
   reset, workspace invites. Admin time per user would not survive 10,000 sign-ups.
2. *Hospital.* HR system is the source of truth: hiring a nurse automatically provisions the
   directory account; termination disables it within minutes. Self-service is limited to profile
   fields.
3. *Open-source community platform.* Self-registration plus volunteer moderators who can disable
   accounts, a hybrid with clear limits on what moderators may touch.

**Self-check:** An ex-intern's account still works six months after their internship ended.
Which lifecycle stage failed? (Leaver: deprovisioning. The mover and joiner stages were fine;
access was simply never ended.)

---

## 6. Why IAM is hard (the honest part)

**Objective:** state, with numbers, why credentials and offboarding are where IAM fails in
practice.

IAM looks like solved plumbing until you read the breach reports. Three hard numbers:

- **Stolen credentials are the most common way in.** The Verizon 2025 Data Breach Investigations
  Report (12,195 confirmed breaches analyzed) found credential abuse was an initial access vector
  in **22% of breaches**, the leading vector for the second year running. Not zero-days, not
  exotic malware: usernames and passwords that already worked.
- **The bill is measured in millions.** IBM's Cost of a Data Breach Report 2025 put the global
  average cost of a breach at **$4.44 million** (down from $4.88 million in 2024, the first drop
  in five years, but hardly cheap).
- **Leavers stay inside.** A OneLogin survey of IT decision makers (2017, dated but still widely
  cited) found that half of organizations left ex-employee accounts active for more than a day
  after departure, and a quarter for a week or more. Every day of lag is a day a valid login
  belongs to someone with no reason to protect you.

Three structural reasons these numbers persist:

- **Passwords leak in bulk and get reused.** Every breached site publishes a credential list, and
  attackers replay those lists against other sites (**credential stuffing**). Your users' password
  hygiene is only as strong as the weakest site they ever used, which you do not control. This is
  why Section 4 pushes MFA and Section 13 hashes passwords properly.
- **Takeover beats break-in.** Guessing or buying a valid credential is cheaper than exploiting
  software, because a valid login looks like normal traffic. Detection, not prevention, is often
  the only signal you get.
- **Offboarding is a process problem wearing a technical costume.** The technology to disable an
  account is trivial. The failure is organizational: nobody owns the mover/leaver feed, contractors
  are not in the HR system, and access sprawls across forty tools nobody inventoried.

**Self-check:** Your app has strong password hashing and enforced MFA. Which of the three hard
problems above is still untouched? (Offboarding: account lifecycle hygiene is independent of
credential strength, so leavers with MFA accounts are still leavers with working accounts.)

---

# Part 2: The Landscape (identity stores)

Every account from Part 1 has to live somewhere. This Part surveys the three kinds of identity
stores you will meet in the wild. Version-stamped, as of August 2026, because this Part goes
stale first.

## 7. The map: three lanes

| Lane | What it is | Who typically owns it | When you meet it |
|---|---|---|---|
| **A. LDAP / Active Directory** | A dedicated directory server, often decades old | IT operations | Enterprises, governments, universities |
| **B. Application database tables** | A `users` table inside your own app database | Your dev team | Small apps, startups, prototypes |
| **C. Cloud directories / SaaS IdPs** | Identity as a hosted service | A vendor (you configure it) | Modern SaaS, mobile apps, anything new |

The lanes are not mutually exclusive. A common enterprise reality: lane A holds the workforce,
lane C fronts the customer app, and lane B still exists inside a legacy internal tool nobody
dares to migrate.

---

## 8. Lane A: LDAP and Active Directory

**What it is.** **LDAP** (Lightweight Directory Access Protocol) is the standard protocol for
querying a directory: a tree of entries (people, groups, machines) with attributes. **Active
Directory (AD)** is Microsoft's directory product, which speaks LDAP plus several Microsoft
extensions, and sits at the center of most corporate Windows environments. Open-source
implementations include OpenLDAP and FreeIPA.

**Who it is for.** Organizations with hundreds to hundreds of thousands of internal users, where
one authoritative list must feed email, VPN, file shares, and internal apps.

**What it costs you.** Real operational weight: replication, schema design, backups, and a
specialist skill set. Integrating an application with LDAP is fiddly (binds, base DNs, group
lookups), and AD creates strong gravity toward the Microsoft ecosystem.

**Version landmarks.** OpenLDAP 2.6 is the current stable line; Windows Server 2025 is the
current AD host release (both as of August 2026; verify before building on either).

Flavor sketch, an LDAP entry in LDIF format:

```ldif
dn: uid=ada,ou=people,dc=corp,dc=example
objectClass: inetOrgPerson
uid: ada
cn: Ada Lovelace
mail: ada@corp.example
memberOf: cn=engineering,ou=groups,dc=corp,dc=example
```

---

## 9. Lane B: Application database tables

**What it is.** A `users` table in your application's own database: identifier, password hash,
profile fields, maybe a roles column. Nearly every web framework ships with this pattern built
in.

**Who it is for.** Small applications with one database, one team, and no need to share identity
with other systems. It is the fastest way to a working login and the right default for a
prototype.

**What it costs you.** You own everything: hashing, reset flows, email verification, lockouts,
breach response, and the lifelong guilt of the mover/leaver columns. It also does not scale
sideways: the day a second application needs the same users, you are building lane C by hand,
badly.

Flavor sketch, the table (note what is and is not stored):

```sql
CREATE TABLE users (
    id            TEXT PRIMARY KEY,      -- stable internal identifier, never changes
    email         TEXT UNIQUE NOT NULL,  -- attribute, not the primary key (Section 3)
    password_hash TEXT NOT NULL,         -- bcrypt/argon2 output, never the password (Section 13)
    display_name  TEXT,
    created_at    TIMESTAMP NOT NULL,
    disabled_at   TIMESTAMP              -- leaver switch: set it, and login stops
);
```

---

## 10. Lane C: Cloud directories and SaaS identity providers

**What it is.** An **identity provider (IdP)** is a service that stores identities and performs
authentication on behalf of your applications. In this lane the IdP is hosted: you configure
users, policies, and MFA in a web console, and your app delegates login to it. Examples (as of
August 2026): Microsoft Entra ID (formerly Azure AD), Okta, AWS Cognito, Firebase Auth,
Keycloak as the self-hosted open-source option.

**Who it is for.** Teams that want MFA, social login, breach screening, and reset flows without
building them, and any architecture with more than one application sharing users.

**What it costs you.** Per-user pricing that grows with success, vendor lock-in (your user
records and policies live in their model), a runtime dependency on their uptime, and a learning
curve of product-specific concepts. The protocols your app uses to talk to them (SAML, OAuth
2.0, OIDC) are Parts 3 to 5 of this series; the hands-on work with a real IdP (Keycloak) starts
in Part 4.

**Self-check (lanes):** Your two-person startup is building its first SaaS product and expects a
second app next year. Which lane? (Lane C: lane B fits one app, but the second app turns your
`users` table into a hand-rolled IdP, the worst of both worlds.)

---

## 11. Honorable mentions

- **HR systems as identity source.** Workday, SAP SuccessFactors and similar often *originate*
  the joiner/mover/leaver feed into a directory, even though they are not directories themselves.
- **Social login providers.** "Sign in with Google/Apple/GitHub" outsources authentication to the
  consumer IdPs; the mechanics are OAuth 2.0 and OIDC (Parts 4 and 5).
- **Kerberos.** The ticket-based authentication protocol inside Windows domains; positioned in
  Part 3's protocol map.
- **Password managers.** Not an identity store, but the reason "unique password per site" is
  achievable advice; encourage them, your credential-stuffing risk drops with every user who has
  one.

---

# Part 3: Putting It Into Practice

## 12. How to choose: build vs buy user management

| Your situation | Start with |
|---|---|
| Prototype or side project, one app, few users | **Build**: framework's built-in auth + `users` table (lane B), bcrypt from day one |
| Startup with growth ambitions or a second app coming | **Buy**: a SaaS IdP (lane C); migrating a live user base later is painful |
| Enterprise with existing AD/LDAP | **Integrate**: connect apps to the directory (lane A); never build a second source of truth |
| Regulated environment (health, finance, government) | **Buy or integrate**: audit trails, MFA, and joiner/mover/leaver automation are hard to build well |
| Hard requirement to self-host (data residency, air gap) | **Buy, self-hosted**: open-source IdP such as Keycloak instead of hand-rolled tables |

Two practical truths:

1. **The concepts transfer; the products churn.** Provisioning, factors, roles, and the three
   questions look the same in every tool from AD to Cognito. Learn the vocabulary once (Sections
   2, 3, 5) and each new console is just a new skin on it.
2. **If you build, the password storage decision outlives every other decision.** UI frameworks
   come and go; the day your `users` table leaks, the only thing that matters is whether the
   hashes were bcrypt/argon2 or something weaker. That is exactly what Section 13 practices.

---

## 13. Optional hands-on track: a minimal user store with correctly hashed passwords

**Objective:** store a password so that a leaked database does not leak the password. Project
root: `hands-on/part-01/`.

You will build a tiny user store twice: first the way that causes breaches, then the correct way,
and watch the difference with your own eyes. No IdP needed yet; that starts in Part 4.

### Step 1: Set up the environment

Requires Python 3.10 or newer.

```bash
mkdir -p hands-on/part-01 && cd hands-on/part-01
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install bcrypt
```

Verify the installation:

```bash
python -c "import bcrypt; print(bcrypt.__version__)"
# Expected output: a version like 4.2.x or 5.x (any recent major version is fine)
```

### Step 2: The bad version, plaintext storage (do this once, then never again)

Create `bad_store.py`:

```python
# Bad: passwords stored as-is. If this file leaks, every account is compromised instantly.
users = {}

def register(username, password):
    users[username] = password            # the password itself is the record

def login(username, password):
    return users.get(username) == password

register("ada", "correct horse battery staple")
print("login works:", login("ada", "correct horse battery staple"))
print("what an attacker sees in the DB:", users)
```

Run it:

```bash
python bad_store.py
# Expected output:
# login works: True
# what an attacker sees in the DB: {'ada': 'correct horse battery staple'}
```

The second line is the entire point: a database leak hands the attacker working credentials,
for this site and, thanks to reuse (Section 6), probably for other sites too.

### Step 3: The good version, salted and slow hashing

**Hashing** turns a password into a fixed-looking string that cannot be turned back. A **salt**
is a random value mixed in so two identical passwords produce different hashes. The right tool is
a deliberately slow password hash: **bcrypt** or **Argon2** (OWASP recommends Argon2id first,
bcrypt as a solid alternative). Fast hashes like MD5 or SHA-256 are wrong here: fast for you
means fast for the attacker's GPU rig.

Create `good_store.py`:

```python
# Good: store only a salted bcrypt hash. The DB can leak without leaking passwords.
import bcrypt

users = {}

def register(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    users[username] = hashed              # bytes like b'$2b$12$...' never the password

def login(username, password):
    stored = users.get(username)
    return stored is not None and bcrypt.checkpw(password.encode(), stored)

register("ada", "correct horse battery staple")
print("correct password:", login("ada", "correct horse battery staple"))
print("wrong password:  ", login("ada", "tr0ub4dor"))
print("what an attacker sees in the DB:", users)
```

Run it:

```bash
python good_store.py
# Expected output (your hash string will differ, that is the salt working):
# correct password: True
# wrong password:   False
# what an attacker sees in the DB: {'ada': b'$2b$12$<53 random-looking characters>'}
```

The `$2b$12$` prefix tells you the algorithm (`2b` = bcrypt) and the cost factor (`12`). The
attacker with this file must now guess passwords one by one against a deliberately slow hash,
which is the difference between "breach on the news" and "breach nobody can exploit quickly".

### Step 4: Prove the salt works

```bash
python -c "
import bcrypt
p = b'same-password'
print(bcrypt.hashpw(p, bcrypt.gensalt()))
print(bcrypt.hashpw(p, bcrypt.gensalt()))
"
# Expected output: two DIFFERENT hashes of the same password, e.g.
# b'$2b$12$xxxxxxxxxxxxxxxxxxxxxx...'
# b'$2b$12$yyyyyyyyyyyyyyyyyyyyyy...'
```

Two users with the same password now have unrelated hashes, so a leaked table reveals nothing
about who shares a password, and precomputed "rainbow tables" are useless.

*Variant:* to try Argon2id instead, `pip install argon2-cffi`, then
`from argon2 import PasswordHasher; PasswordHasher().hash("...")`. Same shape: salt handled for
you, store the string, verify with `ph.verify(stored, candidate)`.

---

## 14. Common misconceptions and pitfalls

**Pitfall 1: "We authenticated them, so the request is authorized."**
Symptom: any logged-in user can open any record by changing an ID in the URL. Cause:
authentication and authorization were merged into "logged in = allowed". Fix: check a permission
for the specific resource on every request, after authentication; re-read Section 2.

**Pitfall 2: "The passwords are in the database, but it is encrypted/the server is safe."**
Symptom: a backup or SQL injection leak exposes working passwords for every user. Cause:
plaintext or fast-hash (MD5, SHA-1, plain SHA-256) storage. Fix: bcrypt with cost >= 12 or
Argon2id, as in Section 13; the database must be safe to *leak*.

**Pitfall 3: "We disabled their login, so the ex-employee is out."**
Symptom: a departed contractor's API token or secondary app access still works months later.
Cause: partial deprovisioning, the leaver checklist covered the main login only. Fix: one
deprovisioning runbook that disables the account, kills sessions, revokes tokens and keys, across
every system that issued any; re-read Section 5.

**Pitfall 4: "Email is the user ID."**
Symptom: a user changes their email and loses their history; worse, a recycled email address
inherits a stranger's account. Cause: an attribute (email) was used as the stable identifier.
Fix: generate an internal ID that never changes, treat email as a verified, changeable attribute;
re-read Section 3 (identifier).

**Pitfall 5: "MD5 was fine when we built this."**
Symptom: a 2012-era user table with `md5(password)` hashes survives every migration. Cause:
hashing algorithms age, GPUs get faster, yesterday's cost factor becomes trivial. Fix: plan
re-hashing at login (verify with the old scheme, immediately store with the new one) and review
the OWASP Password Storage Cheat Sheet periodically; re-read Section 13.

---

# Part 4: Reference

## 15. Advanced topics and learning path

**Recommended learning order:** Part 2 of this series (tokens) to Part 3 (SSO) to Part 4
(OAuth 2.0). You now have the vocabulary; next you need the artifact (tokens) that every
protocol moves around, then the user-facing goal (SSO), then the protocols themselves.

**Direction 1: Tokens, anatomy and lifecycle** | Difficulty: Beginner
The very next part, `002-tokens-anatomy-lifecycle.md`: what a token is, how a JWT is put
together, and why "decoding is not verifying".

**Direction 2: Passwordless and passkeys** | Difficulty: Intermediate
The possession-plus-biometric model sketched in Section 4. Recommended resources: FIDO Alliance
passkey documentation, and NIST SP 800-63B (revision 4, 2025) for the verifier rules.

**Direction 3: Reading breach reports like a practitioner** | Difficulty: Beginner
The Verizon DBIR and IBM Cost of a Data Breach reports (Section 6) are published annually.
Reading one cover to cover teaches more IAM judgment than most product documentation.

**Hands-on project suggestions:**

1. **Extend the Section 13 store**: add password change, account disable (leaver switch), and a
   migration from a weak hash to bcrypt on next login. Concepts: Sections 5, 13, Pitfalls 2 and 5.
2. **Lifecycle audit spreadsheet**: pick any system you use, list its joiner/mover/leaver events,
   and note who triggers each and how fast. Concepts: Section 5.
3. **Factor inventory**: list every login in your own life, classify the factors, and find the
   accounts with no second factor. Concepts: Section 4.

**Best practices:**

- Never store passwords in plaintext, and never roll your own hash scheme; use bcrypt or Argon2id.
- Use a stable internal identifier for every account; treat email as a changeable attribute.
- Automate deprovisioning, and audit leavers quarterly against the account list.
- Offer MFA everywhere, require it for admins.
- Screen new passwords against known-breached lists instead of forcing composition rules.

---

## 16. Cheatsheet

**Definition:** IAM is the discipline of making sure the right people (and the right programs)
can use the right systems and data, and nothing more.

**The three questions, always in this order:**

```text
1. Who are you?                    -> authentication  (credential check)
2. What may you do?                -> authorization   (permission check, post-login)
3. How do you exist in the system? -> user management (provision, update, deprovision)
```

**Vocabulary:** identity (the facts) - account (the record) - principal (who is asking) -
credential (the proof) - identifier (stable pointer) - claim (asserted fact) - role (bundle) -
permission (one yes/no).

**Factors:** know (password) / have (phone, key) / are (biometric). MFA = two *different* types.

**Lifecycle:** joiner (provision) - mover (adjust) - leaver (deprovision everything, everywhere).

**Password storage (OWASP):** Argon2id preferred; bcrypt cost >= 12 acceptable; never MD5/SHA-*
fast hashes; salt is automatic in both.

**Key number:** stolen credentials were an initial access vector in 22% of breaches (Verizon
DBIR 2025), the most common way in; the average breach costs $4.44M (IBM 2025).

**Version landmarks (as of August 2026):**

| Thing | Milestone |
|---|---|
| NIST SP 800-63B | Revision 4 (2025): no forced rotation, no composition rules |
| OWASP Password Storage Cheat Sheet | Argon2id first choice, bcrypt acceptable |
| Argon2 | RFC 9106 (2021) |
| Verizon DBIR | 2025 edition: credential abuse top initial vector (22%) |
| IBM Cost of a Data Breach | 2025 edition: $4.44M global average |
| OpenLDAP / Windows Server | 2.6 stable / Windows Server 2025 (verify before building) |

**Quick troubleshooting:**

| Symptom | Likely cause | Quick fix |
|---|---|---|
| "Invalid password" for correct password | Identifier mismatch or stale hash after email change | Look up by internal ID; re-read Pitfall 4 |
| Leaked DB exposes working passwords | Plaintext or fast-hash storage | bcrypt/Argon2id; re-read Section 13 |
| Ex-employee still has access | Partial deprovisioning | One runbook covering sessions, tokens, all apps; re-read Section 5 |
| "Logged in but forbidden" confused with login failure | authN/authZ conflation | Separate the two checks; re-read Section 2 |

---

## Appendix

### Glossary

| Term | Definition |
|---|---|
| **Identity and access management (IAM)** | The discipline of ensuring the right people and programs can use the right systems and data, and nothing more |
| **Authentication (authN)** | Proving a principal is who it claims to be |
| **Authorization (authZ)** | Deciding what an authenticated principal is allowed to do |
| **User management** | Creating, updating, and retiring accounts and their attributes |
| **Identity** | The set of attributes a system holds about one entity |
| **Account** | The concrete record representing an identity in one system |
| **Principal** | The authenticated subject attached to a request or session |
| **Credential** | The secret or proof presented to authenticate (password, key, biometric) |
| **Identifier** | The stable name that points at an account; should never change |
| **Claim** | A single asserted fact about a principal, trustworthy only as its issuer |
| **Role** | A named bundle of permissions assigned to principals |
| **Permission** | One yes/no decision: principal, action, resource |
| **Factor** | A category of authentication proof: knowledge, possession, or inherence |
| **Multi-factor authentication (MFA)** | Requiring proofs from two or more different factor types |
| **One-time password (OTP)** | A code valid once and briefly, typically 30 seconds in an authenticator app |
| **Biometric** | An inherence factor measured from the person (fingerprint, face, iris) |
| **Passkey** | A passwordless credential: private key on the device, public key on the server |
| **Provisioning** | Creating accounts and granting initial access |
| **Deprovisioning** | Removing access and disabling or deleting accounts at the end of the lifecycle |
| **Joiner, mover, leaver** | The three lifecycle events: arriving, changing role, departing |
| **Directory** | A central store of identities and attributes consulted by many applications |
| **LDAP** | The standard protocol for querying a directory tree of entries |
| **Active Directory (AD)** | Microsoft's directory product, central to most corporate Windows environments |
| **Identity provider (IdP)** | A service that stores identities and performs authentication for applications |
| **Hashing** | One-way transformation of a password into an irreversible string |
| **Salt** | Random value mixed into a hash so identical passwords hash differently |
| **bcrypt** | A deliberately slow password hashing function with a tunable cost factor |
| **Argon2** | The memory-hard password hashing function (RFC 9106); OWASP's first choice |
| **Credential stuffing** | Replaying username/password lists leaked from one site against others |

### Sources (as referenced in this tutorial)

- Verizon, "2025 Data Breach Investigations Report" (April 2025): credential abuse as initial
  access vector in 22% of breaches, leading vector; 12,195 confirmed breaches analyzed.
- IBM, "Cost of a Data Breach Report 2025" (July 2025): $4.44M global average breach cost, down
  from $4.88M in 2024.
- OneLogin, "The Curse of the Ex-Employees" survey (2017): half of organizations leave
  ex-employee accounts active more than a day, a quarter a week or more. Dated; treat as
  directional.
- NIST, "SP 800-63B Digital Identity Guidelines, Authentication and Authenticator Management",
  revision 4 (2025): no forced periodic password changes, no composition rules.
- OWASP, "Password Storage Cheat Sheet" (accessed August 2026): Argon2id recommended, bcrypt
  acceptable with sufficient work factor.
- IETF, RFC 9106, "Argon2 Memory-Hard Function" (September 2021): the Argon2 specification.

*Note: this tutorial reflects the field as of August 2026. Breach statistics are republished
annually, product versions drift, and the OneLogin figure is old; verify version-specific claims
against official documentation before building on them.*
