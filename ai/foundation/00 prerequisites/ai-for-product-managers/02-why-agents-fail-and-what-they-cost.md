# Why Agents Fail, and What They Cost

> Part 2 of 8 in the **AI for Product Managers** series | Reading time: ~25 minutes | No code
> Series home: [README](README.md) | Previous: [What Is an AI Agent?](01-what-is-an-ai-agent.md) | Next: [Memory and Conversations](03-memory-and-conversations.md)

## Why this matters to you as a PM

Demo agents look magical and production agents disappoint, and the gap between the two is not bad luck or a weak team. It is arithmetic. Agents fail in statistically predictable ways, and they cost money in equally predictable ways, and both follow from one mechanical fact: an agent works in loops, and every loop round re-reads everything it has seen so far. If you can do this arithmetic on the back of an envelope, you will scope features your team can actually ship, catch unrealistic reliability promises before your users do, and read a cloud bill without being surprised. This part gives you the three numbers behind almost every agent postmortem: step reliability, context size, and token cost.

## Failure mode one: errors compound

Part 1 described the agent loop: reason, act, observe, repeat. Each round of that loop is a small act of judgment, and each judgment has some chance of being wrong. The model might misread the customer's question, pick the wrong tool, or misinterpret what the tool returned. Modern models are good, so any single step might be right 95% of the time. The trouble is what happens when steps multiply.

If every step is 95% reliable, the probability that a whole task succeeds is 0.95 multiplied by itself once per step:

| Steps in the task | Chance the whole task succeeds (at 95% per step) |
|---|---|
| 1 | 95% |
| 5 | about 77% |
| 10 | about 60% |
| 20 | about 36% |
| 50 | about 8% |

Read the 20-step row again. A task with twenty dependent steps, each one individually excellent, fails almost two times out of three. This is not a defect in any particular model or framework; it is multiplication. The engineer's phrase for it is: **step count is the enemy of reliability.**

A real-life picture: a bucket brigade. Twenty people pass buckets hand to hand, and each person catches and passes cleanly 95% of the time. You do not get a brigade that is 95% effective. You get spilled water on most runs, because one fumble anywhere breaks the chain. Nobody in the line is incompetent; the line is just long.

This has direct product consequences:

- **Scope features by step count, not by ambition.** "Answer a shipping question" (look up one order, compose one reply) is a 2-3 step task and can be very reliable. "Handle any customer issue end to end" is a 20+ step task and cannot be, at current model quality. The support copilot that answers questions and looks up orders is shippable. The support copilot that autonomously negotiates complex disputes is a reliability lawsuit.
- **Prefer fewer autonomous steps over more cleverness.** When your engineers propose splitting a task into a fixed pipeline with one or two judgment calls instead of a free-running agent, they are not being timid. They are buying reliability with structure. The engineering sources for this series put it plainly: the craft of agent engineering is mostly about constraining autonomy so the agent stays reliable.
- **Escalation is a feature, not a failure.** If the copilot resolves 70% of tickets and cleanly hands the rest to a human with full context, that is a good product. A copilot that attempts 100% and botches 30% is a bad one. Design the handoff, measure it, and market it honestly.

When a vendor demos an agent that "handled a complex workflow flawlessly," your first question should be: how many steps was that, and what happens on run number two hundred?

The recruiter companion makes the same point from the other side. Scoring one CV against one job post is a short chain: parse, compare, judge, report. A "run the whole hiring funnel" agent, screen fifty CVs, email candidates, schedule interviews, collect feedback, update the tracker, is a long chain where each candidate multiplies the step count again. Ship the short chain first. The long chain is a roadmap item, and it may never belong in one autonomous loop at all.

## Failure mode two: the desk has a fixed size

Part 1 introduced the idea that the model has no memory of its own. Between calls it forgets everything, so the agent re-reads its entire case file on every round of the loop. That case file, the standing instructions, the tool menu, the conversation so far, every tool result, and the model's own earlier notes, is called the **context**.

The **context window** is the maximum size of that file, measured in tokens (the next section explains tokens). It is a hard physical limit of the model, not a setting you can raise by paying more. Exceed it and the request fails, or, in some products, the oldest content is silently dropped, which is worse, because the agent keeps working while having quietly forgotten the beginning.

Two properties of the window matter for product decisions:

