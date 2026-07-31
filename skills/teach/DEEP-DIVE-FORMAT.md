# DEEP-DIVE-FORMAT.md Format

A **deep dive** is the long-form teaching layer: the document a user studies from to genuinely master a unit and be tested on it (exams, interviews, certification, real competence). It complements, and does not replace, the interactive lesson and the one-page reference. Build one per **unit**, and one per **synthesis topic** (a cross-cutting theme that ties several units together).

Deep dives live in `./deep-dive/` and are titled `NN-<dash-case-name>.html`, where `NN` matches the unit number (so `deep-dive/03-*.html` pairs with `reference/03-*.html` and the unit's lesson).

## When to build one

- The mission is mastery, top grades, certification, or an interview.
- The user says the material feels "too thin," or asks to "go deeper," "add more," or "know more."
- The topic is knowledge-dense (law, medicine, theory, standards) where understanding *why* matters as much as doing.

Skip or defer deep dives only when the user explicitly wants surface familiarity. Record the chosen depth in `NOTES.md`.

## Structure

```
[eyebrow: course/topic · unit N]
[H1 title]  ·  [italic standfirst: what this doc is for]  ·  [reading time]

[Table of contents — the sections below, linked]

1. Framing        — why this unit matters, what the exam/practice tests
2. Core teaching  — several sections of full narrative prose, building up the concepts
   worked examples embedded throughout (fully solved, every step shown)
3. Nuance/edge    — the subtleties that separate strong answers from average ones
4. Common mistakes — a wrong vs right table targeting the exact errors this topic punishes
5. Exam long-answer bank — model answers to essay/calculation questions, tagged by mark weight
6. Extended glossary — the unit's canonical terms (consistent with GLOSSARY.md)
7. Sources        — citations, drawn from RESOURCES.md
```

## Rules

- **Teach in full prose, not fragments.** Explain the reasoning and the *why*. A reader should be able to write an exam essay from this document. This is the one place in the workspace where length is a feature, not a bug.
- **Many worked examples, fully solved.** For quantitative topics, show every step and deliberately vary which value is hidden (solve forward, solve backward). For conceptual topics, use concrete worked scenarios.
- **A common-mistakes table is mandatory.** Two columns, wrong vs right, aimed at the specific misconceptions the topic's exams exploit. This is high-value and hard to get elsewhere.
- **An exam long-answer bank is mandatory.** Provide model answers to the kinds of questions the user will face, tagged with mark weight, so they learn the *structure* of a good answer, not just facts.
- **Cite every claim.** Draw citations from `RESOURCES.md`. If you assert a number, a standard, or a rule, name the source. Never trust parametric memory for a deep dive.
- **Adhere to the glossary.** Terminology must match `GLOSSARY.md`; the deep dive's extended glossary expands it, never contradicts it.
- **Beautiful and print-friendly.** Same design system as the lessons and references (shared tokens, restrained palette, per-topic accent). It must print cleanly, users print deep dives to study. No animation unless the user asks.
- **Pair it explicitly.** Reference the matching lesson and reference in the footer so the three layers stay linked.
- **One unit per document.** Do not merge units. Cross-cutting themes get their own *synthesis* deep dive instead.

## Relationship to the other layers

| Layer | File | Purpose | Length |
| --- | --- | --- | --- |
| Deep dive | `deep-dive/NN-*.html` | Learn deeply, prep for exams | Long |
| Lesson | `lessons/NNNN-*.html` | Test yourself (interactive drill + exercise) | Short |
| Reference | `reference/NN-*.html` | Revise fast | One page |

Build the deep dive first when teaching a new unit for a mastery goal, then the lesson to test it, then the reference to compress it. Retrofit deep dives onto earlier units when the user raises the depth bar mid-course.
