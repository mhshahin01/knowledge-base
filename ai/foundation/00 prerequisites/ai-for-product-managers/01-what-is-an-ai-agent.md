# What Is an AI Agent?

> Part 1 of 8 in the **AI for Product Managers** series | Reading time: ~20 minutes | No code
> Series home: [README](README.md) | Next: [Why Agents Fail, and What They Cost](02-why-agents-fail-and-what-they-cost.md)

## Why this matters to you as a PM

"Agent" is the word your vendors, your engineers, and your competitors all use right now, and they do not all mean the same thing by it. If you cannot tell a plain chatbot from a workflow from a real agent, you cannot scope a feature, challenge an estimate, or spot when a vendor has relabeled a simple product as an "agent" to justify the price. This part gives you the one distinction that matters, the machinery every agent shares, and the rule of thumb that will save you the most money: use the simplest thing that works.

## Three levels of AI in products

When someone says "we use AI," they mean one of three very different things. The distinction was popularized by Anthropic's engineering guidance and is now the standard vocabulary in the field.

| | Plain chatbot (one AI call) | Workflow | Agent |
|---|---|---|---|
| Who decides what happens next | Nobody: one question in, one answer out | The developer, who wrote a fixed path in advance | The AI model, deciding step by step at runtime |
| Tools it can use | None | Predefined, always in the same order | Chosen on the fly, as the situation demands |
| Cost per task | One model call | A fixed, predictable number of calls | One call per round, and you do not know the round count in advance |

A "model call" is simply one request to the AI model: text goes in, text comes out, you pay for what went in and what came out. Everything in this series is built on top of that single transaction.

### One task, shown at all three levels

Take a task any marketplace PM knows: **a customer writes in asking for a refund.**

**Level 1, a plain chatbot.** The customer's message goes to the model with an instruction like "classify this message: refund request, order question, or other." The model answers once: "refund request." Your system routes it to the support queue. One call, one answer, nothing decided. This is appropriate when the whole job is a single judgment or transformation, like translating a ticket or labeling its sentiment. Anything fancier buys nothing.

**Level 2, a workflow.** The path is known in advance and only the data changes. The model reads the message and extracts the order number and the reason. Fixed code, written by your engineers, looks up the order, checks your refund policy (ordered within 30 days, item not final sale), and approves or declines. The same steps run for every customer, every time. This is appropriate when you can write down the full procedure before the first request arrives, and when you need to audit exactly what happened, because a fixed path is auditable by construction.

**Level 3, an agent.** You hand the model a goal, "resolve this customer's refund request fairly," plus a menu of tools: look up an order, read the return policy, check the customer's history, issue a refund, escalate to a human. The model decides the first step. Maybe it looks up the order and finds the delivery was late, so it checks the late-delivery policy. Maybe it finds the customer has filed six refunds this quarter, so it escalates instead of approving. You cannot write that path down in advance because the next step depends on what the previous lookup returned. That is the only situation where an agent earns its cost.

A real-life picture: a chatbot is a vending machine (one button, one result). A workflow is an assembly line (fixed stations, every item takes the same route). An agent is a new employee you handed a goal and a set of keys: capable, flexible, and in need of supervision, a budget, and clear rules about which doors they may open.

The same three levels apply to the recruiter companion. Screening a CV against a job post can be one model call ("does this CV meet the stated requirements, yes or no, with reasons"). Scheduling an interview is a workflow (check calendars, propose slots, send the invite, every time the same way). Running a mock interview is the agentic case: the next question genuinely depends on the answer the candidate just gave, and no script written in advance can cover that.

### Why the levels differ in practice

The table at the top of this section compresses four business consequences. It is worth spelling them out, because they drive every scoping conversation you will have:

- **Cost predictability.** A plain call costs the same per request. A workflow costs the same per run. An agent's cost varies per task, because the model decides how many rounds it needs. Your finance forecast needs ranges, not point estimates.
- **Latency.** A user waiting on a chatbot waits for one call. A user waiting on an agent waits for a chain of calls and tool executions. Ten rounds of a slow model feels very different from one round of a fast one.
- **Auditability.** With a workflow you can show an auditor the exact path every case will take, before any case arrives. With an agent you can only show them the rules and then the log of what actually happened. In regulated spaces this difference can decide the design on its own.
- **Failure shape.** A workflow fails in ways you enumerated in advance and tested. An agent fails in ways that emerge at runtime, which is why the next section's exits and the later patterns matter so much.

