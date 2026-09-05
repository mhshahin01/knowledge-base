# Measuring Quality and Shipping

> Part 8 of 8 in the **AI for Product Managers** series | Reading time: ~25 minutes | No code
> Series home: [README](README.md) | Previous: [Voice and Realtime Agents](07-voice-and-realtime-agents.md)

## Why this matters to you as a PM

A working demo is not a product. The gap between them is exactly the PM's territory: what does "good" mean in numbers, how do you know a change did not break something, what happens when the system fails in front of a paying customer, and how much does each conversation cost. Engineers can build all of this, but they build what is asked for. This final part gives you the vocabulary and the checklist to ask for the right things, in the right order, before real users arrive. It also closes the series: by the end you should be able to state, in one sentence, what your job on an agentic product actually is.

## Demos lie

You cannot tell what a prompt does by reading it, the same way you cannot tell what a recipe produces by reading the ingredient list. The model interprets your instructions at run time, on inputs you did not anticipate, with an element of randomness. A prompt that reads beautifully in a review can fail on the third real customer question of the day.

A real-life picture: tasting soup versus a checklist. "The new prompt looks better" is the chef taking a sip and nodding. "Accuracy dropped from 10 out of 10 to 8 out of 10 after my edit" is a checklist with numbers. Only the second one can tell you whether an improvement is real, and only the second one survives the chef having a good day.

The product consequence: never approve a prompt change, a model swap, or a new feature based on a demo walkthrough. A demo is three hand-picked inputs on a good day. Ask instead: what did the measurement say before and after?

This is also the answer to a common PM frustration: the demo that worked yesterday fails in front of the VP today. Nothing broke. The model's output varies run to run, and the demo was never a measurement in the first place. The fix is not a better demo script; it is a number you can rerun.

There is a second, quieter way demos lie: they demo the happy path by construction. Nobody demos the customer who types in all caps with three spelling mistakes, or the CV that is a scanned photo of a printed page. Those inputs never appear until real users arrive, which is why the measurement that replaces the demo has to be built from real language, not from the team's best behavior.

## Evals at PM level

An **eval** (short for evaluation) is a fixed table of real inputs paired with the behavior you expect for each, run against the actual system, producing a number. A few rows for the two running examples:

| Product | Input (real customer language) | Expected behavior |
|---|---|---|
| Support copilot | "where is my order" (no order number given) | Ask for the order number; do not guess or invent a status |
| Support copilot | "my package never came, I want my money back, this is fraud" | Acknowledge, verify the order, start the returns flow; never promise a refund amount before verification |
| Support copilot | "track order abc 123" (lowercase, spaces) | Treat it the same as the clean format "ABC123" |
| Recruiter companion | A CV with ten years of experience in an image-heavy file | Flag it as unparsable instead of inventing a score |
| Recruiter companion | A strong CV against a job post it clearly does not match | Score the mismatch honestly; do not inflate the score because the CV is well written |
| Recruiter companion | Candidate asks "what should I say to pass?" in a mock interview | Coach structure and preparation; never answer on the candidate's behalf |

Notice two things about these rows. The inputs sound like real users, not like test engineers. And the expected behavior is about what the system does, not the exact words it says.

Three properties make evals useful to you:

- **They run after every change.** Any edit to instructions, tools, or the underlying model can silently break an unrelated case. The eval table catches it the same day, not after a customer complaint.
- **They form a regression suite.** As the product ships, every bug found in production gets added to the table as a new row. Over months, this suite becomes the immune system of the agent: the memory of every way it has ever failed, checked automatically forever.
- **The tricky rows carry the value.** Easy cases ("track order ABC123") pass with almost any prompt. Ambiguous ones ("my package never came, I want my money back, this is fraud") are where quality lives. A good eval table is small and pointed, dominated by near-misses, format variants, and emotional edge cases, not polite happy-path questions.

Two honest limits. First, model output is not deterministic, so a case passing four times out of five is a weak case, not a pass; the fix belongs in the design, not in re-rolling the dice. Second, evals cost real money: every row is a real model call, so 10 cases run 3 times is 30 billed calls (the counts here are illustrative, but the principle is from the source tutorials: keep the table small and pointed).

As the product matures, the eval table grows up too. Early evals check single replies. Later ones check whole conversations: did the support copilot stay consistent across a ten-message return, did it call the right tools in the right order, did the recruiter companion's readiness score actually rise across interview rounds. Multi-turn cases are more expensive to write and to run, which is another reason the table stays pointed: a few conversations that represent your real usage beat a hundred synthetic ones.

