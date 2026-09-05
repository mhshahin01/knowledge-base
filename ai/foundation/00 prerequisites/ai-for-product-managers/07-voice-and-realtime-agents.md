# Voice and Realtime Agents

> Part 7 of 8 in the **AI for Product Managers** series | Reading time: ~15 minutes | No code
> Series home: [README](README.md) | Previous: [Trust, Safety, and Control](06-trust-safety-and-control.md) | Next: [Measuring Quality and Shipping](08-measuring-quality-and-shipping.md)

## Why this matters to you as a PM

Everything in parts 1 through 6 assumed the user types and the agent replies in text. Voice changes none of the concepts underneath (the agent still reasons, acts, and observes in a loop), but it multiplies every cost and every failure mode you have already learned: latency budgets get brutal, mistakes cannot be scrolled back to, and a slow tool call becomes dead air on a live call. Voice is also where roadmaps get ambitious too early, because a spoken demo feels like magic in a meeting room. Your job is to know what voice actually adds, what it removes, and when the product is ready for it.

This part stays deliberately short compared with the safety and measurement parts, for a reason that is itself a lesson: voice adds no new agent concepts. If parts 2, 3, and 6 made sense to you, you already hold most of the mental models voice requires. What follows is mostly about where those models get stressed hardest.

## What changes when users talk instead of type

Text chat is forgiving. The user reads at their own pace, scrolls back, and tolerates a few seconds of a typing indicator. Spoken conversation has different physics, and four of them matter for your roadmap.

To make this concrete, picture the support copilot handling a return over a voice call. The customer says "I want to send back the jacket." Everything the text version gets for free is now work: the agent must notice exactly when the customer finished speaking, reply fast enough that the line does not feel dead, survive the customer cutting in with "wait, not that one", keep its answers short enough to be heard rather than read, and understand a speaker who is on a speakerphone in an echoing kitchen with an accent the training data underrepresents. The agent's brain is identical to the text product. Everything around the brain is harder.

**Sub-second turn-taking.** In a natural conversation, people respond to each other in well under a second. Stretch that gap to two or three seconds (an illustrative figure, but close to what most users start noticing) and the experience stops feeling like a conversation and starts feeling like leaving voicemails for a slow machine. In text chat, the same two seconds are invisible. This is the single biggest engineering pressure in voice: the whole chain from "user stops talking" to "agent starts replying" has to fit inside a fraction of a second to feel human, and every stage in that chain spends part of the budget.

**Interruptions and barge-in.** People interrupt. A customer who hears the support copilot start reading the wrong order status will say "no, the other order" halfway through the sentence. A voice agent must detect that the user has started speaking, stop its own reply mid-word, and pick up the new thread. In text, this problem does not exist; the user simply waits or starts a new message. In voice, an agent that cannot be interrupted feels like talking to a phone menu from 2005.

**No re-reading.** A text answer can be scanned twice. A spoken answer is gone the moment it is said. That means spoken replies must be shorter, plainer, and structured for the ear: one answer, then an offer to go deeper, not a five-paragraph policy explanation. It also means the agent should confirm consequential things out loud ("so that's a return of the blue jacket, size medium, correct?") because the user has no written record to check against. Expect this to change how your team writes the agent's instructions: a prompt that produces excellent chat replies usually produces spoken answers that are too long, and the fix is deliberate writing for the ear, not a smaller font on the same text.

**Accents and noise are reality, not edge cases.** Speech systems are trained on large collections of real speech, but your users include regional accents, call-center headsets, speakerphones in kitchens, and patchy mobile connections. Any of these can garble what the agent hears, and the agent may not know it heard wrong. In the recruiter companion, this is concrete: the mock-interview feature was explicitly gated on Arabic speech quality before any voice version could ship, because an interviewer that mishears the candidate is worse than no interviewer. Treat "how well does it hear our actual users, in their actual environments" as a launch metric with a threshold, not a test the team runs once on a quiet office microphone.

