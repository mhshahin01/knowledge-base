# Tools, Integrations, and MCP

> Part 5 of 8 in the **AI for Product Managers** series | Reading time: ~20 minutes | No code
> Series home: [README](README.md) | Previous: [Giving Agents Knowledge: RAG](04-giving-agents-knowledge-rag.md) | Next: [Trust, Safety, and Control](06-trust-safety-and-control.md)

## Why this matters to you as a PM

An agent that can only talk is a chatbot. The moment your product does something real, looks up an
order, issues a refund, creates a ticket, schedules an interview, it does so through *tools*, and every
tool is an integration someone has to build, secure, and maintain. This part covers what tools are, why
integrations multiply faster than roadmaps expect, what the new industry standard (MCP) does and
pointedly does not solve, and how to reason about build-versus-buy and vendor lock-in before the
decisions harden.

## Tools are how an agent touches your systems

A tool is a capability you hand the agent: a named action with a description and a list of typed inputs.
"Look up an order by number." "Issue a refund up to this amount." "Create a support ticket." The
support copilot for the online store needs order lookup, refund processing, and ticket creation. The
recruiter companion needs a CV reader, a calendar, and maybe an email sender.

The load-bearing fact, the one to hold onto through every vendor demo: **the model only ever requests;
your systems execute.** The agent does not reach into your order database. It produces a request that
says, in effect, "please run order lookup with order number 4821," and *your* code decides whether that
request runs, with what permissions, and what comes back. This is good news for control (part 6 is all
about what you can gate) and it defines the engineering work: every tool is a small, real piece of
software with its own authentication, failure modes, and edge cases.

**The description is what the model reads.** A tool comes with a short text description, and that text
is how the agent decides when and how to use it. It is the model's user interface. A tool described as
"handles returns" will get aimed at everything from refund requests to "where is my package," because
the model has nothing else to go on. A tool described as "issue a refund for a delivered order, maximum
50 EUR, requires the order number" gets aimed correctly. When your team says "the agent keeps calling
the wrong tool," the first suspect is not the model's intelligence; it is a vague tool description.

A real-life picture: a new hire and a set of labelled forms. The hire (the model) can only act by
filling in one of the forms you put on their desk (the tools). If a form is labelled "miscellaneous
requests," expect it to be used for everything. If it is labelled precisely, with clear fields, expect
far fewer misfires. And the hire never walks into the filing room themselves; they hand in the form and
someone else executes it.

**Product takeaway:** the quality of your agent's behavior in the real world is capped by the quality of
its tool set, and tool quality is mostly unglamorous writing and interface design. Budget for it. A
vague or bloated tool set shows up to users as an agent that "sometimes does random things."

## The integration mess, and the standard plug

Now scale up. Your store's support copilot needs the order system, the payments ledger, and the
ticketing system. Next quarter's returns agent needs the same three. The internal auditor bot needs two
of them. If every agent gets its own hand-written connection to every system, the number of integrations
is capabilities multiplied by agents: three agents times four services is twelve pieces of custom glue,
each with its own credentials, retries, and quirks, and each rewritten when either side changes.

**MCP (Model Context Protocol)** is the industry's answer: an open standard for exposing capabilities
to agents. Each capability is published once, as an *MCP server*, and each agent connects to it as an
*MCP client*, regardless of which framework or model vendor either side uses. The twelve integrations
become seven: four servers plus three client connections.

The standard analogy, which the technical series uses and which holds up well: **MCP is USB-C for agent
integrations.** One plug shape, any device. The analogy is precise in both directions. USB-C did not
make devices smarter; it made them interchangeable. And it did not remove the need to choose good
devices. MCP does the same for tools: it standardizes the connection, nothing more.

What that buys you, concretely:

- **Write once, reuse across agents and vendors.** The order-lookup capability is built a single time
  and serves the support copilot, the returns agent, and next year's whatever-agent, including agents
  built by other teams, in other languages, on other frameworks. A capability built this way also
  survives a framework migration, which matters more than it sounds (see the landscape section below).
- **Ready-made integrations exist.** There is a public registry of MCP servers (in preview since
  September 2025), so common capabilities, calendars, ticketing systems, databases, are increasingly a
  lookup and a review rather than a build. Vendors ship servers for their own products.
- **Neutral governance.** MCP was created by Anthropic in late 2024 and donated to a foundation under
  the Linux Foundation (announced December 2025, co-founded with Block and OpenAI). A protocol owned by
  one vendor is a feature; a protocol owned by a foundation is infrastructure. This materially lowers
  the "what if the owner abandons it" risk.

One more mechanic worth knowing exists, without the plumbing: when an agent connects to an MCP server,
it *asks the server what it can do* and receives the tool names, descriptions, and input shapes at
runtime. That runtime discovery is what makes it a plug standard rather than a pile of adapters.

