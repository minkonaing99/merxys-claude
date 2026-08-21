# Subagent briefs

Copy-ready prompts for phases 2 and 3. Both phases fan out across batches, and
batches drift when each agent invents its own standard — so send every agent the
same brief, and paste finished examples from earlier batches into later ones.

## Repair brief (phase 2)

Fill in the batch and paths, then send as the subagent prompt.

> You are repairing OCR damage in a book that was converted from PDF to
> markdown. Below are paragraphs a detector flagged as possibly damaged.
>
> The detector is deliberately noisy — a large share of these paragraphs are
> perfectly fine. Your job is to fix genuine scanner corruption and leave
> everything else exactly as it is.
>
> **Repair these:**
> - Letters misread by the scanner: `Tn the fall` for `In the fall`, `rnay` for
>   `may`, `0f` for `of`.
> - Contractions split by a stray space: `you' ll`, `you' ve`, `It' 11`.
> - Words fused or broken across a line: `self-  navigating`.
> - Non-Latin glyphs dropped into English text: `The Art of ဥု Clearly`,
>   `swimmer၆s body`. Restore the character that was clearly meant.
> - A word obviously dropped where the sentence cannot parse:
>   `a Wrong Map to at All` is missing `No Map`.
> - A capital letter sheared off the first word of a paragraph by a drop-cap
>   glitch: `T he contrast effect` at the very start of a paragraph is `The
>   contrast effect`. The same pattern mid-sentence (`Option B offers`, `Group B
>   heard`, `disease X or Y`) is an option label, not damage — leave it.
> - Fused words that lost their space or hyphen: `longterm` for `long-term`,
>   `decisionmaking` for `decision-making`. If the correct form is genuinely
>   unclear (open compound vs. hyphenated), a quick web search against the
>   published text beats guessing — but don't turn every borderline case into a
>   research detour.
>
> **Leave these alone:**
> - Anything you would merely phrase differently. This is a published author's
>   text, not a draft to improve.
> - British spelling, archaic usage, unusual but real words, technical terms,
>   and proper nouns you do not recognize. Researchers' names set off most false
>   positives here.
> - Plural possessives (`swimmers' bodies`, `years' time`) and single quotation
>   marks. These trip the detector constantly and are correct.
> - Long or unconventional sentences. Style is not damage.
>
> If you cannot tell what the original word was, leave the paragraph out rather
> than guessing. A missing repair is recoverable; an invented sentence silently
> misattributed to the author is not.
>
> Append one JSON object per repaired paragraph to `build/repairs.jsonl`, one per
> line, creating the file if needed:
>
> ```json
> {"line": 87, "signals": ["ocr_confusion"], "before": "<exact original text>", "after": "<repaired text>"}
> ```
>
> `before` must be copied byte-for-byte from the paragraph as given, including
> punctuation and internal newlines — it is matched literally against the source
> and a paraphrase will silently fail to apply. Change only the damaged span;
> the rest of `after` should be identical to `before`.
>
> Write nothing for paragraphs that need no repair. Reply with the count you
> repaired and the count you skipped.
>
> Paragraphs:
> {paste the batch from build/flags.json here}

## Recap brief (phase 3)

> You are writing end-of-chapter recaps for an EPUB edition of a book. Read each
> chapter file listed below and write one recap per chapter.
>
> **Each recap is 2-3 sentences of plain prose.** Name the idea, state the
> mechanism that makes it work, and land the practical takeaway. It should let a
> reader who finished the chapter a month ago recall it in one glance.
>
> Write in the register of the book itself — a thoughtful writer summarizing
> their own argument. Not a textbook, not a study guide, not a listicle.
>
> - No bullet points, no headers, no bold. Prose only.
> - Do not open with "This chapter..." or "In this chapter...". The reader knows
>   what they just read. Go straight to the idea.
> - Use the book's own terms for its concepts rather than inventing new labels.
> - Do not add advice, caveats, or examples the chapter does not contain.
> - Do not end every recap with the same rhetorical shape. Identical rhythm
>   across a hundred chapters reads as machine-generated.
>
> Return strict JSON mapping section id to recap text, nothing else:
>
> ```json
> {"ch01": "Survivorship bias makes success look far more probable than it is, because the failures leave no trace to count. Every visible winner sits atop a silent pile of identical attempts that went nowhere. Before drawing a lesson from a success story, go looking for the graveyard."}
> ```
>
> Chapters to summarize:
> {list section ids and file paths from build/chapters/index.json}
>
> Recaps already written for this book, to match in voice and length:
> {paste 2-3 finished recaps from earlier batches, or omit for the first batch}

## Merging results

Repair agents append to a shared `repairs.jsonl` concurrently, so re-read the
file once all batches finish and confirm each line parses. Recap agents return
JSON — merge the objects into a single `build/recaps.json` and check that every
`chapter` id in `structure.json` has a key before building.
