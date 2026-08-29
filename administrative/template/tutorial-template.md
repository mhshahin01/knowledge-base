# Tutorial Template

> Last updated: 2026-08-29 | Applies to: every tutorial-style note in this knowledge base
> Source: extracted from `ai/foundation/agentic-ai/001-agentic-ai-basics.md`

The structure below is the house style for long-form tutorials here. It was extracted from the
agentic AI tutorial, which is the reference implementation: when this document and that file
disagree, that file wins and this one should be corrected.

**How to use it:** copy everything between the `TEMPLATE STARTS` and `TEMPLATE ENDS` markers into a
new note, then fill it in and delete the `<!-- -->` guidance comments as you go. Those comments are
invisible in rendered Markdown, so a half-finished note still reads cleanly.

**What is mandatory:** the metadata block, Tutorial Overview, Table of Contents, the Part structure,
an `**Objective:**` on every teaching section, and the Appendix. Everything else is available when
the subject calls for it. A tutorial with no code has no hands-on track; a timeless topic needs no
version landmarks. Do not pad a note to fill the skeleton.

---

## The shape at a glance

| Region | Contains | Required |
| --- | --- | --- |
| Header | H1 title, metadata blockquote | Yes |
| Front matter | Tutorial Overview, Table of Contents | Yes |
| Part 1: Foundations | The concepts, in dependency order | Yes |
| Part 2: Landscape | The tools, frameworks, or variants in the field | When the topic has an ecosystem |
| Part 3: Putting It Into Practice | Decision guide, hands-on track, pitfalls | Yes, at least the pitfalls |
| Part 4: Reference | Learning path, cheatsheet | Yes, at least the cheatsheet |
| Appendix | Glossary, Sources, staleness note | Yes |

Two conventions hold across all of it:

- **Sections are numbered continuously across Parts.** Part 1 ends at section 8 and Part 2 opens at
  section 9. The numbers are stable anchors for cross-references like "re-read Section 2", which are
  used heavily and are the main thing that makes a 1000-line note navigable.
- **Parts are `#` (H1), sections are `##` (H2).** Multiple H1s in one file is deliberate: it makes
  Parts visually heavier than sections in every renderer, without needing a fourth heading level.

---

## Section-level patterns

Each teaching section follows the same internal rhythm.

**1. Objective line.** Every numbered section opens with `**Objective:**` and one sentence naming
what the reader will be able to do. It is a contract: if the body does not deliver it, one of the
two is wrong.

**2. Mental model first.** Lead with the shortest correct framing, usually as a blockquote:

> A chatbot *responds*; an agent *gets things done*.

**3. An analogy for anything hard.** The reference tutorial carries a detective-and-case-file
analogy for the agent loop and a small-office analogy for agent anatomy. Use one sustained analogy
per hard concept and map each element back to the real mechanism explicitly. Do not open a second
analogy for the same concept.

**4. Overview, then `### Details`.** State all items compactly first as a list or table, then expand
each under `### Details` with one `####` per item. A reader who only needs the map can stop after the
overview. Deep-dive headings take the form `#### <Thing>, in detail: <one-line hook>`.

**5. `### Real use cases`.** Concrete, numbered scenarios that give the *reason* the choice fits,
not just a label. Three per option is the working number.

**6. Self-check.** Foundational sections close with a question and its answer in parentheses:

`**Self-check:** ... (No: one prompt, one answer, no tools, no loop.)`

**7. Horizontal rule.** `---` between sections. It is the only visual separator used.

### Writing rules

- Comparison tables for anything with more than two competing options. Prose loses.
- Bold lead-ins on list items, so a list is scannable without being read.
- Every claim that has a cost gets its cost. A pattern without its trade-off is marketing.
- Date-stamp and version-stamp anything that will drift, then repeat the warning in the Appendix.
- Code blocks stay minimal and runnable in principle, and show expected output as a comment.
- Bad-then-good pairs beat abstract advice: show the failing version first, labelled `# Bad:`.

---

## TEMPLATE STARTS

~~~markdown
# <Topic>: Complete Tutorial

> Last updated: <YYYY-MM-DD> | Applicable to: <version, release, or "the field as of <date>">
> Difficulty: <Beginner | Intermediate | Advanced> | Estimated time: <reading time, plus optional hands-on time>

## Tutorial Overview

<!-- One paragraph: what this covers, with the key term in bold on first use. Name the specific
     things covered, so a reader can tell in five seconds whether this is the right document. -->

After completing this tutorial, you will be able to:

