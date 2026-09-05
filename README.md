# Knowledge Base

A personal, long-lived engineering knowledge base: distilled notes, decision records, patterns, and
reference material on backend engineering, system design, AI, and product management.

The goal is **retrieval, not collection**. Every note should answer a question I have actually hit,
in enough depth that I do not need to re-derive the answer from scratch six months later. Anything
that is only a link dump belongs in a bookmark manager, not here.

> **Status:** the taxonomy below is in place and notes are landing in it. Directories still held by a
> `.gitkeep` marker are placeholders: they define where a topic will live, not that content exists
> yet. Sections with notes in them are listed under their entry in the index.

---

## Index

### `ai/`

Notes on applied AI engineering, from first principles up to production systems.

| Path | Scope |
| --- | --- |
| `ai/foundation/00 prerequisites/` | What to know before the AI material: a from-zero Python course that ends at a first Pydantic AI app, and a no-code AI-for-product-managers series. |
| `ai/foundation/` | Core concepts: model families, tokenisation, embeddings, context windows, prompting, evaluation, and the vocabulary needed to read the rest of the field. |
| `ai/foundation/agentic-ai/tutorials/` | The numbered agentic-AI series: the reason/act/observe loop, Pydantic AI, stateful chat agents, retrieval, and MCP. Each part builds on the previous one. A plan file extends the series through 011. |
| `ai/foundation/agentic-ai/hands-on/` | Runnable companions to the tutorials, one numbered subfolder per exercise. Code that is meant to be executed lives here rather than inline in a note. |
| `ai/foundation/llm/` | Large language models themselves: architecture, training and fine-tuning, inference behaviour, sampling parameters, context handling, and evaluation. |

**Prerequisites**

| Note | What it covers |
| --- | --- |
| [`00 prerequisites/pythons-basics/`](ai/foundation/00%20prerequisites/pythons-basics/) | Python Foundations for AI: 13 chunks from running your first script through type hints, classes, async, JSON and HTTP, Pydantic, and a first Pydantic AI application. Python 3.14, every example a runnable file. |
| [`00 prerequisites/ai-for-product-managers/`](ai/foundation/00%20prerequisites/ai-for-product-managers/) | AI for Product Managers: the agentic-AI series consolidated for non-engineers. Eight linked parts, no code: what agents are, why they fail and what they cost, memory, RAG, integrations and MCP, trust and safety, voice, and shipping with measurement. |

**Tutorials in place**

| Note | What it covers |
| --- | --- |
| [`tutorials/001-agentic-ai-basics.md`](ai/foundation/agentic-ai/tutorials/001-agentic-ai-basics.md) | What agents are, the reason/act/observe loop, agent anatomy, the core design patterns, failure modes, and the 2026 framework landscape. |
| [`tutorials/002-pydantic-ai-basics.md`](ai/foundation/agentic-ai/tutorials/002-pydantic-ai-basics.md) | Pydantic AI from zero: agents, message roles, `instructions` versus `system_prompt`, structured output, tools, dependencies, grounding, retries, evals, and cost. |
| [`tutorials/003-agentic-ai-level-2.md`](ai/foundation/agentic-ai/tutorials/003-agentic-ai-level-2.md) | Evolving the 002 agent into a stateful, cost-aware, production-grade chat agent: conversation memory, budgets, guards, approval gates, and resilience against a bad provider day. |
| [`tutorials/004-rag.md`](ai/foundation/agentic-ai/tutorials/004-rag.md) | Retrieval-augmented generation: giving the agent knowledge it does not have through chunking, embeddings, and vector search, plus vector-backed long-term memory and embedding caches. |
| [`tutorials/005-mcp.md`](ai/foundation/agentic-ai/tutorials/005-mcp.md) | Model Context Protocol: how the protocol works on the wire, consuming MCP servers from Pydantic AI, exposing your own service, and when the protocol beats a hand-written tool. |
| [`tutorials/plan-tutorials-003-011.md`](ai/foundation/agentic-ai/tutorials/plan-tutorials-003-011.md) | The plan for the rest of the series (006–011): multi-agent basics, observability, level-2 evals, an agent built from scratch with a production-readiness checklist, LangGraph and durable execution, security and production operations, voice agents, reference architectures (waku, Hermes), and a real-life capstone project. |

**Hands-on exercises**