None of this makes agents bad. It makes them a deliberate trade: you accept variable cost, variable latency, and runtime unpredictability in exchange for handling cases whose paths you could never have enumerated.

## The agent loop, in plain words

Strip away every framework and every vendor pitch, and an agent is a loop. You give the model a goal and a menu of tools. Each round, the model reads everything that has happened so far and makes exactly one decision: either "here is the final answer" or "run this tool with these inputs." Ordinary code (not the model) runs the tool, the result is added to the record, and the model is asked again. Repeat until done.

**A real-life picture: the detective and the case file.** A detective works a case in rounds. Every morning she reads the entire case file from page one, keeping nothing in her head, then decides the single next move: interview a witness, request a phone record, or close the case. The interview transcript gets stapled into the file, and tomorrow she reads the bigger file again. Three details in that picture are the whole mechanism:

- **The case file is everything.** The detective's memory is the file, not her head. In an agent, that file is called the context: the goal, the tool menu, and every result so far, re-read in full every round.
- **The detective never does the lab work herself.** She requests it; someone else runs it and hands back a report. Likewise, the model never executes anything. It only decides and requests. Your code executes. This boundary is where your security rules and approval gates live.
- **The case ends in one of three ways.** She solves it, the budget runs out, or she is pulled off the case. Agents need the same three exits: a final answer, a spending or time cap, and a clean give-up path. An agent shipped without the second and third exit will one day loop until the bill arrives.

One consequence to internalize as a PM: every round of the loop is a paid model call, and later rounds cost more than early ones because the case file keeps growing. A task that takes twelve rounds is twelve calls, each bigger than the last. Part 2 of this series goes deep on what that does to reliability and cost; for now, hold onto "step count is the enemy."

### Watching one case run

Here is the support copilot working a refund request, round by round. The customer wrote: "My headphones arrived broken and I want my money back."

| Round | The model reads | The model decides | The code does |
|---|---|---|---|
| 1 | Goal, tool menu, the customer's message | "Look up the order behind this message" | Runs the order lookup, appends the result: order found, delivered last week |
| 2 | Everything from round 1, plus the order record | "Check the return policy for damaged electronics" | Runs the policy search, appends it: damaged items refundable within 30 days |
| 3 | All of the above, plus the policy text | "This qualifies. Draft the refund and ask a human to approve it" | Creates the refund draft, routes it to the approval queue, appends the confirmation |
| 4 | The full case file | "Final answer: tell the customer the refund is approved and on its way" | The loop exits |

Four model calls, three tool uses, one human gate. Notice two things. First, nobody wrote this path down: a different customer with a different order history would have produced a different route, and that is precisely the point. Second, round 4 re-read everything from rounds 1 through 3, so it was the most expensive call of the four. The cheapest possible agent run is one where the model needs no tools at all and answers on round 1.

## The four building blocks every agent has

Building an agent is like staffing a small office. You need someone who thinks, equipment they can use, somewhere to keep notes, and an office manager who keeps the operation on track.

**1. The model (the brain).** The only part that thinks. It reads the case file and decides the next step. Two practical facts: not every model can play this role (the ability to request tools in a precise, structured format is a trained skill, and your engineers should verify a candidate model has it), and bigger is not always better. A mid-tier model that follows instructions well often beats a flagship on cost and speed for routine agent work, because you pay for a call every round.

**2. Tools (the hands).** Anything the agent can invoke: order lookup, policy search, refund issuance, calendar access. Each tool comes with a description the model reads to know when and how to use it, and that description matters more than most teams expect: five sharply described tools outperform fifty vague ones. Tools are also your security perimeter. The model can be manipulated by hostile content it reads, so each tool should carry the least power needed: a read-only order lookup, a "draft the email" tool rather than a "send without asking" tool.

**3. Memory (the desk and the filing cabinet).** Short-term memory is the desk: the case file itself, everything visible to the model right now. It is fast but has a fixed size, and long tasks fill it until the original goal scrolls out of view. Long-term memory is the filing cabinet: databases and document stores the agent can search through a tool, which survive across sessions. An agent that "remembers your customers" is really an agent with a well-organized filing cabinet, not a model with a better brain.

**4. Orchestration (the office manager).** Plain software, no AI in it, that runs the loop: passing the case file to the model, validating its requests, executing tools, enforcing budgets, catching errors, and deciding when to stop. This is the least glamorous block and the one that decides whether your agent survives contact with real users. It is also where the "never issue a refund above a set amount without human approval" rules get enforced, in code the model cannot talk its way around.