<!-- 4-6 bullets, each starting with a verb: Explain, Describe, Recognize, Choose, Build.
     These are the per-section Objective lines, aggregated. -->

- <outcome>
- <outcome>

**How to read it:** <which Parts are sequential, which are optional, which are reference>

---

## Table of Contents

<!-- Mirror the Part and section numbering exactly. Update this last, after the body is final. -->

- Part 1: Foundations
  - 1. <section>
  - 2. <section>
- Part 2: <The landscape>
  - 3. <section>
- Part 3: Putting It Into Practice
  - N. How to choose (decision guide)
  - N. Optional hands-on track: <goal>
  - N. Common misconceptions and pitfalls
- Part 4: Reference
  - N. Advanced topics and learning path
  - N. Cheatsheet
  - Appendix: Glossary and sources

---

# Part 1: Foundations

<!-- Concepts in dependency order. Nothing here may depend on Part 2. -->

## 1. <What is X?>

**Objective:** <one sentence: what the reader can do after this section>

<!-- Definition, with the term in bold on first use. -->

The one-sentence mental model:

> <shortest correct framing>

<!-- Properties or components as a table once there are three or more. -->

| <Property> | <Meaning> |
|---|---|
| **<name>** | <what it means> |

**Self-check:** <question> (<answer, with the reasoning in one clause>)

---

## 2. <X vs. Y vs. Z>

**Objective:** <one sentence>

<!-- The distinction section. Almost every topic has one comparison that matters more than the
     rest. Make it early and make it a table. -->

| | <Option A> | <Option B> | <Option C> |
|---|---|---|---|
| **<axis>** | <> | <> | <> |

### Real use cases per level

**<Option A>: appropriate when <condition>.**

1. *<Scenario>.* <Why this option fits, and what a heavier option would cost you.>

### <The same problem at all three levels: a worked comparison>

<!-- Optional but high value: take ONE concrete problem and show it solved at each level, then state
     the deciding factors in order. This turns a comparison table into a decision. -->

**The deciding factors, in order:** <factor, and which option it points to>

**Self-check:** <question> (<answer>)

---

## 3. <The core mechanism>

**Objective:** <one sentence>

<!-- The load-bearing section. Explain the mechanism before any tooling touches it. -->

**A real-life picture: <the analogy>.** <Sustained analogy, then map each element back:>

- **<Analogy element>.** <What it corresponds to in the real mechanism.>

### <Reading it, line by line>

### <A full trace, end to end>

<!-- A concrete worked trace. Readers trust a mechanism they have watched run once. -->

### <The failure guards> (never ship without them)

---

## 4. <Anatomy: the building blocks>

**Objective:** <one sentence>

<!-- Overview first: numbered bold blocks, one paragraph each. -->

**1. <Block> (<the metaphor role>).** <What it does.>

### Details

<!-- Open with the sustained framing, then one #### per block. Each answers: what it is, why it
     matters, and what trips beginners up. -->

#### <Block>, in detail

Three practical things to know as a beginner:

- **<Counterintuitive point>.** <Explanation.>

#### The anatomy at a glance

<!-- Summary table closing the section. -->

---

## 5. <Core patterns or variants>

**Objective:** <one sentence>

- **<Pattern>**: <one-line description>

### Details

<!-- Open by stating that these are not competing products but reusable answers, and that real
     systems combine them. Then one #### per pattern. -->

#### <Pattern>, in detail: <hook>

#### Choosing a pattern at a glance

| Pattern | Use when | Cost |
|---|---|---|

### Real use cases

#### <Named real system>: <the one-line characterization>

<!-- Real, named systems beat invented examples. Include one counter-example: something widely
     assumed to be in this category that is not. -->

---

## 6. Why <X> is hard (the honest part)

**Objective:** <one sentence>

<!-- Mandatory. Every tutorial has one, and it is the section that earns the reader's trust. Cover
     failure modes, the arithmetic of unreliability where it applies, and the costs the marketing
     leaves out. Give at least one hard number. -->

---

## 7. <Constraint or resource model>

## 8. <Cost estimation>

<!-- Where the topic has a budget dimension (tokens, money, latency, memory), give a worked example
     with real arithmetic. Show the formula, then run it on one realistic scenario end to end. -->

### Worked example: <forecasting a concrete case>

---

# Part 2: <The Landscape>

<!-- The ecosystem survey. Include this Part only when the topic has competing tools or variants.
     Version-stamp everything here; it is the Part that goes stale first. -->

## 9. The map: <N> lanes

<!-- Organize the field into a few lanes BEFORE naming any individual tool. Readers cannot hold
     fifteen framework names, but they can hold five categories. -->