One more shift sits underneath all four: the send button disappears. In text, the user decides when a message is complete by pressing send. In voice, the system has to guess, from pauses and intonation, whether the user finished a thought or just stopped to breathe. This is called turn detection, and when it guesses wrong in one direction the agent talks over the user, and when it guesses wrong in the other the agent sits silent while the user waits. Much of what makes a voice product feel polished or broken is this one judgment call, made continuously.

A real-life picture: text chat is email, voice is a phone call. The same person handles both, but the phone call punishes slow thinking, rewards brevity, and gives no second chance to re-read.

For quick reference:

| Expectation | Text chat | Voice |
|---|---|---|
| Response delay | A few seconds is fine | Sub-second or it feels broken |
| Long answers | Acceptable; user can skim | Hostile; user cannot skim audio |
| Mistakes | User scrolls back and re-reads | Gone the moment they are spoken |
| Interruptions | Not applicable | Constant, and must be handled |
| Input quality | Clean typed text | Accents, noise, bad microphones |

## The two architectures, in plain terms

There are two ways to build a voice agent today, and your team will pick one. You should understand both well enough to follow the trade-off conversation, because the choice determines what you can measure, what you can swap, and how natural the result sounds.

### The relay race: separate stages

The first approach chains three specialist components together. A speech-to-text stage listens to the user and produces text. The agent (the same kind you know from parts 1 through 6) thinks about the text and decides what to do, including calling tools. A text-to-speech stage turns the reply back into audio. A fourth component, turn detection, decides when the user has finished speaking and when an interruption is happening.

A real-life picture: this is a relay race. Three runners each handle one leg and pass the baton. Each runner is a specialist you can swap: if a better transcription service appears next quarter, you replace one runner without touching the others.

The strengths are exactly what parts 2 and 6 taught you to value. Each stage is independently measurable (how accurate was the transcription, how long did the agent think, how natural does the voice sound), independently replaceable (swap vendors per stage), and independently debuggable (you can read the transcript to see where things went wrong). When the support copilot mishears "order 45" as "order 54", a relay race lets you point at the exact stage that failed and fix or replace that stage alone. The weakness is latency: every baton pass costs time, and the delays add up across the chain. Hitting that sub-second turn-taking feel with a relay race takes real engineering effort.

### One model, audio in, audio out

The second approach uses a single speech-to-speech model: audio goes in, audio comes out, and the model handles understanding, thinking, and speaking in one step. There is no text in the middle unless you ask for it.

A real-life picture: instead of a relay team, you hire one interpreter who listens and speaks directly, never writing anything down. Faster and smoother, but you cannot easily inspect or replace one leg of the job.

The strengths are lower latency (no baton passes) and more natural prosody, the rhythm, stress, and tone of speech, because the model produces speech directly rather than reading out synthesized text. It can hear hesitation or urgency in the user's voice and respond to it. For the recruiter companion's mock interview, that matters: a spoken interviewer that notices a hesitant answer and follows up the way a human interviewer would is a genuinely better training experience than a relay race reading out its lines.

The weaknesses follow from the same design. The stages are no longer independently swappable or measurable, so when quality drops you cannot easily tell whether the problem was hearing, thinking, or speaking, and any transcript has to be requested from the model rather than read off a stage you own. These models are also newer and come with practical constraints. One current speech-to-speech service, for example, caps a continuous session at about eight minutes, after which the connection must be renewed and the conversation carried over into the new session. Your engineers can handle that pattern, but you should know it exists before promising hour-long uninterrupted calls. Vendor choice is narrower too: with a relay race you can mix a transcription specialist, your preferred agent model, and a voice specialist; with speech-to-speech you buy one vendor's whole package.

### How to think about the choice

| | Relay race (separate stages) | Speech-to-speech (one model) |
|---|---|---|
| Latency | Higher; delays add up across stages | Lower; single hop |
| Naturalness of voice | Good, but stitched together | Better rhythm and tone |
| Swapping components | Easy, per stage | Not possible; it is one model |
| Measuring each step | Easy, each stage has its own numbers | Harder; the middle is opaque |
| Vendor options | Many per stage | Few |
| Maturity | Established | Newer, with session limits and quirks |