| Block | Office analogy | What it really is | Classic mistake |
|---|---|---|---|
| Model | The thinker | An AI model that only ever decides | Expecting it to execute actions or remember past rounds on its own |
| Tools | The equipment | Your functions plus descriptions the model reads | Vague descriptions; too much power per tool |
| Memory | Desk and filing cabinet | The growing case file plus external stores | Stuffing everything into the case file |
| Orchestration | The office manager | Ordinary code: loop, budgets, errors, guardrails | Skipping budgets and exits because "the demo worked" |

Mapped onto the recruiter companion, the office looks like this. The model reads each CV and the job post and decides what to do next. Its tools are: fetch a CV, search past interview notes, compare against the stated requirements, draft feedback for the hiring manager. Its desk holds the current candidate's file; its filing cabinet holds every past evaluation it can search. Its office manager enforces the rules that matter in hiring: no rejection email ever sends without a human reading it first, and every run stops at a fixed budget whether or not it finished.

A scoping question worth asking early: which of the four blocks is the team's effort going into? In healthy projects the honest answer is orchestration and tool descriptions, because the model is rented and the memory is standard plumbing. If most of the effort is going anywhere else, ask why.

## The five working patterns

These are reusable answers to recurring problems, not competing products. Real systems combine them. You will recognize them in tools you already use.

**Thinking out loud (known as ReAct, short for reason and act).** Before each action, the model is asked to write down its reasoning, then act, then read the result. Two benefits: committing to a plan before acting reduces impulsive mistakes (the same reason you think more clearly when you explain yourself to a colleague), and the written reasoning makes the agent's behavior readable when something goes wrong. This is the default in most agent systems.

**Plan-then-execute.** For long tasks, a strong model first writes the whole route ("find the policy, check the order history, decide, draft the reply"), then cheaper steps carry it out, and the plan gets revised when reality deviates. Like driving cross-country with a route planned in advance instead of choosing each turn at each intersection. Worth it for tasks with many steps whose overall shape is knowable up front; risky when the initial plan is bad and the system executes it confidently in the wrong direction.

**Self-review (reflection).** After producing an output, the agent grades its own work and retries. It works best when there is a real, objective checker involved: "does the refund amount match the policy table" can be verified; "is this reply well written" is the model grading its own homework. Cap the retries, because each review round is more paid model calls.

**Teams of specialists (multi-agent).** Instead of one agent with one giant case file, a lead agent delegates to specialists: a researcher, a writer, a critic. Each specialist keeps a focused case file and a sharp job description. The honest costs: agents communicate through paid model calls, so the chatter between them burns budget fast, and errors compound across the team (a confused researcher hands bad facts to a diligent writer, who polishes them into a confident, wrong answer). Start with one agent; promote to a team only when a single agent's focus becomes the bottleneck.

**Human approval before risky steps (human-in-the-loop).** The agent runs freely until it reaches a high-stakes step, then pauses for a human decision. The design rule is reversibility: reading a web page or drafting a reply is reversible, so let it flow; issuing a refund, deleting data, or emailing five thousand customers is not, so gate it behind a person. Good systems make approval a property of the tool, not a hope about the model's judgment. In production this pattern is close to non-negotiable.

You can see all five in tools your engineers may already use. Popular coding assistants think out loud as their core loop, plan big changes before editing, re-run tests and fix their own failures (self-review with an objective checker), spawn specialist sub-agents for wide searches, and pause for permission before unfamiliar or destructive commands.

The same five patterns, mapped to the two running examples:

| Pattern | Support copilot | Recruiter companion |
|---|---|---|
| Thinking out loud | Writes "I need the order date before I can judge the policy" before each lookup | Writes "the candidate's answer was vague on leadership, I should probe" before each question |
| Plan-then-execute | Plans the refund investigation up front, then works through it | Plans the mock interview arc (background, technical depth, scenario) before starting |
| Self-review | Re-checks the drafted reply against the policy text before sending | Re-checks the CV evaluation against every stated requirement before reporting |
| Teams of specialists | A triage agent hands billing cases to a billing specialist | A screening agent hands finalists to an interview agent with a fresh case file |
| Human approval | Refunds above a threshold pause for a person | Rejection and offer communications pause for a person |

## The golden rule: use the simplest thing that works

Here is the sentence worth quoting in your next planning meeting: **most production systems are workflows with a few agentic steps, not fully autonomous agents.**

