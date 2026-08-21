---
name: lecture-to-summary
description: Turn one lecture folder in the Mahidol Obsidian vault into a study-ready summary.md by fusing the slide PDF, class transcript, and the user's raw notes.md. Use whenever the user points at a lecture folder (e.g. courses/<code>-.../lectures/lecture_N/) or says things like "summarize this lecture", "make a study doc for lecture 2", "turn my transcript + slides into notes", "what do I need to know from this lecture", "pull the deadlines out of this lecture", or drops a transcript/slide set from a class and wants it distilled. Also trigger when the user has just transcribed a class recording and wants it written up alongside the slides. This produces a study doc (TL;DR, deadlines, key concepts, what you need to know, open questions, source map, plus a dedicated Assignment section when the lecture sets one) AND a single self-contained lecture.html the user can learn from without reopening the slides, both written in the user's own voice, and syncs any deadlines into the course index.
---

# Lecture to Summary

Turn a single lecture folder into `summary.md`: a tight, study-ready distillation that fuses everything the user has for that class (slides, transcript, their own scrappy notes) so they rarely need to reopen the slides. Also lift any deadlines up into the course-level index so all due dates live in one place.

The user is doing an MSc and studying for real. The goal is a doc they trust: complete enough to revise from, honest about what's uncertain, and traceable back to the source so they can dig deeper when a point matters.

## When this runs

The user points at one lecture folder, typically `courses/<code>-<name>/lectures/lecture_N/`. If they were vaguer ("summarize lecture 2"), find the matching folder before starting. Operate on exactly one lecture folder per run.

## Step 1: Gather the inputs

Read everything in the lecture folder:

- **Transcript** — the `.txt` file (plain prose, no timestamps). This is the spoken lecture: the richest source for emphasis, examples, and anything the professor said but didn't put on a slide (deadlines, "this matters for your thesis", warnings).
- **Slides** — PDF(s) whose name matches the course code or says "Lecture"/"slides". Read with the Read tool's `pages` param; note page numbers as you go so you can cite them.
- **Raw notes** — `notes.md`, the user's own hand-typed notes. Treat as high-signal: whatever they bothered to write down mattered to them, even if terse or typo'd. Never edit or overwrite this file.
- **Supplementary PDFs** — any other PDF (e.g. a research paper with a different course code) is background reading, not the lecture itself. Skim it, use it only to clarify a concept, and label it as supplementary in the Source map. Don't let it dominate the summary.

Ignore the course-level `materials/` folder unless the user explicitly points you there — it drifts from what was actually taught in this session.

If a source is missing (no transcript, or no slides), just work from what exists and note the gap rather than stalling.

## Step 2: Check before overwriting

This skill generates two files, `summary.md` and `lecture.html`. Both are its own output and normally safe to regenerate. But the user may have hand-edited either. Before overwriting one that already exists, read it and look for signs of manual work: added prose outside the expected sections, extra sections, inline commentary, reworded bullets. If it looks like a clean prior generation, overwrite it. If it looks hand-edited, stop and ask whether to overwrite, keep, or merge. Losing the user's own edits is far worse than an extra question. Never touch `notes.md`.

## Step 3: Write summary.md

Write in the user's own voice. Invoke the `my-writing-tone` skill and write the prose (TL;DR, definitions, the assignment write-up, anything in sentences) in that voice, and strip AI-writing tells before saving. This is the user's personal study doc — it should read like they wrote it, not like a generic AI summary. Bullet fragments and `term — definition` lines can stay terse; the tone matters most in the flowing prose.

Write to `lecture_N/summary.md`. Start with the vault's file convention so it fits the Obsidian graph:

```markdown
---
tags:
  - mahidol
---
# Lecture N — <short title>

> [[index]]
```

Then these sections, in this order. Six are always present; the **Assignment** section appears only when the lecture actually sets or discusses an assignment. Keep the whole thing to roughly one screen — study-ready medium depth. Cut logistics chatter (screen-sharing fumbles, greetings, "can you hear me"). Keep substance.

### 1. TL;DR
2-4 sentences. What this lecture was actually about and why it matters for the course. If someone read only this, they'd know whether they need to read the rest.

### 2. Deadlines & action items
A markdown checklist. Everything the user has to *do*: assignments, due dates, "next class is onsite", "bring X". Pull dates from wherever they appear (transcript often has the real date; notes may have a rougher version) and reconcile them. Format:

```markdown
- [ ] Assignment 1 — due 2026-08-21 23:59
- [ ] Next class onsite — Sat 2026-08-22
```

Use ISO dates (`YYYY-MM-DD`) when the year is known. If a date is spoken ambiguously ("the 21st, I think"), pick the most likely value and flag the uncertainty. If there are no deadlines, write `- None this lecture.`

### 3. Assignment
Include this section **only if the lecture actually sets or explains an assignment** (a task to hand in). Skip it entirely otherwise — don't emit an empty heading.

