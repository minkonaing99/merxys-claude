---
name: md-to-epub
description: Convert a markdown or PDF book into a clean, readable EPUB — stripping images, copyright and publisher matter, rebuilding a real table of contents, repairing OCR damage, and adding a short recap to the end of every chapter. Use this whenever someone wants an .md or .pdf turned into an ebook, epub, or Kindle-readable book, wants a scanned or converted book cleaned up for reading, mentions a messy book dump with broken headings or scanner garbage, or asks to add chapter summaries to a book. Reach for it even if they only say "make this readable" or "turn this into an ebook" without naming EPUB.
---

# Book to EPUB

Turn a markdown or PDF book into an EPUB that is pleasant to actually read: no
images, no legal boilerplate, a working table of contents, repaired text, and a
short recap closing every chapter.

Books arrive in shapes the format cannot express. Heading levels collapse —
every heading lands on `##`, so chapter titles, subtitles, and copyright pages
become indistinguishable. Text gets corrupted, by OCR in the worst case and by
drop caps and lost hyphens even in the best. Both need judgment to undo, so this
workflow alternates between scripts (which measure and assemble) and model
passes (which decide).

## Pick the best source first

Do this before anything else, because it decides how much of the rest you have
to do. Look at what else sits in the folder: an `.md` and a `.pdf` of the same
book are common, and they are not equally good.

```bash
pdfinfo book.pdf | head -6      # Creator field
pdftotext -enc UTF-8 book.pdf - | head -40
```

**A PDF with a real text layer beats a markdown dump every time.** If the
Creator says calibre, InDesign, Word, LaTeX, or similar, the PDF was generated
from a digital original and carries the publisher's own characters. A markdown
file sitting next to it was usually OCR'd *from* that PDF, so it has all the
same content plus scanner damage the PDF never had.

The difference is not marginal. On one real book the OCR'd markdown needed 90
text repairs across 101 chapters; the PDF needed 20, all of them minor drop-cap
and hyphen artifacts. It also had 211 flat mangled headings where the PDF gave
99 clean numbered chapters for free.

Only prefer the markdown when the PDF is a scan of paper — no text layer, or
`pdftotext` output that is empty or garbled. Then the markdown's OCR already did
the work and redoing it gains nothing.

```bash
python3 scripts/frompdf.py book.pdf -o book.from-pdf.md
```

This reflows the hard-wrapped PDF text into paragraphs and marks chapters, then
the rest of the pipeline runs unchanged. Requires `pdftotext` (`brew install
poppler`).

`frompdf.py` handles two chapter-marker conventions and picks between them
automatically: a bare page number (`99` alone on its own line, as a
calibre-style export often does), or a word marker (`CHAPTER 1`,
`INTRODUCTION`) when no numbered pages turn up. The word-marker path reads
exact chapter titles from the book's own contents listing rather than guessing
from line length, because that layout tends to run the title straight into the
first subsection heading with no blank line to separate them — length alone
would merge the two. Note the listing sometimes spans more than one PDF page;
the parser already looks across a joined window rather than a single page, but
if a book still comes out with a `Chapter N` fallback title instead of the real
one, that is the symptom to check for.

It also strips two things mechanically, no judgment required: watermark lines
a piracy site stamps on every page (`OceanofPDF.com` and the like — anything
domain-shaped that repeats three or more times across the document), and drop
caps that extraction split off as their own line (`W` then, on the next line,
`hen I was twenty-six...`). Both are common enough on books sourced from the
open web that they are worth checking for even when the PDF looks otherwise
clean.

## Pipeline

```
frompdf.py        ->  book.md                 (PDF sources only)
parse.py analyze  ->  headings.json, flags.json, meta.json
   you classify   ->  structure.json          (what is a chapter, what gets cut)
   subagents      ->  repairs.jsonl           (text fixes, every edit logged)
   subagents      ->  recaps.json             (one recap per chapter)
build.py          ->  book.epub
verify.py         ->  structural check
```

Work in a `build/` directory next to the source file. Every intermediate is
plain JSON, so a failed phase is re-runnable without repeating the ones before it.

If you convert the same book twice from different sources, `recaps.json`
carries over untouched as long as the section ids match — the chapters are the
same text either way, so there is no reason to pay for them again.

## Phase 0 — Measure

```bash
python3 scripts/parse.py analyze "book.md" --out build
```

Read the printed `meta.json` before going further. It tells you what kind of
document you have:

