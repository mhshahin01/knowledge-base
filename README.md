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
| `ai/foundation/` | Core concepts: model families, tokenisation, embeddings, context windows, prompting, evaluation, and the vocabulary needed to read the rest of the field. |
| `ai/foundation/agentic-ai/` | Agentic systems: the reason/act/observe loop, agent anatomy, design patterns (ReAct, plan-and-execute, reflection, multi-agent, human-in-the-loop), failure modes, and the framework landscape. |
| `ai/foundation/llm/` | Large language models themselves: architecture, training and fine-tuning, inference behaviour, sampling parameters, context handling, and evaluation. |

### `backend/`

Language- and framework-level engineering practice: how to actually build the service once the
design is settled.

| Path | Scope |
| --- | --- |
| `backend/java/language/` | The Java language and platform itself: records, sealed types, pattern matching, virtual threads, the memory model, collections, and JVM behaviour. |
| `backend/java/spring-boot/` | Spring Boot application concerns: dependency injection, configuration, data access, transactions, validation, security, testing, and observability wiring. |
| `backend/python/` | Python for backend work: language features, typing, packaging and environments, async, and the web/service frameworks around it. |

### `system-design/`

Design-level material: the decisions made before the first line of service code is written, and the
infrastructure those decisions imply.

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

**Directories**
- `kebab-case`, singular where the folder describes a concept, plural where it holds a set of things.
- A directory earns a subdirectory only once it holds enough notes to be hard to scan.

**Content**
- Diagrams are inline Mermaid, each with a one- or two-sentence prose summary above it, so the note
  still reads correctly where Mermaid does not render.
- Code samples are minimal and runnable in principle; no framework scaffolding for its own sake.
- Record the *why* and the trade-off, not just the *what*. A pattern without its cost is marketing.
- Cite the source when a claim is not self-evident, and date anything version-sensitive.

**Commits**
- Conventional Commits: `docs:` for note content, `chore:` for structure and tooling,
  `refactor:` for reorganising existing notes.

---

## Contributing

This is a personal knowledge base rather than a community project, so there is no PR process
and no branching model. Notes are committed straight to `main` and pushed.

```bash
git add -A
git commit -m "docs: add note on <topic>"
git push
```

`main` is therefore always the working copy. Nothing here is release-gated, so the cost of a
half-finished note on `main` is lower than the friction of a branch nobody reviews.