For most products today, the relay race is the safer first build because it is measurable and debuggable, and measurability is what lets you improve. Speech-to-speech is the likely long-term direction and worth a spike once the team has voice experience. Ask which one your team chose and why; either answer can be right, but "we did not compare" is not.

Whichever architecture is chosen, one thing stays constant: the agent's brain and its tools do not change. The order lookup, the return processing, the interview scoring, all of the tool loop from earlier parts works the same way whether the agent's mouth and ears are text or audio. Voice is a new interface wrapped around the same loop, which is why it belongs late in the series and late in your roadmap.

One footnote worth knowing exists: some teams blend the two approaches, using the relay race where measurability matters most and a speech-to-speech model where naturalness matters most, sometimes even in different features of the same product. You do not need to design this blend yourself, but if your team proposes it, it is a legitimate engineering position rather than indecision.

## Telephony: voice agents on actual phone lines

A voice agent does not have to live inside your app. The same machinery can connect to the ordinary telephone network, which means the agent can answer a real phone number, or place outbound calls. For a PM this is less a technical detail than a distribution decision: the phone network is the largest voice interface that already exists, and your users already know how to use it.

This opens product shapes that app-based voice cannot:

- **Support without an app.** The store's support copilot can answer the phone line customers already call, look up the order while talking, and process the return in one call, for customers who will never install anything.
- **Booking and scheduling.** An agent that calls a supplier to confirm a delivery window, or answers inbound booking calls after hours, reaches people whose entire workflow is the phone.
- **The recruiter companion's phone screen.** A first-round screening call conducted by the agent, on a normal phone call, at whatever hour suits the candidate.

Telephony also changes your addressable market in a way worth stating in a roadmap review: the phone network reaches every customer with any phone, including users on basic handsets, users who will not install your app, and users in markets where a phone call is simply how business gets done. If your growth plan includes those users, telephony is not an add-on to the voice story, it is the main event.

A practical note for planning: a phone-call agent needs somewhere to live. Voice systems run on real-time audio infrastructure that your web stack does not already have, and teams either assemble and host that infrastructure themselves or rent it as a managed service. That build-versus-rent decision carries staffing and cost consequences beyond the AI parts, so ask for it explicitly rather than discovering it in an estimate.

Phone lines also raise the stakes of everything in part 6. A phone call carries no interface chrome: no buttons, no disclaimers on screen, no "confirm" dialog. Identity verification ("prove you are the account holder before I read out order details"), consent and call-recording disclosure, and the escalation path to a human all have to happen in speech. Callers also bring learned expectations from decades of phone menus, and some will press zero, shout "agent", or simply stay silent to reach a person; decide how the system responds to each. These are product decisions, and they belong in the requirements before the first call, not in a postmortem after the first complaint.

## Cost and quality: voice multiplies what you already know

Part 2 gave you the latency and resilience toolkit for text agents. Voice does not add new categories of concern; it turns the volume up on the existing ones. Four of them deserve a place in your planning documents.

- **Latency is now user-visible in the worst way.** In text, a slow tool call shows a spinner. In voice, it is a silent pause on a live call. When the support copilot looks up an order, that lookup is now an audible gap. Teams handle this with spoken acknowledgments ("let me check that for you") and by keeping slow operations behind the same gate discipline from earlier parts, so a sluggish lookup never stalls the conversation. As a PM, treat "what does the agent say while it thinks" as a designed feature, not an afterthought.
- **Resilience matters more because sessions are live.** A text user whose session hiccups refreshes the page. A caller whose session drops has been hung up on. Reconnection, session renewal (remember the eight-minute cap on at least one speech-to-speech service), and graceful handoff to a human are launch requirements, not polish.
- **Costs stack per stage.** In the relay-race architecture you pay for transcription, for the agent's thinking, and for speech synthesis, all metered by time or volume, plus telephony minutes if you are on phone lines. A voice conversation typically costs meaningfully more per minute than the same conversation in text (any multiple you hear quoted is illustrative until your team measures your stack). Get a cost-per-call estimate next to your cost-per-chat estimate before setting pricing or volume expectations.
- **Quality measurement moves to transcripts and per-stage numbers.** You cannot evaluate voice by listening to a few calls and forming a vibe, the same way part 6 argued you cannot evaluate text agents by reading a few chats. The workable approach: record transcripts, measure each stage (how often was the transcription wrong, how long did each leg take, how often did interruptions misfire), and evaluate the transcripts with the same rigor as text conversations. If your team cannot show you per-stage latency and transcription accuracy numbers, you do not yet have a measurable voice product.