## 10. <Tool>: <the one-line positioning> (<language or platform>)

<!-- Per tool: what it is, who it is for, what it costs you, and a flavor sketch of the code. Keep
     every entry the same shape so they can be compared by scanning. -->

```<language>
# Flavor sketch: <what this shows>
```

## <N>. Honorable mentions

<!-- One line each for things that exist but do not warrant a section. Heads off the "why didn't you
     mention X" reaction without bloating the Part. -->

---

# Part 3: Putting It Into Practice

## <N>. How to choose (decision guide)

| Your situation | Start with |
|---|---|
| <concrete situation> | **<choice>** |

<!-- Close with the practical truths that survive the churn: that concepts transfer between tools,
     or that the category moves fast enough that you should pin versions. -->

Two practical truths:

1. **<Truth>.** <Why it matters.>

---

## <N>. Optional hands-on track: <goal>

**Objective:** <one sentence> Project root: `<dir>/`.

<!-- Optional. Include only where the reader can actually run something. Every step must be
     independently verifiable: no step ends without the reader knowing whether it worked. -->

### Step 1: Set up the environment

```bash
# Requires <runtime and minimum version>
```

Verify the installation:

```bash
<verification command>
# Expected output: <what they should see>
```

### Step 2: <The mechanism, with no framework> (no API key needed)

<!-- Show the bare mechanism first, with a mock or stub so it runs offline and free. This is the
     step that teaches. The framework step only shows ergonomics. -->

```python
# Expected output:
# <exact expected lines>
```

### Step 3: The same thing, with a real framework

---

## <N>. Common misconceptions and pitfalls

<!-- Numbered pitfalls in Symptom / Cause / Fix form, each pointing back to the section that
     explains it properly. Include a security or safety pitfall where the topic has one, and one
     about the ecosystem breaking underneath you. -->

**Pitfall 1: "<the thing people wrongly believe>."**
Symptom: <what they observe>. Cause: <the real reason>. Fix: <the action>; re-read Section <N>.

---

# Part 4: Reference

## <N>. Advanced topics and learning path

**Recommended learning order:** <A> to <B> to <C>. <One line on why this order.>

**Direction 1: <Topic>** | Difficulty: <Intermediate | Advanced>
<What it covers.> Recommended resources: <named, specific resources>.

**Hands-on project suggestions:**

1. **<Project>**: <what it does>. Concepts: <which sections it exercises>.

**Best practices:**

- <Practice, phrased as an imperative.>

---

## <N>. Cheatsheet

<!-- Must stand alone. A reader who finished the tutorial should be able to return here six months
     later and recover the whole model without re-reading anything above. -->

**Definition:** <the one-sentence definition, repeated verbatim from Section 1>

```<language>
<the core mechanism in under ten lines>
```

**<Anatomy>:** <block> - <block> - <block>

**Key number:** <the one statistic that changes decisions>

**Version landmarks (as of <Month Year>):**

| <Thing> | Milestone |
|---|---|

**Quick troubleshooting:**

| Symptom | Likely cause | Quick fix |
|---|---|---|

---

## Appendix

### Glossary

<!-- Every bolded term introduced anywhere in the tutorial appears here, one line each, defined so
     the row stands alone without the surrounding section. -->

| Term | Definition |
|---|---|
| <Term> | <Definition> |

### Sources (as referenced in this tutorial)

<!-- Attributed and dated, in the form below, so a reader can tell which claim each source backs. -->

- <Publisher>, "<Title>" (<date>): <the specific claim it supports>

*Note: <the staleness warning>. Verify version-specific claims against official documentation before building on them.*
~~~

## TEMPLATE ENDS

---

## Pre-publish checklist

- [ ] Metadata blockquote present, with a real `Last updated` date and an `Applicable to` scope
- [ ] Every numbered section has an `**Objective:**` line, and the body delivers it
- [ ] Table of Contents matches the body headings and numbering exactly
- [ ] Section numbers run continuously across Parts, and every "see Section N" resolves
- [ ] The load-bearing mechanism is explained before any tool or framework is named
- [ ] There is an honest section on failure modes, carrying at least one hard number
- [ ] Every comparison with three or more options is a table, not prose
- [ ] Every code block is runnable in principle and shows its expected output
- [ ] Pitfalls are in Symptom / Cause / Fix form and link back to the explaining section
- [ ] The cheatsheet stands alone without the body
- [ ] Every bolded term in the body has a Glossary row
- [ ] Sources are dated and attributed to the specific claim they support
- [ ] The staleness note names the month and year the content reflects