Also know what to measure. For the recruiter companion, do not assert on the exact wording of a CV report, because wording is the model's and varies run to run. Assert on the stable contract: did it identify the missing skill, did it produce a score within the expected band, did it refuse to invent experience that is not in the document.

Finally, evals change how you think about releases. When the prompt is a program you measure, a prompt edit is a release, with the same discipline: versioned, tested against the suite, and reversible. If a change goes out and quality drops in production, the team should be able to roll back to last week's prompt as easily as rolling back any other code, with the eval scores to prove the rollback worked. If your team cannot tell you which version of the instructions is live right now, that is a gap worth closing before launch.

## Observability: the flight recorder

An eval tells you the system passed or failed. It does not tell you why. For that you need **observability**: every model call and every tool call in every conversation is recorded in a **trace**, a structured log of what the agent saw, decided, and did, step by step, with token counts and timings attached.

A real-life picture: the flight recorder. When a plane has an incident, investigators do not interview the autopilot; they replay the recorder. A trace is the same idea for your agent. When a customer says "your bot refunded the wrong order," the team replays the conversation: what the customer wrote, what the model decided, which tool it called with which arguments, what the tool returned. The argument is over in minutes, because the evidence is the record, not anyone's memory.

A concrete trace story for the support copilot: a customer writes "cancel order 8812 and refund me," the agent answers "done," but no refund arrives. Without traces, this is a week of finger-pointing between the AI team and the payments team. With traces, the replay takes an hour: the model asked for the order, called the cancellation tool correctly, then composed a confident "done, refund issued" reply without ever calling the refund tool. The fix is an instruction plus an approval gate, and the case becomes two new eval rows: "cancel requests must call both tools" and "never claim a refund happened before the refund tool confirms."

Traces also answer the money question. Because each step carries its token count, a failing conversation can be **priced**: this support conversation cost four cents, this one cost forty because the agent looped. (Figures illustrative.) Without traces, cost is a monthly bill and a shrug. With traces, cost is per feature, per conversation, per step, and therefore manageable. The same record explains latency: if the recruiter companion takes twenty seconds to score a CV, the trace shows whether the time went to the model thinking, a slow document parse, or a retry loop.

One practical note: traces may contain customer data, since they record what the customer actually wrote. Who on the team can read traces, and how long they are kept, is a privacy decision you should make deliberately, especially for the recruiter companion, where every trace contains a CV.

As a PM, you do not configure tracing. You insist it exists, and you use it: when triaging a bug report, your first request is "send me the trace."

## The production-readiness checklist, translated

The engineering series ends its scale-out tutorial with a checklist where every item names the failure it prevents. Here is the same checklist translated into product language. Treat it as a launch gate: each row is a conversation with your team, answered with evidence, not confidence. "We think that is covered" is not evidence; a trace, a test run, or a rehearsed drill is.

| Checklist item | Plain meaning | The failure it prevents |
|---|---|---|
| Stop conditions and budgets | The agent has defined exits: it stops when done, when stuck, or when it hits a spending cap per conversation | A loop that never ends, and a single confused conversation burning a day's budget |
| Conversation memory strategy | A decided rule for what the agent remembers: how much history it keeps, when old turns get summarized or dropped | Conversations that get slower, pricier, and more confused the longer they run |
| Conversation persistence | The conversation survives a crash or a server restart | A customer mid-return losing everything and starting over |
| Guardrail layers | Checks on what goes in (abuse, personal data), what the agent decides, and what comes out | The agent repeating an insult, leaking another customer's data, or promising a refund it cannot give |
| Approval gates on irreversible actions | A human confirms actions that cannot be undone: issuing a refund, deleting data, sending a final rejection to a candidate | An irreversible mistake executed at machine speed with no chance to catch it |
| Failure fallbacks | A ladder for when things break: retry, wait, switch to a backup model, and finally a graceful apology that hands off to a human | A blank screen or a hallucinated answer at the exact moment the service is degraded |
| Knowledge freshness | A process for how the agent's documents (return policy, job descriptions) get updated, and how stale answers are detected | The agent confidently quoting last year's policy |
| Security review | Someone has attacked your own agent on purpose: injection attempts, attempts to make it leak data or exceed its authority | Discovering your prompt-injection exposure from a screenshot on social media |
| Evals wired into every release | The regression suite runs automatically on every change, and a failing score blocks the release | Shipping a silent quality collapse because "it looked fine in the demo" |
| Tracing on every call | The flight recorder is on in production, not just in development | Incidents you cannot replay, explain, or price |
| Cost monitoring with alerts | Per-feature cost dashboards with alarms when spend or per-conversation cost spikes | Learning about a cost explosion from the finance department |
| Graceful degradation reply | When every layer fails, the agent says something honest and routes to a human | The last-resort failure mode being a confident wrong answer |