One more quality trap is specific to voice: small text improvements can be voice regressions. A more thorough agent prompt that reads beautifully in a chat window produces spoken replies that are too long to listen to. Voice needs its own instruction style (short spoken replies, one idea at a time, confirm consequential details out loud) and its own evaluation pass, even when the underlying agent is unchanged. Budget for that work; it is not free reuse of the text build.

The summary for planning purposes: voice keeps your part 2 and part 6 disciplines but tightens every tolerance. Whatever latency, failure rate, and cost your text product has today, assume voice will make each one more visible to users and more expensive to fix, and size the voice effort accordingly.

## When voice beats text, and when it loses

Voice is a channel, not an upgrade. It wins in specific contexts and loses in specific others, and shipping it where it loses makes the product worse, because you have paid voice's costs (latency pressure, mishearing risk, higher per-minute spend) without buying voice's benefits.

Voice wins when:

- **Hands are busy.** Driving, cooking, warehouse work, a nurse between patients. The user cannot type, so the alternative to voice is nothing.
- **Accessibility requires it.** Users with limited vision, limited literacy, or motor impairments may have no realistic text option. This is not a niche; it is often the difference between serving a user and excluding them.
- **The market is phone-first.** In many segments and regions, the phone call is the default way business gets done, and an app is the obstacle, not the feature.
- **The conversation is the product.** A mock interview only trains real interview skill if it is spoken; a candidate typing answers to the recruiter companion is rehearsing a different skill than the one the job interview tests.

Voice loses when:

- **Precise identifiers are involved.** Order numbers, tracking codes, account IDs, spellings of names. Humans mishear them, speech systems mistranscribe them, and reading "B as in Bravo" back and forth is misery for everyone. If the task hinges on an exact string, show it or type it.
- **The user needs a link or must copy something.** You cannot click a spoken link, and nobody reliably writes down a URL read aloud.
- **An audit trail matters.** Text gives both sides a written record by default. Voice gives a recording and a transcript that may contain errors, which is a weaker foundation for disputes, compliance, and "but the agent told me" situations.
- **The answer is long or complex.** Anything the user would want to skim, re-read, or compare side by side belongs on a screen.

The strongest products treat this as a both/and: voice for the conversation, with a text message or screen for the confirmation number, the link, and the summary. The support copilot can process the return by voice and then send the return label and confirmation code by message. Plan for the pairing, not for voice alone.

Two questions sharpen the decision for any specific feature. First, if voice were removed, would the target user still be able to complete the task comfortably? If yes, voice is a convenience and should be prioritized like one. If no (hands busy, accessibility, phone-first market), voice is the core value and deserves the harder engineering. Second, does the task's success depend on anything exact or anything the user must keep? If yes, voice alone cannot carry the feature, no matter how good it sounds.

Notice that both running examples answer these questions differently. The support copilot's order lookup is a convenience channel (the customer could type), so voice there is a fast-follow nicety. The mock interview loses its training value without speech, so voice there is core value, and it is exactly the feature that earned a hard quality gate before launch.

## The phasing recommendation

Here is the sequencing this series recommends, stated plainly:

1. **Ship text first.** Voice adds no new agent concepts, it multiplies the existing ones: latency, resilience, observability, evaluation, cost. Those all need to be solid in the text product before voice makes them harder. A team that has not measured its text agent's latency and failure rates is not ready to make those numbers live and audible. Text also buys you the evaluation machinery first: transcripts, scoring, and regression checks built for the text product become the foundation voice quality is measured against later.
2. **Add voice as a fast-follow, not a launch feature.** Once the text product is stable with real users, voice becomes a channel decision, not a research project. This is exactly the path in the running example: the recruiter companion ships text mock interviews first, and the voice version follows only after the text version is proven and after Arabic speech quality is verified, because the interview use case makes speech quality a gating requirement, not a nice-to-have.
3. **Regulated or high-stakes voice keeps the same gates as text, plus new ones.** Everything from part 6 (approval steps, human escalation, action limits) applies unchanged when the agent speaks. Voice adds its own requirements on top: recording consent, identity verification by voice, and a spoken path to a human. If the text version of a feature needed an approval gate before acting, the voice version needs it more, because the user cannot re-read what they agreed to.