- **Input and output share the same window.** If the window holds 200,000 tokens and the case file already fills 190,000, only 10,000 remain for the model's answer. A nearly full window does not just risk failure; it strangles the reply. This is why an overloaded agent sometimes answers in a truncated sentence or two and stops.
- **Agents fill the window by design.** A chatbot user hits the limit only after a very long conversation. An agent appends a tool result on every loop round, so it burns through its allowance far faster, on every long task. The desk fills up exactly when the work gets ambitious.

A real-life picture: a detective with a small desk. Every morning the detective lays out the whole case file on the desk, works, adds new notes, and lays everything out again the next morning. The desk does not grow. At some point the new evidence physically pushes the original assignment off the edge, and from then on the detective works diligently on a case whose goal is no longer in sight. That is what "the agent lost track of the goal" means mechanically: the goal scrolled out of the window.

There is one more honest caveat. Even before the window is full, models recall and reason worse about content buried in the middle of a very long context, a known weakness sometimes called the "lost in the middle" effect. The advertised window size is what survives the vendor's benchmarks; the *effective* window your agent experiences is smaller. Treat big window numbers as a ceiling, not a working area.

Engineering countermeasures exist (summarizing the old parts of the file, storing durable facts outside the context, delegating subtasks to sub-agents with fresh desks), and Part 3 covers the conversation side of this. Your job as PM is simpler: know that "give the agent more to read" is never free, and that "just use the model with the huge window" trades one problem for two others, cost and degraded recall.

## Tokens: the unit everything is billed in

Models do not read characters or words. They read **tokens**: chunks of text drawn from a fixed vocabulary. For English, the rough conversion is:

- 1 token is about 4 characters, or about three quarters of a word
- 100 tokens is about 75 words, a solid paragraph
- A page of text is roughly 500-700 tokens; a two-page CV is roughly 1,200-2,000 tokens

Two warnings worth remembering. First, not all text tokenizes equally: numbers, structured data, and non-English languages cost more tokens per character than plain English prose. Second, each model family has its own tokenizer, so exact counts differ slightly between providers. For forecasting, the rough conversions above are enough.

**Reading is cheaper than writing.** Every call to the model is billed in two directions at different prices. Input tokens are everything you send: instructions, tool menu, history, tool results. Output tokens are everything the model generates: the reply, the tool calls, and for reasoning models, hidden deliberation tokens you never see but still pay for. Output typically costs 3 to 6 times more per token than input, because reading can be done in parallel while writing happens one token at a time. Practical consequence: a short, precise answer is not just better UX, it is cheaper UX. Long-winded agents are a cost problem, not a style problem.

**Every loop round re-reads the whole file.** This is the arithmetic that surprises everyone. The agent does not pay for three calls' worth of new material on a three-round task; it pays for the entire growing context three times. An illustrative example from the engineering track: a 3-round task whose context starts at 3,000 tokens and grows with tool results bills about 9,950 input tokens to produce a 600-token answer. The rule of thumb: **agent cost grows with rounds times average context size.** Both halves of the reliability-and-cost problem live in that one formula.

**Conversations pay a replay tax.** The same law applies across turns of a chat: turn N re-sends turns 1 through N-1, plus the standing instructions and tool menu, every single time. Small worked example (all numbers illustrative): a support chat with 1,500 tokens of fixed overhead (instructions plus tool menu) where each turn adds about 400 tokens of conversation:

| Turn | Input sent that turn (tokens) | Running total billed |
|---|---|---|
| 1 | 1,900 | 1,900 |
| 2 | 2,300 | 4,200 |
| 3 | 2,700 | 6,900 |
| 4 | 3,100 | 10,000 |
| 5 | 3,500 | 13,500 |
| 6 | 3,900 | 17,400 |

The actual content of that six-turn conversation is about 2,400 tokens. You paid for 17,400. And the penalty grows faster than the conversation: doubling the number of turns more than doubles the bill, because every new turn re-pays for all the old ones. This is why "add a chat feature" has a cost curve that looks nothing like the demo's two polite exchanges. A 30-turn power user is a different product, financially, than a 3-turn casual one.

## Worked forecast: the support copilot's unit economics

Here is the full method applied to the series' running example. Every number below is illustrative; the point is the shape of the calculation, which you should be able to redo with your own vendor's price sheet.

**The product:** the support copilot for an online store. A customer opens a chat with a problem. The copilot reads the question, looks up the order, checks the return policy, possibly processes a return, and replies. Assume a typical ticket takes 5 loop rounds, on a mid-tier model priced at $1.25 per million input tokens and $10 per million output tokens (illustrative prices in the range of real mid-tier models; always check the current sheet).

