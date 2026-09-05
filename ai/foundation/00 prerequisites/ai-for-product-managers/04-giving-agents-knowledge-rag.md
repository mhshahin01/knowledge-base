# Giving Agents Knowledge: RAG

> Part 4 of 8 in the **AI for Product Managers** series | Reading time: ~20 minutes | No code
> Series home: [README](README.md) | Previous: [Memory and Conversations](03-memory-and-conversations.md) | Next: [Tools, Integrations, and MCP](05-tools-integrations-and-mcp.md)

## Why this matters to you as a PM

Your support copilot will be asked about your return policy, your warranty terms, and your shipping rules. Your recruiter companion will be asked about your hiring criteria and your interview process. The AI model behind both has never read any of these documents, and what it does not know, it invents, fluently. How your team gives the agent your company's knowledge is a product decision with direct consequences for cost, accuracy, update speed, and liability. That mechanism is called RAG, and this part gives you enough of it to scope features, read vendor claims, and challenge your engineers with the right questions.

## The problem: the model never read your documents

A large language model knows what was in its training data: the public internet, books, and licensed text. It has not read your help center, your return policy, your internal pricing sheet, or your job-post rubric. When a customer asks the support copilot "can I return a sale item after 40 days?", the model has no idea what your policy says. Left alone, it answers from general knowledge of what return policies usually look like. The answer sounds confident and may be wrong. In a support product, a confident wrong answer is worse than no answer.

There are two bad ways to solve this, and one good one.

**Bad option 1: paste everything into the instructions.** You can put your entire knowledge base into the agent's standing instructions, the text that accompanies every request. This works, and for very small document sets it is even the right call. But instructions are re-sent on every call of every turn of every conversation. In the source tutorial's worked example, a 40-page policy set is about 30,000 words-worth of tokens (the units text is billed in). Over a 10-turn conversation, pasting everything costs roughly 324,500 input tokens where retrieval costs roughly 24,500. That is more than ten times the input cost, every conversation, forever. And when the return window changes from 30 to 45 days, someone has to edit a giant block of prompt text and ship it through your change process.

**Bad option 2: give it nothing.** The model answers from general knowledge and invents your policy. Users cannot tell the difference between a correct answer and an invented one, because both are written in the same fluent tone.

**The third option: retrieve only what the question needs.** Store the documents outside the prompt. When a question arrives, find the two or three passages relevant to that specific question and put only those in front of the model. The answer is then written from your actual documents, and the per-question cost stays small no matter how large the document set grows.

This approach has a name: RAG, short for retrieval-augmented generation. In plain words: retrieval (finding the right passages) augments (helps out) generation (the writing of the answer).

A real-life picture: the index-card catalog. Imagine a library with a filing cabinet holding every policy document your company ever wrote, and a receptionist answering questions at the front desk. Nobody expects the receptionist to re-read 40 pages to answer "can I return a sale item?". Instead, the receptionist looks up "returns" in the index-card catalog, pulls the two cards that match, and answers from those. The cabinet holds everything; the desk holds only what this question needs. RAG is that catalog, plus the habit of always checking it before answering.

One honest framing worth memorizing, because every strength and weakness of RAG follows from it: RAG does not make the model read your documents. It makes your software select a few passages and paste them into the request. The model only ever reads what lands in front of it. If retrieval fetches the right passage, the model answers as if it knew your policy all along. If retrieval misses it, the model answers from nothing, and looks exactly the same doing it.

## The pipeline in plain words

RAG is two pipelines that share a database. One runs rarely, when documents change. One runs per question.

**The indexing pipeline (runs when documents change):**

1. **Split documents into pieces.** Your return policy, shipping rules, and warranty terms are cut into smaller passages, typically along the document's own structure: one section or heading per piece. These pieces are called chunks. Each chunk keeps a label saying which document and section it came from.
2. **Store the pieces indexed by meaning.** Each chunk is converted into an embedding: a list of numbers produced by a model trained so that texts with similar meaning get similar numbers. "Quiet hours" and "noise rules" share no keywords, but their numbers come out close. That single property is what makes search by meaning possible: similarity between meanings becomes arithmetic between numbers. The chunks, their numbers, and their source labels go into a searchable index.

**The answering pipeline (runs per user question):**