If a stakeholder pushes voice at launch, the question to ask back is not "why voice" but "which of our text-agent numbers are already good enough to survive being made audible."

One boundary deserves its own sentence. "Text first" does not mean "voice someday, maybe." For the products where voice is the core value (the mock interview, the phone-line support channel), the fast-follow should be a committed phase with its own success criteria, its own quality gates (speech accuracy on your users' languages and accents, measured, not assumed), and its own cost model. Phasing is a risk decision, not a vagueness license.

## Questions to ask your engineering team

1. What is our measured gap between the user finishing a sentence and the agent starting its reply, and how does it compare to the sub-second feel of natural conversation?
2. Can a user interrupt the agent mid-sentence, and what exactly happens to the conversation state when they do?
3. Which architecture are we using, the relay race of separate stages or a single speech-to-speech model, and what did the comparison look like before we chose?
4. What does the agent say or do while a tool call is running, so the pause does not feel like a dead line?
5. What is our cost per minute of voice conversation, broken down per stage (transcription, thinking, speech synthesis, telephony), against our cost per text conversation?
6. How do we measure transcription accuracy on our actual users' accents and audio conditions, and what is the current number?
7. What happens when a voice session drops or hits a connection time limit mid-conversation, and has that path been tested?
8. For any phone-line feature: how do we verify the caller's identity, disclose recording, and escalate to a human, entirely within a spoken call?

## Key terms

| Term | Plain-language meaning |
|---|---|
| Speech-to-text | The component that listens to the user and writes down what was said |
| Text-to-speech | The component that reads the agent's reply out loud in a synthetic voice |
| Speech-to-speech model | A single model that takes audio in and produces audio out, with no text in the middle |
| Cascaded pipeline | The relay-race architecture: transcription, then the agent, then voice synthesis, as separate stages |
| Turn detection | Deciding when the user has finished speaking and it is the agent's turn, replacing the send button |
| Barge-in | The user interrupting the agent mid-reply, and the agent stopping to listen |
| Prosody | The rhythm, stress, and tone of speech; what makes a voice sound natural rather than robotic |
| Latency | The delay between the user speaking and the agent replying; felt as awkward silence in voice |
| Telephony | Connecting the agent to the ordinary phone network, so it can answer or place real phone calls |
| Session limit | A cap on how long one continuous voice connection can last before it must be renewed |
| Per-stage measurement | Tracking accuracy and speed for each step of the pipeline separately, so problems can be located |
| Spoken acknowledgment | A short phrase the agent says while a tool runs ("let me check that"), so the pause does not feel like a dead line |
| Identity verification by voice | Proving on a phone call that the caller is who they claim to be, without the help of a screen or a login form |

## PM self-check

1. Your team proposes launching the support copilot with voice on day one, ahead of text. What is your response? (Voice multiplies latency, resilience, and measurement problems rather than adding new concepts, so text should prove out first and voice should follow once the numbers are stable.)
2. A customer must give the agent a fourteen-character tracking code. Voice or text? (Text: precise identifiers are where voice loses, because both humans and speech systems mangle exact strings.)
3. In a review, your team shows you five recorded voice calls that "sound great." What do you ask for instead? (Aggregate measurements: per-stage latency, transcription accuracy, interruption behavior, and transcript-based quality scores, not curated examples.)

## Going deeper (technical track)

- [The series plan, 009 section (Voice and Realtime Agents)](../../agentic-ai/tutorials/plan-tutorials-003-011.md): the technical tutorial this part consolidates, covering the relay-race pipeline and speech-to-speech models, turn detection, telephony, and per-stage observability, all built in code.