**Step 1: tokens per ticket (illustrative).**

| Component | Tokens |
|---|---|
| Round 1 input: instructions + tool menu (2,000) + customer question (500) | 2,500 |
| Round 2 input: everything re-sent + order lookup result (900) | 3,400 |
| Round 3 input: re-sent again + policy lookup (900) | 4,300 |
| Round 4 input: re-sent again + return processing result (900) | 5,200 |
| Round 5 input: re-sent again + confirmation (900) | 6,100 |
| Outputs: four short tool calls + the final customer reply | 1,000 |
| **Billed per ticket** | **21,500 in / 1,000 out** |

Notice the same trick as before: the unique content is about 6,100 tokens, but 21,500 input tokens get billed, because each round re-sends everything the rounds before it saw.

**Step 2: cost per ticket (illustrative).**

- Input: 21,500 tokens at $1.25 per million comes to about $0.027
- Output: 1,000 tokens at $10 per million comes to about $0.010
- Total: about $0.037, call it 4 cents per attempted ticket

**Step 3: honesty adjustments (illustrative).** Real traffic adds three things: retries and failed loops, customers who paste their entire order history into the chat box, and tickets the agent cannot resolve but still spends tokens attempting. Add a 30% buffer for the first two, and assume 70% of tickets resolve without a human (an ambitious but plausible target for a well-scoped copilot). Cost per *resolved* ticket is then roughly 4 cents times 1.3, divided by 0.7: about 7 cents.

**Step 4: the forecast (illustrative).**

| Volume | Attempted tickets per month | Model cost per month | Cost per resolved ticket |
|---|---|---|---|
| 1,000 tickets/day | 30,000 | about $1,600 | about $0.075 |
| 10,000 tickets/day | 300,000 | about $16,000 | about $0.075 |

Two things to take from this table. First, the model bill itself is rarely the scary number at moderate scale; $1,600 a month to deflect most of 21,000 tickets is usually a bargain against human support time. Second, the number scales linearly with volume and with the size of each ticket's context, so the levers in the next section are where the margin lives. And remember the chat effect: if each resolved ticket then continues into a 6-turn follow-up conversation, the replay tax from the previous section stacks on top of these numbers.

## The cost levers you should know exist

You do not need to implement any of these. You need to know they exist, so that when a forecast looks too big you can ask "which levers have we pulled?" instead of "can we afford AI?"

- **Fewer steps.** The master lever. It cuts cost and raises reliability at the same time, because both scale with loop rounds. Ask whether a task really needs five autonomous rounds or whether two judgment calls inside a fixed pipeline would do.
- **Shorter instructions and a smaller tool menu.** The standing instructions and tool descriptions ride along on every single call. Bloated instructions are a per-call tax you pay forever.
- **A cheaper model for the easy steps.** Reading an order record and reformatting it does not need the flagship model; judgment about refunds does. A realistic mixed setup, cheap model for mechanical steps and strong model for judgment, often lands 3 to 10 times cheaper than running everything on the flagship. For the recruiter companion, parsing a CV is the cheap step; evaluating it against the job post is the expensive one.
- **Caching repeated content.** Providers bill re-sent, unchanged input at a steep discount, often around 90% off the input price, when the beginning of the request is identical to a recent one. Your standing instructions and tool menu are exactly that kind of content. This is close to free money for loop-heavy agents, but it only works if the stable content sits at the front; one changing detail placed early quietly disables the discount.
- **Trimming conversations and tool outputs.** A tool that returns 200 rows "for completeness" bills you for 200 rows on every later round and every later turn of that conversation. Capping tool results at the source and compressing or windowing long chat histories are standard practice; Part 3 goes deeper on the conversation side.
- **Hard budgets.** Engineers can set literal caps: maximum model calls per task, maximum tokens per run, maximum spend per conversation. When a cap is hit, the agent stops with a clean message instead of looping until the bill arrives. This is the cheapest insurance in the whole stack. If your agent has no budget cap, you do not have a cost forecast; you have a hope.

One caution about the popular intuition "costs will just keep falling." Model prices per token do tend to fall over time, but agent usage tends to grow faster: more features, longer conversations, more users, richer tool results. Treat falling unit prices as headroom for doing more, not as a reason to skip the levers above.