- `heading_levels` all `2` — the flat-heading problem. Phase 1 is doing real work.
- `flag_ratio` above ~0.10 — the damage detector is firing on style rather than
  scanner noise. Raise `--garble-ratio` and rerun; repairing 300 paragraphs that
  were never broken wastes tokens and invites the model to "fix" good prose.
- `unbalanced_fences` true — a stray ``` is swallowing text. `build.py` drops
  fenced content, so check what is inside before it silently vanishes.

## Phase 1 — Classify the structure

Read `build/headings.json`. It has one record per heading with the fields you
need to judge it: `text`, `line`, `body_lines`, `body_chars`, `all_caps`,
`first_body_line`. Classify **all** headings in a single pass and write
`build/structure.json`.

Do it in one pass rather than sampling. A few hundred heading records is only a
few thousand tokens, and the errors that matter are the ones a rule would never
flag as uncertain.

### Look for the original contents listing first

Before classifying anything by eye, check whether the book still carries its own
table of contents — usually a heading called `Contents` near the front, holding
what looks like one long unreadable paragraph.

That blob is the highest-value object in the file. It survives conversion as
prose, but it still lists every chapter in order with its correct title and
subtitle, which makes it ground truth for the whole book. Parse it into a
numbered list and match those entries against the headings.

The payoff is that it resolves the traps below without guesswork. When the blob
says `31: How to Relieve People of Their Millions: Induction` and the headings
read `## How to Relieve of Their Millions` followed by `## People`, the merge and
the missing word are both settled facts rather than judgment calls. It also
gives you an exact chapter count to reconcile against, which is how you notice a
chapter whose heading was demoted to plain text and would otherwise vanish
silently into the chapter above it.

Expect a handful of entries not to match automatically — the blob is OCR'd too.
Match what you can mechanically, then resolve the leftovers by hand. That is a
few explicit cases, not a few hundred.

```json
{
  "title": "The Art of Thinking Clearly",
  "creators": ["Rolf Dobelli", "Nicky Griffin (translator)"],
  "language": "en",
  "sections": [
    {
      "id": "ch01",
      "role": "chapter",
      "number": 1,
      "title": "Why You Should Visit Cemeteries",
      "subtitle": "Survivorship Bias",
      "start_line": 106,
      "end_line": 124
    },
    { "id": "drop-copyright", "role": "drop", "title": "Copyright",
      "start_line": 17, "end_line": 60 }
  ]
}
```

- `role` is `chapter` (goes in the book) or `drop` (does not). Everything must be
  assigned one so the totals reconcile.
- `number` is the chapter number, or `null` for unnumbered matter you keep, like
  an Introduction or Epilogue.
- `start_line` is the line **after** the heading; `end_line` is the last line
  before the next heading. `build.py` renders the title from `title`, so leaving
  the heading line in produces a duplicate.
- Sections must not overlap, and together they should account for the whole file.

### What to cut

Remove copyright pages, publisher and printing data, ISBN and cataloging blocks,
marketing blurbs, credits, and the book's *original* contents listing — that last
one always survives conversion as an unreadable run-on paragraph, and this
workflow builds a real one to replace it.

Ask before cutting anything with authorial content: dedications,
acknowledgments, epilogues, appendices, and endnotes are judgment calls, not
boilerplate. When the user has already said what they want cut, follow it.

### Traps in flat-heading books

These are the failure patterns that make a mechanical rule produce a broken book.
Watch `headings.json` for each:

**Split titles.** OCR breaks one title across two headings. `## Mission` followed
by `## Accomplished`, or `## How to Relieve of Their Millions` followed by
`## People` — where the stranded word belongs *inside* the previous title, not
after it. Signature: a heading with very few `body_lines` immediately followed
by another heading. Merge them into one `chapter` and repair the wording.

**Promoted subtitles.** A chapter's subtitle got its own `##`. `## Sweet Little
Lies` then `## Cognitive Dissonance` is one chapter, not two. Signature: same
tiny-body pattern, but the second heading names a concept rather than continuing
a sentence. Fold it into the `subtitle` field.

**Back matter that mimics chapters.** Endnote and source sections repeat every
chapter's title as a heading, often in caps. Signature: `all_caps` true, or
headings whose titles duplicate ones seen earlier, clustered at the end of the
file. These are references, not chapters.

Repair damaged heading text as you classify — you are already reading every
title, so it costs nothing extra and titles are the most visible text in the book.

### Chapters with internal subsection headings