When present, give the user everything they need to start the assignment without reopening the slides or transcript: what to produce, the exact requirements and format, any template or structure the professor specified, worked examples he gave, constraints (allowed tools, length, topic restrictions), and how it will be assessed or used later (e.g. "this feeds your final presentation"). Keep the due date in the Deadlines checklist above; this section is the *what and how*, not the *when*. Pull details from wherever they live — the assignment slide, what the professor said out loud (often stricter or clearer than the slide), and the user's notes.

### 4. Key concepts
The must-know terms and ideas, each as `**term** — short definition`, with a concrete example from the lecture where one was given (examples are what make concepts stick). This is the core of the doc. Favour the concepts the professor dwelt on or the user noted, not every term mentioned in passing.

### 5. What you need to know
The exam/thesis-relevant takeaways — the stuff that will actually be assessed or that the professor flagged as important ("this matters for your independent study", grading breakdowns, expectations, methodology steps to follow). This is distinct from Key concepts: concepts are *what things mean*, this is *what you're accountable for*.

### 6. Open questions / gaps
Honest uncertainty: things left unclear in the lecture, questions the user should ask, gaps between the slides and what was said, or topics deferred to a later class. Don't invent these — if the lecture was clear and complete, a short list or "None" is fine. This section keeps the doc trustworthy.

### 7. Source map
For each substantive point in the doc, note which source backs it, so the user can trace and dig deeper. Tag with `[slides p.N]`, `[transcript]`, `[notes]`, or `[supplementary: <filename>]`. A point can have multiple tags. Keep it compact — a bulleted list mapping claim → source, not a re-listing of every sentence.

See `references/example-summary.md` for a filled-in example.

## Step 4: Build the lecture HTML

Also write `lecture_N/lecture.html`: a single self-contained page the user can read to learn the whole lecture without ever reopening the slide PDF. Where `summary.md` is the quick-revision distillation, this is the full teaching version: the slides expanded back into explained prose using what the professor actually said.

**Content model.** Walk the slides in order. For each slide (or small group of related slides), write a section that fuses the slide's own content with the matching spoken explanation from the transcript. Terse slide bullets get expanded into clear paragraphs; every concrete example, analogy, and aside the professor gave in the transcript gets woven in where it belongs. The goal is that reading top to bottom replaces both watching the recording and reading the deck. Keep the slide order so it still maps to the deck if the user ever cross-references. Write the teaching prose in the user's voice via the `my-writing-tone` skill.

**Design.** This is a page the user reads for hours, so its craft matters. Invoke the `taste-skill` for overall visual direction and layout judgment, and `emil-design-eng` for the fine details: typography, spacing rhythm, restraint, and the small touches that make a reading surface feel considered. Let those skills drive the look; the requirements below are the hard constraints they must stay inside.

**Technical requirements.** One file, fully self-contained, because the vault syncs over iCloud and must open offline:
- All CSS inline in a single `<style>` block. No external stylesheets, no CDN, no web fonts, no JavaScript frameworks. A small amount of vanilla `<script>` is fine only if it genuinely helps learning (e.g. a table-of-contents scroll); don't add it for decoration.
- Use a system font stack, generous line-height, and a light comfortable background. This is for long reading, so optimize for that. Constrain the content column to a max width of 80% of the viewport, horizontally centered.
- Start with the lecture title and an in-page table of contents linking to each section (anchor links).
- Use real semantic structure: `<h1>`/`<h2>`, `<p>`, `<ul>`, `<blockquote>` for the professor's direct quotes. Callout boxes for the important rules, deadlines, and the assignment are welcome, done with inline-styled `<div>`s.
- No external images. If a slide was purely a diagram or photo, describe it in words rather than linking a file.

Keep it genuinely useful, not padded. It can be longer than `summary.md` since it's the learn-from-it version, but every section should teach something, not restate a slide title.

## Step 5: Sync deadlines to the course index

The course `index.md` is one level up from `lectures/` (e.g. `courses/<code>-.../index.md`). It's the single place the user checks for all course due dates.

Take the deadlines you found and upsert them into a `## Deadlines` section there:

- If no `## Deadlines` section exists, add one (after the course metadata bullets, before any other section).
- Each deadline is one checklist line, same format as in the summary, tagged with the lecture it came from so it's traceable:
  ```markdown
  ## Deadlines
  - [ ] Assignment 1 — due 2026-08-21 23:59 (lecture 1)
  - [ ] Final report — due 2026-12-07 (lecture 1)
  ```
- **Dedupe on re-run.** Match on the item + date. If the same deadline is already there, leave it. If the date changed, update it. Don't create duplicates. Preserve any deadlines from other lectures and any the user checked off (`- [x]`).
- Only add real due dates and required actions. Don't push vague "read more about X" items up to the index.

## Working principles

- **Fuse, don't concatenate.** The value is one coherent picture from three overlapping sources, not three summaries stapled together. When the transcript and notes say the same thing, merge them; when the notes add something not on the slides, keep it.
- **The transcript carries the deadlines and the emphasis.** Slides give structure; the spoken track gives what actually matters and what's due. Read the transcript carefully for both.
- **Trust the user's notes.** They were in the room. A terse line in `notes.md` often marks the single most important thing in the lecture.
- **Be honest.** A trustworthy doc with an "Open questions" section beats a falsely complete one. Don't paper over gaps.