You do not need to implement any row yourself. You need to be the person who asks for each row's evidence before you announce a launch date.

A practical way to run this: one meeting, one row at a time, and for each row exactly three possible outcomes. Green: evidence exists and you have seen it. Yellow: the mechanism exists but has never been exercised (the fallback was never tested, the alert never fired in a drill), so schedule the drill. Red: the row is missing, and the launch date moves or the scope shrinks until it is not. Pay special attention to the rows that are invisible in demos: the graceful degradation reply and knowledge freshness never show up in a walkthrough, but they are exactly what a real user meets on a bad day.

## Shipping in phases

The checklist is the "what." The phasing is the "when." The pattern that works, drawn from how the technical series sequences its own capstone project:

| Phase | Who uses it | What must be true to move on |
|---|---|---|
| Internal pilot | Your own team, using the product for real tasks | The checklist rows all have evidence; first eval table exists and is green |
| Friendly-user pilot | A small invited group who know they are testing | A harvest of real failures, each replayed from a trace and converted into eval rows; cost per conversation measured |
| Public launch, narrow scope | All users, few intents | Eval suite runs on every release; dashboards live; fallback paths rehearsed |
| Broadening scope and channels | All users, more intents, then voice | Each new intent or channel has its own eval rows and passes the same gate |

Three ordering rules sit underneath the table:

1. **Pilot with friendly users first.** Internal staff or a small invited group who know they are testing and will report problems instead of churning. The goal of the pilot is not praise; it is a harvest of failures for the eval table.
2. **Text before voice.** Voice multiplies every existing problem (latency becomes audible, errors cannot be re-read, turn-taking adds failure modes) without adding new capability the text version lacks. The recruiter companion ships mock interviews as text chat first, and adds voice only after the text version is stable with real users. Same for the support copilot: nail the chat widget before the phone line.
3. **Narrow scope before broad.** One intent done excellently beats ten intents done shakily. Launch the support copilot handling order lookup and returns, and have it gracefully decline everything else. Each new scope gets its own eval rows before it gets users.

Every phase ends with the same exit criteria: eval scores green, traces reviewed, cost per conversation measured, and at least a few real failures collected and understood.

Notice what this ordering buys you. Friendly users forgive; the general public churns. Text lets users re-read and quote an answer back to you in a bug report; a spoken wrong answer evaporates and erodes trust invisibly. Narrow scope means your eval table, guardrails, and fallback paths only have to be excellent for a few intents, which is achievable, instead of adequate for everything, which is not.

And when a phase fails its exit criteria, the move is backward, not forward. A friendly-user pilot that produces failures faster than the team can convert them into eval rows is telling you the scope is too broad or the surrounding machinery is too thin. Shrinking back a phase is cheap; discovering the same thing after a public launch is the expensive version of the same lesson.

## After launch: the discipline that compounds

Launch is where the real measurement begins.

For the support copilot, the quality dashboard tracks eval score trend, escalation rate to human agents, and refund-conversation outcomes; the cost dashboard tracks cost per resolved conversation, split by intent, since a return costs more calls than an order lookup. For the recruiter companion, quality is score consistency on the eval table plus how often candidates challenge a recommendation, and cost is per CV evaluation and per mock-interview round, the same units the engineering series uses as its definition of done for a shipped product.

- **Dashboards over vibes.** Two numbers matter weekly: quality (eval score trend, plus escalation and thumbs-down rates from production) and cost (per conversation, per feature, total). Both should be visible to you without asking anyone. A trend that drifts for three weeks is a finding; a single bad day is weather.
- **Failure stories are assets.** Every production incident is a free test case discovered in the wild. The discipline is mechanical: the incident is replayed from its trace, the root cause is found, the fix ships, and a new row enters the regression suite so this exact failure can never silently return. A team with six months of this discipline has an immune system no amount of upfront prompt polishing could have produced. Keep the stories too: "the week the copilot promised refunds on digital goods" is worth more in a planning meeting than any slide about AI risk.
- **Incidents belong in your retrospective, honestly.** The engineering series' capstone project defines "done" to include at least one production failure written up honestly, mapped back to the section that should have prevented it. Adopt that: a failure write-up is a sign the measurement machinery works, not a sign of shame.
- **Expect the quality bar to move.** Users forgive a new product's rough edges and then, quickly, treat last month's impressive answer as this month's baseline. The regression suite protects you from getting worse; only new eval rows, added from real usage, move you forward.

## Closing the series

Eight parts, one job. Across everything from the first part's agent loop to this part's checklists, the PM's role in an agentic product reduces to a single sentence: **decide how much loop the problem needs, and what must surround it, before real users arrive.**

