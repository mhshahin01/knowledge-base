# Memory and Conversations

> Part 3 of 8 in the **AI for Product Managers** series | Reading time: ~20 minutes | No code
> Series home: [README](README.md) | Previous: [Why Agents Fail, and What They Cost](02-why-agents-fail-and-what-they-cost.md) | Next: [Giving Agents Knowledge: RAG](04-giving-agents-knowledge-rag.md)

## Why this matters to you as a PM

"The assistant remembers me" is the single most oversold sentence in AI product marketing, and it will end up in your copy, your support docs, and your users' heads whether you put it there or not. What actually ships is plumbing: your team re-sends old text to a model that forgets everything the moment a call ends. That plumbing decides three things you own: how the product feels at conversation 50 versus conversation 1, what a power user costs compared to the demo, and whether a deletion request from a regulator or an angry customer is a routine operation or a project. You do not need to build any of it. You need to know what is real, so you can scope it, price it, and stop your marketing from promising a mind that does not exist.

## The model remembers nothing

Start with the uncomfortable fact, because everything else in this part follows from it: the model itself has no memory. None. Every time your product sends a message, the model reads what it is given, produces an answer, and forgets the exchange ever happened. The next message arrives at a blank mind.

So why does the chat assistant in the demo clearly remember that you mentioned your order number three messages ago? Because your product quietly re-sent those three messages along with the new one. The model did not remember anything; it re-read the transcript. Every "memory" feature you have ever used in a chat AI works this way. Memory is not a property of the model. It is text your product supplies again and again.

A real-life picture: the relief receptionist. Picture a front desk staffed by a different receptionist every hour, each one starting their shift knowing absolutely nothing about the day so far. This works fine, as long as there is a logbook on the desk. The new receptionist reads the logbook before picking up the phone, so to the caller the desk seems to have a continuous memory. The logbook is doing all the work; the receptionist is interchangeable. Your product is the clerk who slides the logbook across the desk before the model's phone rings. No logbook, no memory.

One subtlety worth knowing, because it produces the sneakiest bug in this whole area: the logbook can be passed in full or in part. If your product hands over only the most recent exchange instead of the whole logbook, the assistant works for a turn or two, the demo looks fine, and then it starts forgetting everything older than the previous message. Users experience this as an assistant that is fine at the start of a chat and gets strangely dense as the chat goes on. If you ever see that complaint pattern, this paragraph is the first thing to ask your team about.

This has two immediate product consequences.

First, continuing a conversation is a feature your team builds, not a default. An assistant wired without the logbook step is an amnesiac: it answers each message as if it were the first. Users say things like "and what about the other one?" and "any updates on my return?". If nothing re-supplies the earlier turns, those messages are unanswerable. For the support copilot, this is the difference between "Yes, your return for order 4417 was approved Tuesday" and "Could you tell me which order you mean?".

Second, the transcript is the product's most important file. Because the model remembers nothing, the stored conversation is the only place the conversation exists. It is the debug log when a user complains the assistant "said something weird" (you read the row), the fix when a bad answer poisons a chat (you edit the row), and the thing that must survive your app restarting, deploying, or crashing mid-conversation. If the transcript lives only in a running process's memory, the conversation dies with the process, and "continue where we left off" is impossible.

## Conversation memory: the whole chat is re-read every turn

Here is the mechanism to internalize, because it explains both your cloud bill and a quality problem your users will report: on every single turn, the product sends the entire conversation so far, plus the new message. Turn 10 does not send message 10. It sends messages 1 through 9 again, then message 10. Turn 50 sends 1 through 49 again.

