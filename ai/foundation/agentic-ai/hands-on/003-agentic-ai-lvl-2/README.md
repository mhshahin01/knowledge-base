# 003 - Conversation Memory: `all_messages()` vs `new_messages()`

> Last updated: 2026-09-02 | Verified against: pydantic-ai 2.35.0, Python 3.14.3
> Difficulty: Beginner | Estimated time: 15 minutes

The smallest experiment that makes multi-turn memory undeniable: five scripted turns through one
agent, run twice. `option-a-all-messages.py` continues each run with `result.all_messages()`;
`option-b-new-messages.py` continues with `result.new_messages()`. The two files are identical
except for that one marked line, and they print everything in between (the history handed in, the
reply, the usage), so you watch one line of code decide whether the agent remembers.

This is the hands-on companion of Section 1 of
[`003-agentic-ai-level-2.md`](../../../tutorials/003-agentic-ai-level-2.md).

**What it demonstrates**

- Conversation memory is an argument, not a model feature: `message_history=` is the whole trick.
- `all_messages()` accumulates: the trace handed in grows 0, 4, 6, 8, 10 messages across the five
  turns, and "my unit" resolves at turn 5.
- `new_messages()` resets: the trace handed in goes 0, 4, 2, 2, 2. Turn 2 still works, which is
  what makes the bug sneaky; turn 3 is where "And tomorrow?" first arrives with no unit in sight.
- Every turn is bigger than the last under Option A: the replay tax of Section 3 of the tutorial,
  visible in the `usage` lines.

---

## Files

| File | Purpose |
| --- | --- |
| `option-a-all-messages.py` | The correct continuation: accumulate the full transcript. |
| `option-b-new-messages.py` | The amnesia bug: hand back only the latest run. |
| `.env` | Holds `OPENAI_API_KEY`. Git-ignored, never committed. |
| `.env-sample` | Committed template. Copy to `.env` and set your key. |

There is no shared module. Each file is standalone and runnable on its own, because the whole point
is to read one against the other: `diff` them and you get the docstring plus one line.

---

## Setup

```powershell
cd W:\ITV\lrn\knowledge-base-first\ai\foundation\agentic-ai\hands-on\003-agentic-ai-lvl-2

pip install pydantic-ai python-dotenv

copy .env-sample .env
notepad .env                 # replace "Your API KEY" with your real key
```

Leave the placeholder and the run falls back to `TestModel`, free and offline. In that mode the
mechanics (history growth, tool-call parts, message counts) are fully visible, but the replies are
canned placeholders like `success (no tool calls)`. Set a real key to see the actual conversation:
reply wording then varies run to run, and the traces look like the ones in the tutorial.

## How to run

```powershell
python option-a-all-messages.py
python option-b-new-messages.py
```

Each runs the same five turns non-interactively:

```text
TURNS = [
    "My unit is A-12.",
    "Any bookings for my unit today?",
    "And tomorrow?",
    "Which amenity did I book tomorrow?",
    "What was my unit again?",
]
```

A booking tool backed by a fixed in-memory table (A-12 has the Swimming Pool today and the Yoga
Room tomorrow) keeps the traces deterministic on the tool side.

---

## What to watch

**Option A, the history handed in grows every turn.** Message counts handed to runs 1..5,
measured on a real `gpt-5` run: 0, 2, 6, 10, 14. By turn 5 the model sees the complete case file
(user texts, its own replies, the tool calls and tool returns), so "What was my unit again?" is
trivially answerable. Notice the `usage` lines too: every run re-sends everything before it (input
tokens grew 144 → 527 → 714 → 1135 across the first four turns).

**Option B, the history handed in resets after turn 2.** Message counts: 0, 2, 4, 4, 4. Turn 2
still sees turn 1, so the demo looks healthy; turn 3 hands in only turn 2's exchange, and the user
texts of turns 1–3 are gone. From then on the agent is a goldfish with a one-exchange memory, and
the final transcript (printed at the end) contains only the last exchange instead of the whole
conversation.

**The honest wrinkle.** On the measured real run, Option B *still* answered turn 5 correctly,
because "A-12" survived inside the surviving exchange's tool-call arguments
(`bookings_by_unit({"unit_id":"A-12",...})`), not in any memory. Facts can hitchhike one turn at a
time inside tool parts. To watch the amnesia bite in plain English, add a fact that never passes
through a tool: turn 1 "I prefer email, not phone", turn 5 "How should the office contact me?"

Exact counts vary with how many tool calls a turn triggers: a tool-using turn adds 4 messages (user
request, tool-call response, tool-return request, text response), a plain answer adds 2. The
invariant is the trend: Option A grows every turn, Option B stalls at one exchange.

The complete walkthrough, with the per-turn "what the model sees / what is lost" tables for both
options, is in Section 1 of the tutorial.

---

## Things to try next

1. `diff option-a-all-messages.py option-b-new-messages.py`. One line of code is the entire
   difference between a conversationalist and a goldfish.
2. Add a sixth turn ("Book the pool for me at 6pm") and watch which option can even attempt it.
3. Print `result.usage.input_tokens` per turn under Option A and plot it against turn number: that
   curve is Section 3's replay tax, and it is why history processors exist (Section 4).
4. Cap Option A by handing in `result.all_messages()[-4:]` instead, and find the turn where it
   breaks the same way Option B does. (Mind the orphaned tool pair, Section 4 of the tutorial.)
5. Run Option B with a real key twice and compare where the model first asks "which unit?": the
   break is deterministic, the wording is not.