1. The user's question is converted into numbers with the same embedding model.
2. The index is searched for the chunks whose numbers are closest to the question's numbers: the top few matches, often around five.
3. Those passages are handed to the model along with the question.
4. The model writes the answer from those passages, and names the source document for each claim.

Three properties matter to you as a PM:

- **Indexing is rare and nearly free; answering is cheap per question.** In the source material, indexing a 40-page document set costs about $0.0006, once, plus a re-index when a document changes. The embeddings are nearly free; the model calls that write the answers are the real bill. (The dollar figure is from the source tutorial; treat any number your vendor quotes you as worth checking against your own document set.)
- **Chunking decisions decide answer quality more than anything else.** If a rule gets cut in half between two chunks ("returns accepted within 30" in one piece, "days of delivery" in another), retrieval can fetch only half the rule and the answer contradicts the document. Splitting along natural boundaries like headings prevents most of this; where fixed-size splitting is unavoidable, chunks overlap by 10 to 20 percent so boundary facts survive (these ranges are community guidance cited in the source, not vendor guarantees).
- **The agent sees none of this machinery.** From the model's point of view, "search the policy documents" is one more capability on its panel, like looking up an order. That is good news for your architecture: retrieval bolts onto an existing agent as one added tool.
- **The embedding model is a one-way door.** Numbers produced by one embedding model are meaningless to another, even when the lists are the same length. Switching embedding models means re-converting every document and rebuilding the index, then re-running the question table. Vendors sometimes present model upgrades as a settings toggle; for a RAG index, they are a migration.

## Why answers still go wrong: two different failures

When a RAG-powered answer is wrong, it failed in one of two independent places, and the distinction is the most useful thing in this part, because the two failures have different fixes and different owners.

**Failure 1: retrieval miss.** The right passage never reached the model. The customer asked "can I use a discount code on a clearance item?" and the index returned passages about loyalty points instead. The model then answered from nothing. Causes: the rule was split badly at chunking time, the user's vocabulary differs too far from the document's, or the search returned too few candidates. Owners: the engineers who built the indexing and search pipeline. Fixes: better chunking, a better embedding model, more candidates returned, or keyword search added alongside meaning search for exact terms like product codes.

**Failure 2: grounding failure.** The right passage was fetched and the model still ruined the answer. It blended your 30-day return window with its general knowledge ("most stores allow 60 days"), or it answered a different question using the wrong retrieved passage, or it invented policy on a topic the documents do not cover at all. Owners: whoever writes the agent's instructions and output checks. Fixes: instructions that forbid answering outside the retrieved passages, require naming the source, and require an honest "our documents do not cover this" when nothing relevant was found.

| | Retrieval miss | Grounding failure |
|---|---|---|
| What happened | The right passage never reached the model | The right passage arrived and was misused |
| Typical symptom | Answer ignores a policy the documents clearly cover | Answer blends your policy with generic "industry standard" claims |
| Owner | Indexing and search pipeline | Agent instructions and output checks |
| Typical fix | Better chunking, better search, more candidates | Stricter answer-from-passages rules, required citations, honest refusals |

From the outside, these two failures look identical: a confident wrong answer. That is why teams get stuck blaming "the model" for weeks when the actual fault is a chunking choice, or rebuilding the search index when the actual fault is a missing sentence in the instructions. The measurement section below exists precisely to keep these apart.

A recruiter-companion version: the companion rates a CV poorly because "the candidate lacks Kubernetes experience" when the job post asks for "container orchestration". If the job post passage was never fetched, that is a retrieval miss. If it was fetched and the model applied its own generic idea of what senior engineers need, that is a grounding failure. Same symptom, different fix, different owner.

## Citations: the feature that makes answers checkable

A well-built RAG answer names its source: "Sale items can be returned within 14 days (returns-policy.pdf, section 3)." This is not decoration. It is the difference between an answer you can audit and one you cannot.

Here is the uncomfortable fact: an uncited correct answer and a hallucinated one are indistinguishable from the outside. Both are fluent, plausible prose. Only the citation lets a user check for themselves, and lets you check at scale: your team can sample answers, follow the citations, and verify that the cited passage actually says what the answer claims.

Citations also change user behavior and trust. A support answer that says "according to our returns policy, section 3" invites verification and survives it. A support answer that just asserts invites a support ticket when it is wrong. For the recruiter companion, a CV evaluation that cites the job-post criterion it applied is defensible to a hiring manager; one that does not is just an opinion with extra steps.