Part 2 called this re-sending pattern the loop's arithmetic; in a conversation it becomes what the technical series calls the replay tax, and it is quadratic: the bill grows faster than the chat does. The source tutorial's worked example makes it concrete. Take a chat where the fixed overhead per call (the assistant's standing instructions and tool descriptions) is 800 tokens, and each exchange adds about 300 tokens of conversation:

| Turn | Input tokens sent that turn | What is in it |
|---|---|---|
| 1 | 1,100 | Overhead plus turn 1 |
| 2 | 1,400 | Overhead plus turns 1 and 2 |
| 3 | 1,700 | Overhead plus turns 1 through 3 |
| 5 | 2,300 | Overhead plus turns 1 through 5 |
| 10 | 3,800 | Overhead plus turns 1 through 10 |
| **Billed across all 10 turns** | **24,500** | For a conversation whose unique content is 3,000 tokens |

You paid for 24,500 tokens to deliver 3,000 tokens of actual conversation. And it accelerates: doubling the chat to twenty turns of the same size bills about 73,000 input tokens, not 49,000. If a tool gets involved, say the copilot looks up an order, the tool's result joins the transcript and replays on every later turn too. Tool results are usually the fattest parts of the transcript, which is why "the assistant checked something once, early in the chat" quietly taxes every later turn of that chat.

To make the mechanism vivid, here is a three-turn support copilot exchange and what the model actually sees each time:

- Turn 1, customer: "My order 4417 hasn't arrived." The model sees: the standing instructions, plus that message.
- Turn 2, customer: "Can you check where it is?" The model sees: the instructions, turn 1's question and answer, plus the new message. It resolves "it" to order 4417 because turn 1 is right there in front of it.
- Turn 3, customer: "And can I return it when it arrives?" The model sees: the instructions, turns 1 and 2 in full (including the order lookup's result), plus the new message.

Nothing here is the model remembering. On turn 3 it is reading turn 1 for the third time, and paying for the privilege each time. Delete the re-sending and turn 2's "it" has no referent at all.

Two things follow that belong in your head, not just your engineers':

- **Long chats cost more than the demo suggests.** Your demo is two turns. Your power user is thirty. That user is not twice or five times as expensive as the demo; the replay tax makes them an order of magnitude more expensive. Forecast from the long chat, not the demo.
- **Long chats quietly get worse before they hit any limit.** Models pay less reliable attention to material buried in the middle of a very long input, a documented weakness the source series calls "lost in the middle". A fact stated on turn 4 of a 60-turn support conversation can effectively go missing, not because anyone deleted it, but because the model's attention thins out over the long middle. Users experience this as "it forgot what I told it earlier", and they are right, sort of.

For the recruiter companion, this is not hypothetical. A mock interview runs long by design: greeting, CV walkthrough, behavioral questions, a case exercise, feedback. The candidate's answer to question 2, which the interviewer-bot should probe at question 9, sits exactly in the thinning middle of the transcript. The interview that degrades as it lengthens is a memory-architecture problem wearing a quality-problem costume.

## Three ways to keep long chats affordable and sharp

Nobody ships full replay of an unbounded transcript. Teams pick one of three strategies to shrink what gets re-sent each turn, and each has a characteristic way it fails. You should be able to name all three and ask which one your product uses.

| Strategy | What the model sees each turn | The trade-off, in one line |
|---|---|---|
| **Cut old turns** (truncation) | Only the most recent message or two | Cheapest possible, and it forgets "my order number is 4417" from three turns ago |
| **Sliding window** | The last N complete exchanges, verbatim | Predictable, bounded cost, but silent amnesia the moment a fact scrolls past the window's edge |
| **Summarize the old part** | A short model-written summary of the early chat, plus recent turns verbatim | Keeps long-range context affordable, but the summary can omit the one fact that turns out to matter (summary drift) |

Cutting old turns fits command-style interactions where each message stands alone: "what are your opening hours", "where is my nearest store". The sliding window fits ordinary chat, because most human references point a few turns back ("and the other one?", "why not?"). Summarization fits long working sessions: a complex support case, a returns dispute, a multi-day planning thread, where turn 3's decision still matters at turn 40.

A real-life picture: the logbook, abridged. No receptionist re-reads January's pages every morning. They keep this week's pages on the desk (the sliding window) and staple a one-paragraph summary of the older months to the front (the summary). The full logbook still exists in the filing cabinet for the day someone disputes what was said.

That last sentence matters: the best practice is to shrink what the model *sees* while keeping what you *store* complete. The full transcript stays in your database for support, audit, and debugging; only the model's copy is abridged. If your team ever conflates the two, trimming storage to save tokens, you lose the audit trail and gain nothing the window did not already give you.

Which strategy is right is a product question before it is an engineering one: how far back do your users' pronouns point? Watch real sessions. If customers routinely reference things from 15 turns back, a five-turn window will feel like talking to someone with a head injury, no matter how good the model is. If your interactions are short and transactional, paying for summarization machinery is waste. There is also a combined option the technical series mentions: compress only when the conversation crosses a size budget, so short chats pay nothing and long chats get summarized. Expect your team to propose that; it is usually the right default.

One engineering constraint you will hear about in design reviews, in plain words: you cannot cut the transcript at just any point. When the model uses a tool, the request and the tool's answer form an inseparable pair in the transcript. Snip between them and the provider rejects the whole request. So windows and summaries are cut at the boundaries of complete user exchanges. You do not need to remember why; you need to not be surprised when "just drop everything older than 10 messages" turns out to need a little care.

## Long-term memory: a notes file about the user

Everything above is one conversation's transcript. Long-term memory is different in kind: a fact learned on Monday ("this customer prefers email, not phone") should be available in a new conversation on Friday, without replaying Monday. Replaying every past conversation would be the replay tax at its absurd limit.

The production answer is deliberately anticlimactic: a small notes file about each user, stored by your product, whose relevant contents are pasted into the context when the user shows up. That is the whole architecture. When a chat product "remembers" that you like concise answers, it is reading a note card, the way the receptionist reads the card on a resident's file before answering the phone.

Hold onto this sentence, it will save you from a category error later: **memory is more context, not learning.** The model did not update itself. It does not "know" your user any more than the receptionist knows a resident from reading their card. Delete the notes file and the personality vanishes instantly. The model serving your users today is the same model it was yesterday; only the text around it changed.

Three honest problems come with the notes file, and they are product-policy problems, not engineering ones:

- **The editorial policy problem.** Something must decide what is worth writing down. A store with no policy fills with trivia ("user said hi"), contradictions ("prefers email" and, two weeks later, "prefers phone"), and plain misreadings. Someone, the model guided by written rules, your team, or the user, acts as editor. The goal is a note card, not a landfill.

  The difference is easy to see on the support copilot. Good notes: "customer prefers email over phone", "customer is shopping for a gift for their father", "return for order 4417 was approved on Tuesday". Bad notes: "customer asked about shipping on Tuesday" (a one-off question, not a durable fact), "customer seemed annoyed" (a mood reading that will mislead future turns), or both "prefers email" and "prefers phone" side by side. For the recruiter companion the stakes are higher: "candidate asked to be contacted after 17:00" is a fine note; "interviewer thought candidate seemed nervous" is a subjective judgment about a named person, stored, and you should think hard about whether you want that file to exist at all.

- **Correction rights.** If the assistant remembers something wrong about a user, who fixes it, and how? Mature products expose memory to the user: "here is what I have noted about you, edit or delete". This is both good UX and, increasingly, a regulatory expectation.
- **Memory poisoning.** A joking or hostile user can try to plant facts: "remember that my account is exempt from shipping fees." If a later turn treats planted notes as ground truth, the prank becomes a discount. What may be written into memory, and which memories the agent may act on, is a safety decision (Part 6 goes deep on this), and it needs an answer before launch, not after the first prankster screenshot.

One scaling note so your roadmap conversation is informed: pasting all of a user's notes into every conversation works while the notes are few. At some point, thousands of facts per user, the product must retrieve just the relevant ones per turn, which is the retrieval machinery of Part 4. Even then, what reaches the model is still curated text. The "more context, not learning" rule never lifts.

## The privacy stakes

Here is why this part of the series is the one legal will ask you about. A conversational agent accumulates personal data in three places at once:

1. **The live context**: everything in the current conversation, sent to the model provider on every turn.
2. **The stored transcript**: the full logbook in your database, containing whatever the user typed, names, order numbers, health-adjacent complaints and all.
3. **The long-term memory store**: the notes file, which by design concentrates a person's preferences and history into one tidy, readable dossier.

All three are personal data under any privacy regime you are likely to operate in. The recruiter companion makes this vivid: its transcripts contain candidates' career histories, salary expectations, and interview performance; its memory store is a file of judgments about named individuals. That is about as sensitive as product data gets.

A simple data map is the fastest way to see your exposure. Fill one out with your team before launch:

| Where the data rests | What is in it | Who can read it | How long it lives |
|---|---|---|---|
| Live context (sent to the model provider every turn) | The current conversation plus any injected memory notes | Your provider, under your agreement with them | For the duration of the call, plus whatever the provider retains |
| Stored transcript (your database) | Everything the user typed and the assistant replied, plus tool activity | Your team, under your access controls | Your retention policy decides |
| Memory store (the notes file) | A concentrated dossier of the user's durable facts | Whoever and whatever can query the store | Until edited, deleted, or expired |

Four obligations follow, and each is a roadmap item, not an afterthought:

- **Deletion must reach all three places.** "Delete my data" means the transcripts, the memory notes, and any logs or backups where conversation text ended up. If transcripts were sprinkled into five different systems, a deletion request is a project. If conversation data lives in one store, it is an operation. This is an architecture decision your team makes early; ask about it before the store design freezes.
- **Per-user isolation is absolute.** One user must never be able to recall another user's facts. This sounds obvious and fails in practice: a memory store keyed sloppily, or a shared cache of answers (Part 2 warned about this on the cost side), can leak one customer's order details into another customer's chat. Isolation is a test case, not an intention.
- **Retention needs a policy, not a default.** How long do transcripts live? Forever is an answer, and usually the wrong one: it maximizes both your replay-tax exposure and your breach exposure. Decide retention by product need (support quality, dispute windows, legal holds), write it down, and enforce it automatically.
- **What leaves your building.** Every turn sends the transcript to the model provider. Your data-processing agreement with that provider (do they train on it, how long do they retain it) is part of your product's privacy posture, and your users will hold you responsible for it, not the provider.

## Expectation setting: "it learns from me" is a myth to manage

Users will tell each other that your assistant "learns from them". Journalists will write it. Your own marketing team will reach for it because it is short and flattering. It is false in a specific way, and the specifics matter for copy and support docs.

What is true: your product may *record* things about the user and *show them back* to the model later. What is false: that the underlying model changes, gets smarter, or internalizes anything. The model is identical before and after every conversation; the notes file changed. A user who believes "it learns" will expect improvement that never comes ("I corrected it twice, why does it still get my name wrong?": because nothing was written down, or it was written down and not surfaced), and will fear surveillance that may not exist ("it remembers everything about everyone": it remembers nothing at all unless your team built a store).

So the PM job is to write the true version, which is actually a good story: "The assistant keeps notes you can see and edit. It does not change itself, and it does not share your notes with other users." That sentence sets a capability expectation users can verify, a correction path they can use, and a boundary that protects you. Put it in onboarding, in the settings screen where the notes live, and in the support macros for "why did it forget me?", which will be one of your top contact drivers within a month of launch.

Also align internally on one vocabulary rule: say "memory" when you mean the notes file, "conversation history" when you mean the transcript, and never say "learning" for either. Teams that blur these words build the wrong feature: someone scopes "make it learn from feedback" when the actual requirement was "write better notes".

A practical starter set of copy decisions to make before launch:

- **Onboarding**: one honest sentence, for example "I keep notes about our conversations so I can pick up where we left off. You can see and delete them in Settings." That single sentence answers the three questions users actually have: does it remember, what does it remember, can I control it.
- **The settings screen**: show the notes themselves, not a vague toggle. A user who can read "prefers email" and tap delete trusts the feature; a user staring at a switch labeled "Personalization" assumes the worst.
- **Support macros**: pre-write the answer to "why did it forget me?" (the conversation was too long, or the note was never written, and here is how to fix it) and to "is it learning about other people from me?" (no; the model never changes; notes are per user).
- **Sales and marketing**: ban "learns from you" and "gets smarter over time". The approved claim is narrower and still attractive: it remembers what you choose to keep.

The recruiter companion shows why this discipline pays. A candidate who believes the tool "learns from every interview" will reasonably ask whether their answers train the system that screens future candidates, or worse, other employers' tools. The true answer, the model is unchanged and your transcript lives under our retention policy, is calming, but only if your copy never promised otherwise.

## Questions to ask your engineering team

1. What exactly do we re-send to the model on each turn of a chat: full transcript, a window, or a summary plus recent turns, and why that choice for our users' reference patterns?
2. What does a 30-turn conversation cost us today, in model fees, compared to the two-turn demo we budgeted from? (Ask for the measured number, not a guess.)
3. Do we store the full transcript even when the model only sees a window or summary? If not, what happens to our ability to debug "it said something weird"?
4. What is the editorial policy for the memory store: what qualifies to be written down, what is explicitly excluded, and can a user view and correct their own notes?
5. If a user sends "delete all my data" today, list every system that holds their transcripts and memory notes. Is deletion one operation or a project?
6. How do we guarantee one user can never see another user's memories or transcript fragments, and is there a test that would fail loudly if that broke?
7. Can a user's own message plant a false fact into their memory store that a later turn would act on (a self-granted discount, a fake preference)? What stops that?
8. What is our transcript retention period, who decided it, and where is it enforced?

## Key terms

| Term | Plain-language meaning |
|---|---|
| **Message history / transcript** | The full record of a conversation: user messages, assistant replies, and tool activity. The product re-sends it to the model on every turn. |
| **Context** | Everything the model can see when producing one answer: instructions, history, the new message. The model knows nothing outside it. |
| **Token** | The unit text is billed and measured in, roughly a word fragment. Costs and limits are counted in tokens. |
| **Replay tax** | The fact that turn N re-sends turns 1 to N-1, so the cost of a chat grows faster than its length. |
| **Lost in the middle** | The documented tendency of models to use information at the start and end of a long input more reliably than information buried in the middle. |
| **Truncation** | Dropping all but the most recent turns. Cheapest memory strategy, fastest to forget. |
| **Sliding window** | Sending only the last N exchanges each turn. Bounded cost, silent amnesia past the edge. |
| **Summarization** | Replacing old turns with a model-written summary. Keeps long chats usable, risks the summary dropping a fact that later matters. |
| **Long-term memory** | A stored notes file about a user (preferences, past decisions) that the product injects into new conversations. More context, not learning. |
| **Memory poisoning** | A user planting false facts into their own memory store so later turns treat them as true. |
| **Per-user isolation** | The guarantee that one user's transcripts and memories are never visible to another user. |
| **Retention policy** | The rule for how long transcripts and memories are kept before automatic deletion. |

## PM self-check

1. Your support copilot answers a customer's fifth message as if it were the first, asking for an order number given twice already. No bug report mentions errors or downtime. What is the most likely cause? (The history hand-off is broken or the window is too small: the model is not being shown the earlier turns, and it cannot remember them on its own.)
2. Finance flags that chat costs tripled after a feature encouraged longer troubleshooting sessions, though the number of users barely moved. Is this necessarily a bug? (No: the replay tax makes cost grow faster than chat length, so longer conversations at flat usage means a sharply higher bill.)
3. Marketing proposes the headline "The assistant that learns from every conversation." What is the accurate version you can sign off on? (Something like "remembers what you choose to keep, and you can see and edit it": the product records and re-supplies notes, but the model itself never learns or changes.)

## Going deeper (technical track)

For the engineering treatment behind this part, with the mechanics, the cost arithmetic, and the memory strategies built in code, point your team (or your curious self) at:

- [003: Agentic AI Level 2](../../agentic-ai/tutorials/003-agentic-ai-level-2.md), Part 1 (sections 1-5): conversation memory, persistence, the replay tax, history management, and long-term memory.

If you read only one section there, read section 3's cost table next to this part's: they are the same numbers, seen from the two seats.