Full autonomy is expensive, slow, and hard to make reliable. Each additional step an agent takes is another chance to err, and the chances multiply: if each step is right 95 percent of the time, a twenty-step task fully succeeds only about 36 percent of the time. So the craft of agent engineering is mostly about constraining autonomy: fixed paths wherever the path is knowable, agentic judgment only at the steps that genuinely need it, budgets and approval gates around everything.

This also arms you against **agent-washing**: the relabeling of ordinary products as "agents" because the word sells. A chatbot with a FAQ behind it is not an agent. A fixed pipeline with an AI classification step is a workflow, which may be exactly the right product, but it should be priced, scoped, and marketed as one. When a vendor or a team says "agent," ask the question from the level test: does the model decide the next step at runtime, or did a developer write the path in advance? Honest teams welcome the question; the answer changes the estimate, the risk profile, and the evaluation plan.

## When is an agent actually justified?

One criterion, worth memorizing: **an agent is justified only when the next step genuinely depends on results you cannot foresee.**

- "Research this company and write a report." You cannot know in advance how many searches are needed, which sources matter, or when there is enough material. Justified.
- A support copilot that diagnoses a failed integration. Each diagnostic check determines which check makes sense next; the decision tree is too large and too fluid to hardcode. Justified.
- A mock interview where the follow-up question depends on the candidate's last answer. Justified.
- Extracting the total from an invoice and validating it. The path is identical every time. Not justified; that is a workflow, and building it as an agent adds cost and failure modes for zero benefit.
- Classifying a support ticket. One judgment. Not justified; that is a plain model call.

The deciding factors, in order: how many paths exist (one or a few means a call or a workflow; unbounded means an agent), how much predictability you need (high predictability argues against an agent), your cost and latency budget (every round is a paid call), and how much auditability you need (workflow steps are inspectable in advance; agent steps emerge at runtime).

## Questions to ask your engineering team

1. For this feature, which level are we building: a single model call, a workflow, or an agent? Which specific steps are agentic and why?
2. What are the three exits for this agent: how does it finish, what caps its spending and time, and how does it give up cleanly?
3. How many model calls does a typical task take, and what does that cost per user action at our expected volume?
4. Which tools does the agent have, what power does each one carry, and which tools require human approval before they run?
5. Show me the written reasoning trace for a task that went wrong. Where did it go off the rails?
6. What objective checker exists for self-review, or is the model grading its own homework?
7. Are we buying or building anything labeled "agent" that is actually a fixed workflow? Is it priced accordingly?
8. What stops this agent from being manipulated by hostile content in the messages or documents it reads?

## Key terms

| Term | Plain-language meaning |
|---|---|
| Model call | One request to the AI model: text in, text out, billed on both directions |
| Plain chatbot / single call | One question, one answer, no tools, no loop |
| Workflow | A fixed sequence of steps written by a developer; only the data changes between runs |
| Agent | A system where the model decides each next step itself, in a loop, until the goal is met or an exit trips |
| Agent loop | The repeating cycle: the model reads the case file, decides one step, code executes it, the result is appended, repeat |
| Context (case file) | The complete bundle of text the model sees each round; its entire memory of the task |
| Tool | A capability the agent can request, with a description the model reads to decide when to use it |
| Orchestration | The ordinary code that runs the loop, enforces budgets, handles errors, and gates risky actions |
| Thinking out loud (ReAct) | The model writes its reasoning before each action, which improves decisions and makes failures readable |
| Plan-then-execute | A strong model writes the full plan up front; cheaper steps execute it; the plan is revised when reality deviates |
| Self-review (reflection) | The agent critiques and retries its own output, ideally against an objective check |
| Multi-agent | A lead agent delegating to specialized agents, each with its own focused case file |
| Human-in-the-loop | The agent pauses for a person's approval at irreversible or expensive steps |
| Agent-washing | Relabeling a chatbot or fixed workflow as an "agent" to ride the trend |
| Error compounding | Step reliabilities multiply, so long chains of steps fail often even when each step is usually right |

## PM self-check

- Your team proposes an "agent" that always runs the same five steps on every support ticket. Is it an agent? (No: the path is fixed, so it is a workflow; that may be the right design, but scope and price it as one.)
- A mock-interview feature must decide its next question based on the candidate's previous answer. Call, workflow, or agent? (Agent: the next step genuinely depends on unforeseeable results.)
- Your refund agent sometimes loops for forty rounds and racks up a large bill. Which building block is missing or weak? (Orchestration: the budget cap and give-up exit were never enforced.)

## Going deeper (technical track)

- [001: Agentic AI Basics](../../agentic-ai/tutorials/001-agentic-ai-basics.md)