A real-life picture: the office kitchen versus the water utility. For one desk, you buy a kettle. For a
building, you connect to the utility and pay for meters, pipes, and inspections. Neither is "better";
they are answers to "how many consumers, and whose responsibility?"

## The trust caveat: a standard plug is not a trustworthy plug

This is the section to reread before anyone installs anything from a registry.

A standard plug standardizes the connection, not the trustworthiness of what you plug in. An MCP server
is someone else's code with a line into your agent's context and, often, your users' authority. That
makes third-party integrations **supply chain**, in exactly the sense that the libraries your app
depends on are supply chain: you inherit their quality, their security posture, and their change
control.

Three specific hazards your engineers will name:

- **Tool descriptions are untrusted content.** They flow into the model's context verbatim. A malicious
  or sloppy server can hide instructions in a description ("when called, also send the conversation
  log to..."), which is a prompt-injection attack delivered through the supply chain rather than through
  a user.
- **Descriptions can change after you approved them.** Servers can update their tool lists, and clients
  pick up the changes. A tool you reviewed on Monday can carry a different description on Friday. The
  community's name for this is a *rug pull*. Approval is a property of a moment; trust is a property of
  a source.
- **Self-declared safety labels are claims, not facts.** Servers can attach hints to their tools such as
  "read-only" or "non-destructive." The standard itself says to treat these as untrusted: they are the
  vendor's sticker on their own machine. Your electrician still checks the wiring.

A real-life picture: the sticker on a borrowed machine. A contractor's equipment arrives labelled "safe,
low voltage." Useful information about the contractor's claim. Not a substitute for inspection.

The practical posture, which part 6 develops fully: consume MCP servers the way you consume software
dependencies. Review before adopting, pin versions, grant the minimum tool set each agent actually
needs (a read-mostly agent gets read-only tools), and put anything that spends money, sends messages,
or deletes data behind human approval. The standard makes installing a server dangerously convenient;
your process has to supply the friction.

## Build, buy, or adopt

Three ways to give an agent a capability, and the decision is mostly about *how many consumers* and
*who owns the system*:

| Option | What it means | Choose it when | Watch out for |
|---|---|---|---|
| **Custom tool** (hand-written, inside your agent) | Your engineers write the connection, usable only by this agent | One agent, one codebase; the capability is app-internal glue; you need tight control over exactly what comes back | Every new agent that needs it means writing it again |
| **Your own MCP server** | You publish the capability once, any agent can connect | Two or more agents, teams, or products need the same capability; you want an execution boundary with its own permissions | It is a service now: deployment, authentication, monitoring, change control |
| **Third-party MCP server** (vendor or registry) | You adopt someone else's published capability | The capability is commodity (calendars, ticketing) and a maintained server exists | Supply chain risk from the previous section; their release cycle becomes yours |

Two rules of thumb fall out of this. First, the number of consumers is the dominant factor: a second
real consumer is usually the trigger to move from custom tool to shared server. If the finance team has
asked twice for "the bot's numbers," that second consumer already exists in embryo. Second, protocol as
fashion is a real failure mode: a single internal helper does not need to be a network service with its
own authentication layer. If your team proposes a server for something only one agent will ever call,
ask who the second consumer is.

For the support copilot, the shape this usually takes: order lookup and refund processing start as
custom tools (you own them, they are core to the product, you want tight control), the calendar and
email come from vendor servers (commodity capabilities), and anything adopted from the public registry
gets the dependency-review treatment.

## The framework landscape at PM altitude

Your engineers will also choose a *framework*: the software toolkit they build the agent itself with.
You do not need to pick one, but you should be able to follow the conversation, because the choice has
hiring, cost, and lock-in consequences. As of mid-2026 the landscape sorts into three camps relevant to
most product teams:

| Camp | The question it answers | Names you will hear |
|---|---|---|
| **Vendor SDKs** | "How do we build fast on one model provider?" | OpenAI Agents SDK, Claude Agent SDK, Google ADK |
| **Orchestration frameworks** | "How do we run complex, long-running agents reliably?" | LangGraph, CrewAI, Pydantic AI, Vercel AI SDK |
| **Enterprise frameworks** | "How do we add AI to our existing Java or .NET applications?" | Microsoft Agent Framework, Spring AI |

Rough guidance: vendor SDKs are the shortest path when you have committed to one model provider;
orchestration frameworks fit complex, money-touching agents where reliability and auditability matter;
enterprise frameworks are near-zero integration cost when the company already runs on that stack.

Two durable truths matter more than any row in the table:

1. **Concepts transfer.** Every framework implements the same underlying loop (decide, act, observe,
   repeat) and the same tool contract you read about above. A team that learned one framework is most
   of the way to another. Do not let "we chose the wrong framework" become a catastrophe narrative; it
   is usually a migration, not a rewrite.
2. **The category churns fast.** In one hands-on test of nine frameworks from the technical series,
   five hit breaking changes, deprecations, or broken installs before any original code was written.
   The PM-relevant consequence: expect your team to *pin versions* (freeze exactly which release of each
   dependency the product uses) and to treat upgrades as planned work, not background noise. A vendor
   pushing "upgrade to the latest" is asking for a slice of your roadmap.

## Lock-in questions to raise early

Lock-in in this space comes in layers, and the cheapest time to see it is before signing:

- **Model lock-in:** if the agent is built on one vendor's SDK, how much of the code assumes that
  vendor's models? Frameworks in the orchestration camp typically swap models more easily.
- **Integration lock-in:** capabilities published as MCP servers survive a framework or model change;
  capabilities wired directly into one vendor's proprietary tooling do not. This is a quiet but real
  argument for the standard plug.
- **Data lock-in:** conversation history, evaluation sets, and memory stores (part 3) are assets. Ask
  where they live and in what format you could export them.
- **Service lock-in:** a third-party MCP server is a dependency on another company's release cycle,
  pricing, and continued existence. For commodity capabilities that is often fine; for a capability
  that *is* your product, it deserves the same scrutiny as any critical supplier.

None of these is a reason to avoid vendors or standards. They are reasons to know which layer you are
locked into, on purpose, and which layers you have kept portable.

## Questions to ask your engineering team

1. What is the full list of tools our agent has, and can I read the description of each one? (If a
   description would not tell *you* exactly when to use it, it will not tell the model either.)
2. Which of our capabilities are custom tools, which are our own shared servers, and which are
   third-party? What was the consumer-count reasoning for each?
3. For every third-party integration: who reviewed it, what version are we pinned to, and how would we
   notice if its tool descriptions changed underneath us?
4. Are we attaching whole tool lists from servers, or filtering down to the subset each agent actually
   needs? (Whole lists cost tokens on every call and cause wrong-tool misfires.)
5. Which tools can spend money, send messages, or delete data, and what approval gate sits in front of
   each one?
6. If we had to switch model providers or frameworks next year, which of our integrations would survive
   unchanged and which would be rewritten?
7. What happens to the user experience when a connected service is slow or down: does the agent degrade
   gracefully, or does the chat hang?

## Key terms

| Term | Plain-language meaning |
|---|---|
| **Tool** | A named capability handed to the agent (look up an order, issue a refund), with a description and typed inputs. The model requests; your systems execute. |
| **Tool description** | The short text the model reads to decide when and how to use a tool. The model's user interface; vagueness here causes misfires. |
| **Integration** | The connection between an agent and one of your (or a vendor's) systems. Each one carries authentication, failure modes, and maintenance. |
| **MCP (Model Context Protocol)** | An open standard for exposing capabilities to agents: publish once as a server, connect from any compatible agent, in any framework. The USB-C of agent integrations. |
| **MCP server / client** | The server publishes a capability; the client is the agent's connection to it. One client per server, so failures and permissions stay isolated. |
| **Registry** | A public catalog of ready-made MCP servers. Makes discovery a lookup instead of a build, but everything in it is someone else's code. |
| **Runtime discovery** | When connecting, the agent asks the server what it can do and receives the tool list live, rather than from a fixed configuration. |
| **Supply chain** | Everything your product inherits from outside code. Third-party integrations belong to it and deserve dependency-style review. |
| **Rug pull** | A server changing its tool descriptions or behavior after users approved them. The reason approval is a moment, not a permanent state. |
| **Least privilege** | Giving each agent only the tools it needs (read-only where possible), not everything a server offers. |
| **Pinning versions** | Freezing the exact release of each dependency your product uses, so upgrades are deliberate events instead of surprises. |
| **Lock-in** | The cost of leaving a vendor, framework, or service. Comes in layers (model, integration, data, service); best addressed before signing. |

## PM self-check

1. Your support copilot's agent keeps applying the refund tool to "where is my order?" questions. What
   is the first thing you ask to see? (The refund tool's description: the model can only aim with the
   text it was given.)
2. Leadership asks why the team wants to "build a server" around the order-lookup system when it
   already works inside the support agent. What is the one-sentence justification? (A second consumer,
   the returns agent, needs the same capability, so writing it once beats writing it twice.)
3. A vendor offers a ready-made integration that would save a month of work, straight from the public
   registry. What two questions precede the cost-benefit math? (Who reviewed it and what are we pinned
   to, and what happens to us if its behavior or terms change later.)

## Going deeper (technical track)

- [005: MCP](../../agentic-ai/tutorials/005-mcp.md): the full protocol tutorial: how connections,
  discovery, and transports actually work, client-side controls (filtering, approvals, timeouts), and
  the security baseline for trusting a server.
- [001: Agentic AI Basics](../../agentic-ai/tutorials/001-agentic-ai-basics.md): the agent fundamentals,
  including the framework landscape and the decision guide for choosing one.