Not every book gives each chapter a one-line subtitle. Some — memoirs,
business nonfiction, anything with a handful of long chapters instead of a
hundred short ones — mark internal sections within a chapter instead (`Life Is
Poker, Not Chess` opens straight into `Pete Carroll and the Monday Morning
Quarterbacks`, its first subsection, with no separating punctuation). Setting
`subtitle: null` for these is correct. Leave the subsection headings inside the
chapter body as plain text rather than inventing a subtitle field for them or
promoting them to their own `##` sections — `reflow()` in `frompdf.py` already
isolates a short heading-like line into its own paragraph, which reads fine as
a lightweight section break without any extra markup.

### Corrupted scene-break dividers

Essay-collection and aphorism books (short reflections, no continuous
argument) typically use a small typographic mark — an asterisk, a bullet, a
short rule — between unrelated passages within a section. OCR and PDF-to-text
extraction reliably mangles this mark, because it is usually a decorative
glyph rather than a real character. It shows up as a standalone one-to-few-
character line sitting alone between blank lines: Myanmar-range Unicode
gibberish (`ရှ`, `ငှ`), a stray `VJ` paired with a bare `*`, or just a solitary
`V`. It is never real text, and the paragraphs on either side of it are always
unrelated in topic — that combination is the signature.

Collapse every occurrence of the pattern to a single `***` line, mechanically,
across the whole file:

```python
divider_re = re.compile(r'^[က-႟\s]{1,6}$')  # extend per-book if the OCR
                                              # produces a different glyph run
```

Walk the file collecting runs of consecutive lines that are each a divider
token (blank lines bridging two tokens count as part of the same run), and
replace the whole run with one `***`. A book like this can carry dozens of
occurrences — one for nearly every short passage — so do this once
programmatically rather than fixing them one at a time.

`build.py` treats a bare `***` (or `---`, `* * *`) as a scene break and drops
it to a plain paragraph gap — no visible rule is rendered by default. This
was a real design call, not an oversight: a lone scene break every few pages
reads fine as a horizontal rule, but a book with dozens of them turns a
visible `<hr/>` into wall-to-wall clutter, which is exactly what a reader
flagged after the first pass through this pattern rendered every collapsed
divider as a line. If a specific book only has two or three scene breaks
total, a visible rule is a reasonable manual choice — but that is an
exception to opt into, not the shipped default.

If line numbers matter downstream (they always do — `structure.json` is
line-indexed), rebuild `headings.json` and `structure.json` after collapsing
dividers, since removing text changes every line number after the edit.

## Phase 2 — Repair flagged prose

`build/flags.json` holds only paragraphs carrying damage signals, typically a few
percent of the book. Repairing just these keeps cost proportional to the damage
and keeps the rest of the text untouched.

Split the flagged paragraphs into batches of roughly 15 and dispatch a subagent
per batch. See `references/agent-briefs.md` for the exact brief — it is written
to be copied.

Each subagent appends to `build/repairs.jsonl`, one JSON object per line:

```json
{"line": 87, "signals": ["ocr_confusion"], "before": "Tn the fall of 2004, a European media mogul", "after": "In the fall of 2004, a European media mogul"}
```

`before` must be copied byte-for-byte from the source or `build.py` cannot match
it and will report the repair as skipped. Omit the record entirely when a
paragraph is fine — plenty of flags are false positives, and forcing an edit is
how correct sentences get rewritten.

Have each subagent write its own file, then combine them:

```bash
python3 scripts/merge.py repairs build/repairs-*.jsonl -o build/repairs.jsonl
```

This drops no-op and duplicate records and rejects malformed lines, which
matters because parallel agents appending to one shared file interleave badly.

Expect to run this phase twice. Reading the chapters surfaces damage the
detector missed, and the recap agents in phase 3 will report specific broken
passages as a side effect of reading every chapter closely. Treat those reports
as a second flag list: collect them, add the pattern to `parse.py` if it
generalizes, rerun `analyze`, and repair whatever is newly flagged.

This phase edits a real author's words. `repairs.jsonl` is the entire audit
trail, so tell the user it exists and keep it beside the output.

### Damage the detector looks for

Worth knowing so you can recognize a report as real rather than noise:
misread letters (`Tn`/`Th` for `In`), italic lowercase L scanned as a slash
(`i//usion`, `/oss aversion`), pipe or bracket for capital I (`| have`,
`] doubt`), contractions split by a space (`you' ll`), non-Latin glyphs standing
in for an apostrophe (`swimmer ၆ body`), fused words that lost a space or
hyphen (`froma`, `socalled`, `baserate`), and drop caps that came out as their
own letter (`T he contrast`, `K evin has`).