| Exercise | What it covers |
| --- | --- |
| [`hands-on/001-pydantic-ai/001-mapping-intent/`](ai/foundation/agentic-ai/hands-on/001-pydantic-ai/001-mapping-intent/) | Intent mapping via tool calls, with the scope guard *asked for* in the system prompt. Demonstrates the two ways that guard fails. Chat UI included. |
| [`hands-on/001-pydantic-ai/002-mapping-intent-enforced/`](ai/foundation/agentic-ai/hands-on/001-pydantic-ai/002-mapping-intent-enforced/) | The same capabilities with the guard *enforced in code*: typed intents validated by Pydantic, a single-intent and a multi-intent router, and code-owned replies the model cannot write. |
| [`hands-on/001-pydantic-ai/002-mapping-intent-enforced/python-basics.md`](ai/foundation/agentic-ai/hands-on/001-pydantic-ai/002-mapping-intent-enforced/python-basics.md) | Language companion to the exercise above: every Python feature its two agent files use, explained from scratch. No AI content. |
| [`hands-on/001-pydantic-ai/003-openai-wrapper/`](ai/foundation/agentic-ai/hands-on/001-pydantic-ai/003-openai-wrapper/) | The same one-shot call written twice, raw OpenAI SDK against Pydantic AI, to show what the framework absorbs. Also where reasoning tokens become visible. |
| [`hands-on/001-pydantic-ai/004-multi-model-wrapper/`](ai/foundation/agentic-ai/hands-on/001-pydantic-ai/004-multi-model-wrapper/) | One wrapper, three backends (OpenAI, Anthropic, a local Ollama model): swapping the model on one line, then checking whether the models are actually interchangeable. |
| [`hands-on/003-agentic-ai-lvl-2/`](ai/foundation/agentic-ai/hands-on/003-agentic-ai-lvl-2/) | Conversation memory made undeniable: five scripted turns run twice, once continuing with `all_messages()` and once with `new_messages()`. Companion to Section 1 of tutorial 003. |

### `backend/`

Language- and framework-level engineering practice: how to actually build the service once the
design is settled.

| Path | Scope |
| --- | --- |
| `backend/java/language/` | The Java language and platform itself: records, sealed types, pattern matching, virtual threads, the memory model, collections, and JVM behaviour. |
| `backend/java/spring-boot/` | Spring Boot application concerns: dependency injection, configuration, data access, transactions, validation, security, testing, and observability wiring. |
| `backend/python/` | Python for backend work: language features, typing, packaging and environments, async, and the web/service frameworks around it. Still a placeholder: the Python language material written so far lives with the AI notes, at [`00 prerequisites/pythons-basics/`](ai/foundation/00%20prerequisites/pythons-basics/) and [`python-basics.md`](ai/foundation/agentic-ai/hands-on/001-pydantic-ai/002-mapping-intent-enforced/python-basics.md). |

### `system-design/`

Design-level material: the decisions made before the first line of service code is written, and the
infrastructure those decisions imply.

#### Identity and access management

| Path | Scope |
| --- | --- |
| `system-design/identity-access-management-iam/tutorials/` | The numbered IAM series: foundations and user management, tokens, single sign-on, OAuth 2.0, and the protocols and products that deliver them. |
| `system-design/identity-access-management-iam/hands-on/` | Runnable companions to the IAM tutorials: a Keycloak Docker Compose stack and per-part scripts and realm exports. |

**Tutorials in place**

| Note | What it covers |
| --- | --- |
| [`tutorials/001-iam-foundations-user-management.md`](system-design/identity-access-management-iam/tutorials/001-iam-foundations-user-management.md) | IAM from zero: authentication, authorization, and user management, the core vocabulary, authentication factors and methods, the account lifecycle, identity stores (LDAP, Active Directory, database tables, cloud directories), and build versus buy. |
| [`tutorials/002-tokens-anatomy-lifecycle.md`](system-design/identity-access-management-iam/tutorials/002-tokens-anatomy-lifecycle.md) | Tokens from zero: opaque versus self-contained, JWT anatomy with a decoded example, access, refresh, and ID tokens, correct validation, the lifecycle from issuance to revocation, and safe transport and storage. |
| [`tutorials/003-single-sign-on-sso.md`](system-design/identity-access-management-iam/tutorials/003-single-sign-on-sso.md) | Single sign-on: the goal and its costs, the sessions and cookies underneath every login, the central login server and redirect mechanics, federation and trust, and a map of the protocols (SAML, OAuth 2.0, OIDC). |
| [`tutorials/004-oauth-2.md`](system-design/identity-access-management-iam/tutorials/004-oauth-2.md) | OAuth 2.0: the delegation problem it solves, why 1.0 and 2.0 are different protocols, the four roles, the grant types and which are deprecated, a full authorization code with PKCE trace, scopes and consent. |
| [`tutorials/004 keycloak-tutorial companion/`](system-design/identity-access-management-iam/tutorials/004%20keycloak-tutorial%20companion/) | Keycloak from zero on Docker (26.7.3): the ideas first, then realm setup, and worked examples for a SPA, a native app, a machine-to-machine job, a protected API, a partner identity provider, and ELK log shipping. |
| [`hands-on/part-04/`](system-design/identity-access-management-iam/hands-on/part-04/) | The OAuth 2.0 hands-on: a realm export to import into the Compose stack and a script that walks the token endpoint. |