Citations are only possible because every chunk carried its source label through the pipeline. If your team's retrieved passages arrive as unlabeled blobs of text, no instruction can produce citations afterward. When you review a RAG design, ask where the source labels live. The answer should be "attached to every piece, from the moment the document is split".

Citations also define your review workflow as a PM. Sample a handful of answers each week, follow each citation, and check whether the cited passage actually supports the claim. That is a task you can do yourself, without engineers, and it catches both failure modes: a citation that does not exist points at retrieval, a citation that exists but does not support the claim points at grounding.

## Freshness: updating knowledge without touching the product

One of RAG's strongest product properties is that knowledge updates are decoupled from product changes. When your return window changes from 30 to 45 days, the update is: edit the policy document, re-run the indexing step for that one document. The next answer reflects the new policy. No prompt edits, no release, no regression risk to the agent's behavior.

Compare the paste-everything approach: a policy change is an edit to a giant instructions block, shipped through your change process, with the risk that someone accidentally alters the agent's behavioral rules while fixing a shipping fact.

This has an organizational consequence worth planning for: with RAG, the people who own the content (support leads, policy writers, recruiters) can update what the agent knows without involving the people who own the product. That is a genuine operational win, but it means you need a lightweight process for who may publish into the knowledge base, because a wrong document now produces wrong answers at scale, instantly. The agent will believe whatever the index contains.

For the recruiter companion, freshness matters differently: job posts open and close weekly, and hiring criteria shift mid-search. A RAG setup lets a recruiter update the criteria document and have the next CV evaluation use it, without an engineer in the loop. It also means a stale job post produces confidently stale evaluations, so the publishing process should include expiry or review dates for documents, not just upload.

## When RAG beats a long prompt, and when to just paste

RAG is not always the answer. The decision is between two ways of putting knowledge in front of the model: all of it, always (the long prompt), or the relevant slice, on demand (RAG). Make the call with arithmetic, not fashion.

**Choose the long prompt (paste the document into the instructions) when:**

- **The knowledge is small and stable.** A one-page price list, a dozen product names, a short FAQ. Building a pipeline to serve a page of stable text is engineering as a hobby.
- **Every question needs most of the document.** A legal clause whose meaning depends on the whole section retrieves badly in slices; the relevant slice is the document.
- **You have zero appetite for infrastructure.** The long prompt has no index to build, host, or keep fresh. Its entire operational surface is a block of text.

**Choose RAG when:**

- The document set is large, growing, or edited often (help centers, policy libraries, product catalogs).
- Answers must cite sources (metadata per chunk is what makes citations possible).
- Different users may see different documents (per-customer or per-role visibility happens at search time).

**The decision guide, condensed:**

| Your situation | Choice |
|---|---|
| Small, stable facts that fit on a page | Paste into the instructions |
| Large or frequently edited document set | RAG |
| Questions need whole documents to answer | Paste (or long prompt) |
| Answers must cite sources | RAG |
| Different users may see different documents | RAG |
| Prototype stage, no infrastructure budget | Paste now, revisit at the first cost or freshness complaint |

A real-life picture: the binder versus the note. A one-page specials board gets read aloud to every guest. A 400-page regulations binder gets quoted by section. Nobody reads the binder aloud, and nobody builds a catalog for the specials board.

The cost arithmetic, from the source material: pasting a 40-page document set into every call multiplies a 10-turn conversation's input cost roughly tenfold (about 324,500 tokens versus about 24,500 with retrieval), and retrieval fetches only a few passages, roughly 2,000 tokens, and only on turns where the question actually needs the documents. The crossover is not subtle: past a few pages, the per-call tax dominates. And the decision is reversible: start with a pasted page, and revisit the first time you hit a cost complaint or a freshness complaint.

## Measuring it: the question table

"Taste is not measurement" applies doubly to RAG, because a good demo proves nothing about the questions you did not ask. The discipline from the source material is a fixed table of real user questions, each paired with the source that should answer it, run after every change.

The table has two levels, matching the two failure modes:

**Level 1: did retrieval fetch the right source?** For each question, check whether the expected passage landed in the top results. This level is cheap and deterministic: given a fixed index, the same question always returns the same results. The valuable rows are the tricky ones:

- Vocabulary-mismatch questions: "can I run a blender at 11pm?" should fetch the noise rules. These test whether meaning-based search earns its keep.
- Absent-topic questions: "what is the fine for late rent?" when no document covers rent. The correct retrieval is nothing, and the correct answer is a refusal. This tests the empty case most demos skip.

**Level 2: given the right passage, did the answer use it?** Run the full agent and check behavior, not wording: did it cite the expected source? Did the absent-topic question produce an honest refusal? Wording varies run to run; citations and refusals are checkable.

Two working rules:

- **Change one thing at a time.** New chunking, new embedding model, more passages per query: rerun the table after each. The table is how you know a "better" search component is better on your documents, not on a vendor's benchmark.
- **Grow the table from failures.** Every user question that was answered badly becomes a row. Over time the table is a fossil record of everything that ever went wrong, and it is the artifact you should ask to see in reviews. A team with a 50-row table built from real failures knows more about their product than a team with a great demo.

One caution from the source material worth repeating to your team: similarity scores and cutoffs are specific to your documents and your embedding model. A threshold copied from a blog post is a guess. Tune on your table.

Run the table after every change: new chunking, new model, new instructions, and after significant document updates. A number that moves is information; a demo that still looks good is not.

## Questions to ask your engineering team

1. When an answer is wrong, how do we tell whether retrieval missed the passage or the model ignored it? Can you show me the last five failures classified that way?
2. How are documents split into chunks, and what protects a rule that would be cut in half between two chunks?
3. Does every retrieved passage carry its source label, so answers can cite the document they came from?
4. What does the agent say when the documents do not cover the question? Show me that behavior on three off-topic questions.
5. What is the process for updating a document, and how long until a corrected policy shows up in live answers?
6. Do we have a fixed question table for retrieval quality? What is the current hit rate, and which rows were added from real user failures?
7. For our document set, where is the crossover between pasting into the prompt and maintaining an index, and which side are we on, with what numbers?
8. If we ever switch the embedding model, what is the re-indexing plan? (Vectors from different models are not comparable, so this is a rebuild, not a toggle.)

## Key terms

| Term | Plain-language meaning |
|---|---|
| RAG | Retrieval-augmented generation: fetching a few relevant passages from your documents and putting them in front of the model, so it answers from them instead of from memory |
| Chunk | One piece of a split document, the unit the index stores and returns, with a source label attached |
| Chunking | How documents are divided into pieces; done well it follows headings and sections, done badly it cuts rules in half |
| Embedding | A list of numbers representing a text's meaning, arranged so similar meanings get similar numbers |
| Vector index | The searchable store of chunk embeddings; the "card catalog" that finds the passages closest to a question |
| Semantic search | Search by meaning rather than by exact keywords, powered by embeddings |
| Retrieval miss | The failure where the right passage never reached the model; fixed in the indexing and search pipeline |
| Grounding failure | The failure where the right passage arrived but the answer ignored it, misread it, or went beyond it; fixed in instructions and output checks |
| Citation | The source document named alongside a claim; what makes an answer checkable by users and by you |
| Refusal | The correct answer when the documents do not cover the question: "our documents do not say" |
| Long prompt | The alternative to RAG: pasting the whole document into the instructions, right for small stable content |
| Question table | A fixed list of real questions with the source that should answer each, rerun after every change; the measurement of a RAG system |

## PM self-check

1. Customers complain the copilot gives wrong shipping answers. Your engineer says "the model is hallucinating, we need a better model." What do you ask first? (Whether the shipping passage is actually being retrieved for those questions; a retrieval miss and a grounding failure look identical, and neither is fixed by a different model.)
2. Legal updates the refund policy and asks how fast the agent will reflect it. What determines your answer? (The re-indexing process for one document, typically minutes, not a release cycle; this is a core RAG property.)
3. A vendor demo shows flawless answers to ten questions. What do you request before buying? (Their retrieval hit rate on a fixed question table, including questions whose answers are not in the documents, measured on your content.)

## Going deeper (technical track)

- [004: RAG](../../agentic-ai/tutorials/004-rag.md): the full engineering tutorial: chunking strategies, embeddings, vector search, the retrieval tool, grounding rules, cost arithmetic, and evaluation tables.