Drop caps are the one class a PDF source still suffers from, and they are
reported with a `start:` prefix when the split sits at the beginning of a
paragraph. That prefix is worth trusting: a paragraph-initial capital is nearly
always a drop cap, while the same pattern mid-sentence is almost always an
option label (`Option B offers`, `Group B heard`, `disease X or Y`) that must be
left alone. Repairing paragraph-initial ones can be done mechanically.

That last one is the most common and the hardest to detect, because a
dictionary alone cannot tell `withdomain` (damage) from `willpower` (a real
compound the dictionary lacks). The script resolves it by checking whether the
book writes that same word pair correctly somewhere else — the document is its
own authority on which compounds it actually uses. Expect a handful of benign
survivors like `anymore` or `bestseller`; skipping those is the correct call.

If a repair agent needs to settle an ambiguous compound — hyphenated or open,
`time-travel` versus `time travel` — a quick web search against the published
text beats guessing. Confirming beats inventing; just don't let it turn into a
research detour for every borderline case.

## Phase 3 — Write the recaps

```bash
python3 scripts/parse.py slice "book.md" build/structure.json --out build/chapters
```

This writes one text file per section. Dispatch subagents over batches of 5-8
chapters; the brief is in `references/agent-briefs.md`.

Each recap is 2-3 sentences of plain prose that name the idea, state the
mechanism, and land the practical takeaway. Results merge into
`build/recaps.json` keyed by section `id`:

```json
{ "ch01": "Survivorship bias makes success look far more probable than it is..." }
```

```bash
python3 scripts/merge.py recaps build/recaps-*.json \
    -o build/recaps.json -s build/structure.json
```

The merge reconciles against `structure.json` and reports any chapter left
without a recap, any id matching no chapter, and anything short enough to be a
truncated response. Rerun only the batches it names.

Give every subagent the same brief, and include two or three finished recaps from
earlier batches as examples once you have them. A hundred recaps written by
separate agents will drift in voice otherwise, and inconsistency is more
noticeable to a reader than any single mediocre recap.

Recaps go at the end of chapters, after the argument has landed. Putting them up
front spoils books whose chapters are built around a turn.

## Phase 4 — Build

```bash
python3 scripts/build.py "book.md" build/structure.json -o "book.epub" \
    --recaps build/recaps.json --repairs build/repairs.jsonl
```

`--recaps` and `--repairs` are optional, so you can build a structurally correct
EPUB early to check the shape before spending tokens on phases 2 and 3.

The script handles image stripping, whitespace collapsing, hyphen rejoining,
fence removal, markdown-to-XHTML, an SVG cover generated from title and author,
an EPUB 3 `nav.xhtml` with an EPUB 2 `toc.ncx` alongside it for older readers,
and the stylesheet. It also strips orphaned footnote-reference asterisks
automatically — dropping the Notes/endnotes section (see "What to cut" above)
leaves a bare `*` dangling after whatever word it used to annotate, and that is
mechanical cleanup, not a judgment call, so it happens for every book rather
than needing a manual pass each time.

The CSS deliberately sets no font family, size, or color. Readers choose those,
often for accessibility, and an ebook that overrides them reads worse on the
device it actually gets opened on.

## Verify before handing it over

Check the reported counts first: chapter count should match what you classified,
and `recaps: N/N` should be complete. Then confirm the file is well-formed:

```bash
python3 scripts/verify.py "book.epub"
```

Beyond the structural checks, this re-runs the phase 2 damage detectors against
the finished, repaired book and reports what still turns up. It exists because
every real conversion so far has surfaced at least one gap the detector missed
the first time around — a fused word too short for the tail-length check, a
drop cap outside a chapter opening, an orphaned footnote marker — and finding
those during review is a lot cheaper than a reader finding them. A handful of
hits is normal (an `Option B offers` split-capital, a genuine `and/or` slash)
and not worth chasing; skim the list, and treat a signal that keeps showing up
across many paragraphs as the real thing.

Report to the user: chapter count, what was cut, how many repairs were applied,
and where `repairs.jsonl` sits so they can audit the text edits.

## Reference

- `references/agent-briefs.md` — copy-ready briefs for the repair and recap
  subagents, plus the recap style spec that keeps voice consistent.