#### Architectural patterns

| Path | Scope |
| --- | --- |
| `system-design/architecture/domain-driven-architecture/` | Bounded contexts, aggregates, ubiquitous language, context mapping, and translating a domain model into service boundaries. |
| `system-design/architecture/event-driven-architecture/` | Asynchronous integration between services: events versus commands, topic design, delivery guarantees, idempotency, and ordering. |
| `system-design/architecture/event-sourcing/` | Persisting state as an append-only event log: event store design, replay, snapshots, and schema evolution over time. |
| `system-design/architecture/cqrs/` | Separating the write model from the read model: projections, read-model rebuilds, and the eventual consistency that comes with them. |
| `system-design/architecture/saga/` | Distributed transactions without two-phase commit: choreography versus orchestration, compensating actions, and failure handling. |

#### Distributed systems and infrastructure

| Path | Scope |
| --- | --- |
| `system-design/microservices/` | Service decomposition, data ownership, inter-service communication, versioning, and the operational cost of the style. |
| `system-design/api-gateway/` | Edge concerns: routing, authentication, rate limiting, request aggregation, and where cross-cutting logic belongs. |
| `system-design/load-balancers/` | Traffic distribution: L4 versus L7, algorithms, health checking, session affinity, and failover behaviour. |
| `system-design/caching/` | Cache strategies and invalidation, layer placement, hit-rate reasoning, stampede protection, and consistency trade-offs. |
| `system-design/databases/` | Storage selection, data modelling, indexing, transactions and isolation levels, replication, partitioning, and migrations. |
| `system-design/networking/` | The transport underneath everything: TCP/TLS, HTTP semantics and versions, DNS, timeouts, retries, and latency budgets. |
| `system-design/kubernetes/` | Workload scheduling and lifecycle, networking and service discovery, configuration and secrets, autoscaling, and deployment strategy. |

#### Cloud platforms

| Path | Scope |
| --- | --- |
| `system-design/cloud/aws/` | AWS services as used in practice, along with their limits, failure modes, and cost characteristics. |
| `system-design/cloud/azure/` | The Azure equivalents, and where the mental model differs from AWS rather than merely renaming things. |

### `product-management/`

The non-code half of shipping: requirements, scope, prioritisation, stakeholder communication, and
the documentation artefacts that carry a product from idea to delivery.

### `administrative/`

Repository meta: the templates and process documents that govern how notes here are written,
rather than the subject matter itself.

| Path | Scope |
| --- | --- |
| `administrative/template/` | Reusable note templates. `tutorial-template.md` defines the house structure for long-form tutorials: Part layout, per-section rhythm, writing rules, and a pre-publish checklist. |

---

## Conventions

These keep the base searchable as it grows. They are deliberately minimal.

**Files**
- One topic per file, Markdown only, `kebab-case.md`.
- Every note opens with an `# H1` title and a one- or two-sentence summary of what question it
  answers. That summary is what makes a grep result useful.
- Prefer a short note that is correct over a long note that is aspirational.
- Long-form tutorials follow [`administrative/template/tutorial-template.md`](administrative/template/tutorial-template.md),
  which carries the section structure and a pre-publish checklist.
- Tutorial series are numbered (`001-`, `002-`, ...) and each part states what it builds on in its
  header, so the reading order is recoverable from the file names alone.

**Directories**
- `kebab-case`, singular where the folder describes a concept, plural where it holds a set of things.
- A directory earns a subdirectory only once it holds enough notes to be hard to scan.
- A topic that has both a series and runnable code splits into `tutorials/` and `hands-on/`, with
  hands-on folders numbered to match the tutorial they accompany.

**Content**
- Diagrams are inline Mermaid, each with a one- or two-sentence prose summary above it, so the note
  still reads correctly where Mermaid does not render.
- Code samples are minimal and runnable in principle; no framework scaffolding for its own sake.
- Record the *why* and the trade-off, not just the *what*. A pattern without its cost is marketing.
- Cite the source when a claim is not self-evident, and date anything version-sensitive.
- Hands-on folders never commit secrets: an `.env-sample` documents the variables, and `.env` is
  gitignored.

**Commits**
- Conventional Commits: `feat:` for a new note or exercise, `docs:` for edits to existing notes,
  `chore:` for structure and tooling, `refactor:` for reorganising existing notes.

---

## Contributing

This is a personal knowledge base rather than a community project, so there is no PR process
and no branching model. Notes are committed straight to `main` and pushed.

```bash
git add -A
git commit -m "feat: add note on <topic>"
git push
```

`main` is therefore always the working copy. Nothing here is release-gated, so the cost of a
half-finished note on `main` is lower than the friction of a branch nobody reviews.
