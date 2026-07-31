---
name: inspiro-save
description: Save a design/UI inspiration photo into the local Inspiro gallery at /Users/aurora/Documents/structure/03_projects/templates/inspiro. Use this whenever the user pastes or references a screenshot, mockup, landing page, portfolio, dashboard, or any UI/design photo and asks to save it, add it to inspiro, add it to the gallery, log it as inspiration, or invokes "/inspiro-save" or "inspiro". Also trigger on phrasing like "save this one", "add this to my inspiration", "do this one" when a design image was just shared and Inspiro has been used in the conversation before. The skill looks at the image directly, writes a structured JSON entry (design-system-style breakdown of layout/components/styling, tags, style notes, hex color palette), copies the photo into the gallery's photos folder, and appends it to data.js — never overwriting prior entries.
---

# Inspiro Save

Capture one design/UI inspiration photo into the local Inspiro gallery so it can be browsed later and reused as reference for vibe-coding frontend projects.

Project root (exact, always use this path): `/Users/aurora/Documents/structure/03_projects/templates/inspiro`

- Photos live in: `/Users/aurora/Documents/structure/03_projects/templates/inspiro/photos/`
- Entries live in: `/Users/aurora/Documents/structure/03_projects/templates/inspiro/data.js` (`const DATA = [ {...}, {...} ];`)
- Viewer: `/Users/aurora/Documents/structure/03_projects/templates/inspiro/index.html` (static, no server, no build step — the user opens it directly in a browser)

If the project root doesn't exist yet, this skill has drifted from what was originally scaffolded — stop and tell the user, don't recreate the whole project from scratch.

## Why this shape

The user is the only consumer of this gallery. There's no upload UI and no vision API call — you already see the image directly in the conversation, so use that instead of round-tripping through another model. Write every entry like a graphic designer reverse-engineering the file, not like someone describing a photo to a blind person. The point of the gallery is reuse for vibe-coding: months later, the user should be able to read one entry and rebuild the *system* (layout, components, styling rules, how pieces connect) in a real frontend, without needing to look at the photo again. Literal contents (exact copy text, company names, photo subject matter) are the least valuable part and fade fast — skip or compress them. Structure, spacing logic, and component relationships are what's worth stealing, and those don't decay.

## Steps

### 1. Find the source photo

The image is either pasted inline in the conversation (it will usually show a `source:` path underneath it) or referenced by an explicit file path the user gives you. Use that path directly — don't ask the user to move or rename the file first.

### 2. Work out the next id

Ids are `YYYY-MM-DD-NNN` where `NNN` is a zero-padded sequence number that resets per day, based on what's *already in `data.js`* — not how many photos exist elsewhere.

- Get today's date (`YYYY-MM-DD`).
- Read `data.js`. If it doesn't exist, treat it as `const DATA = [];`.
- Find existing ids starting with today's date prefix, take the highest `NNN`, add 1. If none, start at `001`.

### 3. Copy the photo

Copy the source file into `photos/` as `<id>.<original-extension>` (keep the original extension — jpg stays jpg, png stays png). Don't re-encode or resize it.

### 4. Look at the image and write the entry

Look at the image like you're about to rebuild it in code, not like you're captioning it for someone who can't see it. Read the layout (grid, sections, columns, spacing rhythm), the component inventory (what kinds of cards/buttons/nav patterns exist and how many variants), the visual system (type scale, corner radius, shadow/elevation depth, border treatment), and how pieces relate to each other (what's nested in what, what repeats, what anchors what). Write these fields:

- **description** — a design-system breakdown, not a scene description. Cover: page structure top to bottom (section order and what each section's layout is — e.g. "2-column split, sidebar fixed-width left, content fluid right"), component patterns and their anatomy (e.g. "card: rounded-xl, icon badge top-left, title, 1-line description, arrow affordance bottom-right — repeats 4x in a row"), how sections connect visually (shared background, overlapping elements, consistent card shape reused across different content), spacing/alignment logic (edge-to-edge vs contained, gutter width relative to content), type hierarchy (how many distinct text sizes/weights and where each is used), and color usage as a system (which color marks primary action vs which marks accent/status, not just "there's some blue"). Skip literal copy text, specific numbers, brand/company names, and photographic subject matter unless the content itself is structurally load-bearing (e.g. a stat row's presence matters, the exact stat value doesn't). Write it so a frontend dev could build the skeleton from the description alone.
- **category** — freeform string, whatever short label fits (e.g. `"landing-page hero"`, `"portfolio landing page"`, `"long-scroll landing page"`). Don't force it into a fixed enum.
- **tags** — array of short lowercase-hyphenated keywords (dark-mode, glassmorphism, bento-grid, pill-nav, gradient-text, etc.) — useful for scanning the gallery visually later.
- **style_notes** — separate from the description. This is *why* the design choice is worth stealing and *what's essential to keep* if duplicating the style: the one or two structural decisions that make the design work (e.g. "card shape reused identically across three unrelated sections is what makes the page feel systemized, not the specific icons"), and any trap to avoid if reproducing it (e.g. "only works because there's exactly one accent color fighting the dark background — a second accent would break the hierarchy"). Write it for a future you about to build something, who needs the reasoning and the load-bearing constraint, not a restatement of the look.
- **color_palette** — 4-6 hex strings, your best estimate of the dominant/accent colors actually present in the image.
- **source_url** — `null` unless the user gives you an actual URL for where the design came from.
- **date_added** — today's date, `YYYY-MM-DD`.

### 5. Append to data.js

Add the new object to the end of the `DATA` array. Only append — never edit, reorder, or remove existing entries. If `data.js` doesn't exist yet, create it with `const DATA = [ {...} ];`.

Schema:

```js
{
  id: "2026-07-25-003",
  filename: "photos/2026-07-25-003.jpg",
  description: "...",
  category: "...",
  tags: ["...", "..."],
  style_notes: "...",
  color_palette: ["#000000", "#ffffff"],
  source_url: null,
  date_added: "2026-07-25"
}
```

### 6. Confirm

Tell the user the assigned id and that it's saved. Don't auto-open the browser every time — only do that if they ask, or if this is the first entry in a session.