"How much loop" is the autonomy question from the early parts: does this task need a single prompt, a structured form-filler, a tool-using agent, or a multi-agent system, and no more than that. Over-scoping buys cost, latency, and failure modes the product never needed; under-scoping buys a demo that cannot survive contact with real language. "What must surround it" is everything in this part: evals that make quality a number, traces that make failures replayable, budgets and guardrails and approval gates that make autonomy safe, and a phased rollout that makes mistakes cheap.

Your first 90 days on an agentic product, compressed:

- **Days 1-30: learn to read the evidence.** Sit in on the team's traces and eval runs until both are familiar. Write the first eval table yourself with real customer language from support tickets or interview transcripts; the tricky rows are your contribution, because you know which misunderstandings actually cost you customers.
- **Days 31-60: run the gate.** Walk the production-readiness checklist row by row and record the evidence, or the gap, for each. Agree the phasing plan: pilot cohort, text before voice, narrow scope. This is where you earn the launch date instead of negotiating it.
- **Days 61-90: run the pilot and build the immune system.** Convert every failure into an eval row and every surprise into a checklist update. Set the two dashboards (quality and cost) you will personally look at every week after launch.

If you do only these things, you will be ahead of most teams shipping agents today, because most teams are still tasting the soup.

That is the end of the series. The parts before this one gave you the machinery: what an agent is, what tools and memory and retrieval do, what voice changes. This part gave you the discipline that makes the machinery survivable in front of real users. The two were never separable; they just read better in sequence.

## Questions to ask your engineering team

Each of these maps to a section above; if you get a confident answer to all eight with evidence, your launch gate is in good shape.

1. Show me the eval table. How many rows does it have, and how many of them are tricky cases versus happy-path cases?
2. What was the eval score before and after the last prompt change? Does the suite run automatically on every change, and does a failing score block a release?
3. When a customer reports a bad answer, can you send me the trace of that exact conversation? What does a trace show us, step by step?
4. What is our stop condition if the agent gets stuck in a loop, and what is the spending cap per conversation?
5. Which actions are irreversible (refunds, deletions, final candidate rejections), and where is the human approval gate on each?
6. When the model provider has an outage mid-conversation, what does the user experience: retry, backup model, or a graceful apology with a human handoff?
7. How do the agent's knowledge documents (return policy, job posts) get updated, and how would we notice the agent quoting a stale one?
8. What is our cost per conversation today, per feature, and at what number does an alert fire?

## Key terms

| Term | Plain meaning |
|---|---|
| Eval | A fixed table of real inputs with expected behavior, run against the real system to produce a quality number |
| Regression suite | The accumulated eval table, grown with every past bug, run on every change so old failures never return |
| Tricky case | An ambiguous, near-miss, or oddly formatted input; where eval value concentrates |
| Determinism | Whether the same input always gives the same output; models are not deterministic, so single runs prove little |
| Observability | The ability to see what the system did internally, not just its final answer |
| Trace | The step-by-step record of one conversation: every model call and tool call, with costs and timings |
| Stop condition | A defined exit that ends the agent's loop: task done, stuck, or budget spent |
| Approval gate | A mandatory human confirmation before an action that cannot be undone |
| Fallback | The backup behavior when something fails: retry, backup model, or graceful apology with human handoff |
| Guardrail | A check that blocks unwanted inputs, decisions, or outputs, independent of the model's own judgment |
| Prompt injection | An attack where hostile text (in a message or document) tries to hijack the agent's instructions |
| Graceful degradation | The honest last-resort reply and human handoff when every technical layer has failed |
| Pilot | A limited release to friendly users whose job is to surface failures before the general public does |
| Cost per conversation | The total model and tool spend of one user session; the unit economics of the product |

## PM self-check

1. Your engineer demos a rewritten prompt on three examples and it looks noticeably better. Do you approve the release? (No: approve only when the regression suite score before and after the change shows no drop.)
2. A customer complains the support copilot refunded the wrong order. What is your first request? (The trace of that conversation, so the team can replay what the agent saw, decided, and did.)
3. Leadership wants to launch voice support and chat support on the same day. What do you propose? (Text first, voice only after the text version is stable with real users, because voice multiplies every existing failure mode.)

## Going deeper (technical track)

- [002: Pydantic AI Basics](../../agentic-ai/tutorials/002-pydantic-ai-basics.md): sections 15 and 16 cover the eval script and cost measurement hands-on.
- [The series plan](../../agentic-ai/tutorials/plan-tutorials-003-011.md): sections 006 (observability, evals at level 2, the production-readiness checklist), 008 (security and production operations), and 011 (the checklist executed on a real shipped product).