## Latency is a product property

Every loop round is a model call, and model calls take time: reading the full context, then generating the output one token at a time. A single chatbot reply might take a second or two. A five-round support ticket takes five sequential calls, each slower than a plain reply because each reads more than the last. Users experience this as a long, silent wait, and silent waits read as broken software.

The product implications:

- **Perceived latency is designable.** Streaming the reply as it is generated, showing honest progress states ("looking up your order..."), and answering the easy part first all change how the wait feels without changing the underlying speed. A spinner that says nothing for twelve seconds is a design failure; the same twelve seconds with visible progress is acceptable.
- **Step count hits you twice.** The same loop rounds that multiply cost also multiply waiting. The "fewer steps" lever is a latency lever too.
- **Set expectations per feature.** Instant answers for FAQ-style questions (often one round, sometimes cacheable), a few seconds for order lookups, a progress bar for anything that processes a return. If your UX assumes every agent interaction is as fast as a search box, users will abandon it before the demo ends.

A real-life picture: a good waiter versus a silent kitchen. The food may take the same fifteen minutes either way, but the waiter who says "your order is in, the grill is backed up, about ten minutes" keeps the table. The silent kitchen loses it. Progress states are your waiter.

When reviewing a prototype, do not just ask "does it work?" Ask "how long does the slowest common case take, and what does the user see while it happens?"

## Questions to ask your engineering team

1. How many loop rounds does a typical task take, and what is our measured end-to-end success rate at that step count, not the per-step rate?
2. What is our per-task token budget, broken into input and output, and where did the estimates come from?
3. Which model handles which step, and what did the cheap-model-for-easy-steps analysis show?
4. Is prompt caching active, and have we verified the actual cache hit rate on the bill rather than assuming it?
5. What are the hard caps on model calls, tokens, and spend per task and per conversation, and what does the user see when a cap triggers?
6. How do we handle conversations that grow long: truncation, a sliding window, or summarization, and what does the user lose in each case?
7. What is the p95 latency of a resolved ticket, and what does the user see on screen during the wait?
8. When the agent cannot complete a task, what does the handoff to a human look like, and does the human get the full context?

## Key terms

| Term | Plain meaning |
|---|---|
| Error compounding | Each step's small chance of failure multiplies across steps, so long tasks fail often even when every step is good |
| Context | The complete bundle of text the model re-reads on every call: instructions, tool menu, history, tool results, its own earlier output |
| Context window | The hard maximum size of that bundle, shared between what you send and what the model replies |
| Token | The chunk of text models actually read and bill for; about 4 characters or three quarters of an English word |
| Input tokens | Everything sent to the model on a call; the cheaper direction |
| Output tokens | Everything the model generates; typically 3-6 times the input price, and includes hidden reasoning on some models |
| Replay tax | The cost of re-sending the entire conversation history on every new turn; grows faster than the conversation itself |
| Prompt caching | A provider discount (often around 90% off input price) for re-sent, unchanged content at the start of the request |
| Lost in the middle | The tendency of models to recall content buried in the middle of a long context worse than content at the start or end |
| Usage limits | Hard caps on calls, tokens, or spend that stop a runaway agent with a clean message instead of a giant bill |

## PM self-check

1. A vendor demos an agent completing a 25-step workflow and claims 95% reliability "because the model is 95% accurate." What is the likely real end-to-end success rate? (Roughly 28%, since 0.95 multiplied by itself 25 times gives about 0.28; per-step accuracy is not task reliability.)
2. Your support copilot's chat gets a new feature: customers can now ask unlimited follow-up questions after their ticket is resolved. What happens to the cost per conversation as chats get longer? (It grows faster than the conversation length, because every new turn re-sends the whole history: the replay tax.)
3. Engineering proposes cutting the agent's tool menu from 30 tools to 8 and shortening its instructions by half. Which two things improve? (Cost on every call, since instructions and the tool menu are re-sent each round, and reliability, since fewer tools means fewer wrong choices per step.)

## Going deeper (technical track)

- [001: Agentic AI Basics](../../agentic-ai/tutorials/001-agentic-ai-basics.md): sections 6-8 cover why agents are hard, the context window, and token cost estimation with a fully worked forecast.
- [003: Agentic AI Level 2](../../agentic-ai/tutorials/003-agentic-ai-level-2.md): sections 3, 6, and 7 cover the replay tax in detail, prompt caching, and context budgeting in practice.
