---
name: design-bakeoff
description: Orchestrate all frontend/design skills into one website-design pipeline. Diverging variants, objective gates, real-pixel judging, learned taste profile, effort tiers. Use when user wants to design/redesign website, landing page, portfolio, dashboard, or app UI and wants best UI/UX. Triggers on "design a site/landing/portfolio/dashboard", "redesign this", "/design-bakeoff", any frontend visual-design request.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Task
---

# design-bakeoff

One brain (this file) drives the design engines. The engines stay pristine — steer them by HOW you invoke them, never by editing them. Improve the SYSTEM, not the parts.

**Using this skill?** Read `GUIDE.md` (same dir) for brief templates, effort tiers, steering, and worked examples. This file is the engine spec; `GUIDE.md` is the how-to.

## Engines (never edited — call-time steering only)

| Role | Skill | Driven how |
|---|---|---|
| Design read | `taste-skill` §0 | infer page kind / audience / vibe, set dials |
| Generator A | `taste-skill` | landing/portfolio ONLY (refuses dashboards) |
| Generator B | `impeccable craft` | any surface incl. dashboards/app UI |
| Generator C | `stitch-skill` | DESIGN.md spec → build (only if user drives Google Stitch) |
| Generator D | `high-end-visual-design` | Awwwards/agency briefs, VARIANCE ≥ 8 — expensive feel, blocks cheap defaults |
| Lane guide: minimalist | `minimalist-ui` | inject into Generator when dial reads VARIANCE ≤ 4, editorial/clean brief |
| Lane guide: brutalist | `industrial-brutalist-ui` | inject when brief explicitly calls for brutalist/tactical/raw aesthetic |
| Visual mockup | `imagegen-frontend-web` | generate one image per section BEFORE coding — used as design reference for generators |
| Visual mockup: mobile | `imagegen-frontend-mobile` | generate mobile screen concepts for mobile-first briefs or Stage 3 responsive check |
| Brand identity | `brandkit` | generate logo/brand-kit when brief has no existing brand assets |
| Redesign auditor | `redesign-existing-projects` | audit existing site, identify AI-slop patterns, plan targeted upgrades — used in redesign-preserve path |
| Judge 1 | `emil-design-eng` | feel/motion critique, Before/After table |
| Judge 2 | `impeccable audit`/`polish` | fix hierarchy, a11y, spacing, type, color |
| Motion | `gsap-*` | gsap-core → timeline/scrolltrigger/react, only if MOTION dial > 4 |
| Video/frames | `hyperframes` (router) → `motion-graphics` / `general-video` / `website-to-video` / `product-launch-video` / `remotion` | hero loops, accent motion-graphics, post-launch promo |
| Copy | `humanizer`, `edit-article` | de-AI the copy deck; long-form content |
| Web quality | `next-best-practices`, `react-best-practices` | port correctness — hydration, RSC, bundle, re-renders |
| SEO | `nextjs-seo`, `api-design-patterns` | meta/OG/sitemap/JSON-LD/CWV/favicons; form+API design |
| Ship | `hostinger-deploy`, `e2e` / `playwright-cli` | smoke test + deploy live |

`design-an-interface` is NOT here — it designs code/API module shapes, not visual UI.

## Skill firing matrix (efficiency governor — do NOT fire everything every run)

The engines above are a *menu*, not a checklist. Firing all 20 on every job wastes tokens and time. Fire by tier + trigger. Cost must match the job.

| Skill | Tweak | Page | Site | Conditional trigger (overrides tier) |
|---|:--:|:--:|:--:|---|
| `taste-skill` §0 (design read) | ✓ | ✓ | ✓ | always — it's the cheap read that gates the rest |
| Generator B `impeccable` | ✓ | ✓ | ✓ | always eligible (any surface) |
| Generator A `taste-skill` | — | ✓ | ✓ | landing/portfolio only; dropped on dashboard/app UI |
| Generator C `stitch-skill` | — | — | ○ | only if user drives Google Stitch |
| Generator D `high-end-visual-design` | — | ○ | ✓ | only when VARIANCE ≥ 8 or brief says agency/Awwwards/premium |
| Lane guide `minimalist-ui` | ○ | ○ | ○ | inject only into the variant whose lane is minimalist/editorial |
| Lane guide `industrial-brutalist-ui` | ○ | ○ | ○ | inject only when brief explicitly names brutalist/tactical/raw |
| `imagegen-frontend-web` | — | ○ | ✓ | skip if imagegen unavailable or visual direction already clear |
| `imagegen-frontend-mobile` | — | ○ | ○ | mobile-first briefs only |
| `brandkit` | — | ○ | ○ | ONLY when brief has no brand + explicitly wants identity work |
| awesome-design-md lookup | ○ | ✓ | ✓ | only when brief names/evokes a known brand (near-zero cost — just a file read) |
| `emil-design-eng` (judge) | ○ | ✓ | ✓ | skip on pure tweak unless motion/feel is the point |
| `impeccable audit` (judge) | ✓ | ✓ | ✓ | always — cheapest quality gate |
| `gsap-*` | ○ | ○ | ○ | winner only, and only if MOTION > 4 (see Stage 4) |
| `humanizer` / `edit-article` | — | ✓ | ✓ | only when the variant carries real marketing copy |
| `next/react-best-practices` | — | ✓ | ✓ | port stage only, and only for React/Next targets |
| `nextjs-seo` | — | ○ | ✓ | port stage, public-facing pages only |
| `redesign-existing-projects` | ○ | ○ | ✓ | redesign briefs only (there's existing code to audit) |
| video/`hyperframes` chain | — | ○ | ○ | only when brief wants real video beyond DOM/GSAP |
| ship (`hostinger-deploy`/`e2e`) | — | ○ | ○ | only on explicit "go live" |

✓ = default fires · ○ = fires only if the conditional trigger hits · — = skip.
**Rule of thumb:** a Tweak touches ~3 skills, a Page ~6-8, a Site ~10-14. If you're about to fire more than the tier's budget, ask why.

## Owned artifacts (this dir)

- `taste-signals.jsonl` — append-only machine-readable pick record (one row/run: gallery chips, note, winner tokens, runner-up reject, loser token-diffs, dials). Raw fuel for the learning loop; schema in `data/taste-signals.schema.md`. Written in Stage 5, read for auto-dial in Stage 0.
- `taste-profile.md` — the DERIVED prose narrative distilled from `taste-signals.jsonl` (fonts, palette, layout, motion, density). Rewritten by the distill step only. Read it in Stage 0.
- `references.md` — swipe file: real-pixel tokens extracted from sites you rate. Persists across jobs.
- `scoreboard.md` — secondary metric: generator win tally. Used only to retire a dead engine.
- `data/` — static lookup tables (`colors.csv` 160 palettes by product type, `typography.csv` 73 font pairs w/ ready imports, `charts.csv` 25 data-type→chart picks). Curated priors, not verdicts. See `data/README.md`. Grep to seed a variant when no real reference grounds the job; real pixels always override.

## Pipeline

### Stage 0 — Design Read + grounding (always, but cache-aware)
1. Run `taste-skill` §0: infer page kind, audience, vibe. State the one-line Design Read.
2. **Read `taste-profile.md` + `references.md` first.** If they cover this job, skip fresh grounding (reuse cache — cost drops as profile matures).
3. **Real-pixel grounding** (Q5, #2): if the user names/links sites or drops screenshots, ground in the *actual* pixels — not my memory of them.
   - **Live sites → read computed styles, not just a screenshot.** Open the ref in claude-in-chrome and pull real values via `getComputedStyle` (font-family, font-size scale ratio, line-height, letter-spacing, color/bg hex, contrast, spacing rhythm, border-radius, transition/easing curves). Far more accurate than eyeballing. Screenshot only supplements (composition/mood).
   - **Static screenshots / images** → image Read for principles.
   - Extract *principles* not layouts; append concrete tokens to `references.md`. Variants anchor to these real tokens, not my priors.
   - **No real reference given?** Grounding precedence: real pixels > awesome-design-md brand tokens > `data/` lookup tables > raw LLM priors.
     - **awesome-design-md brand match:** if the brief names or references a known brand aesthetic (stripe, linear, notion, apple, vercel, cursor, raycast, figma, spotify, etc.), check `~/.claude/reference/awesome-design-md/design-md/<brand>/DESIGN.md` — 74 brands available. If a match exists, copy its `DESIGN.md` to the project root and use it as the primary token reference. This gives real measured tokens (colors, type, spacing, radius, motion) from that brand's actual design system — far more accurate than memory.
     - **data/ fallback:** if no brand match, grep `data/colors.csv` for the matched product type and `data/typography.csv` for the read's mood to get a curated starting palette + font pair — beats inventing AI-purple/Inter. These SEED, they don't decide; divergence + judges still run. Dashboards: also grep `data/charts.csv` per data shape.
4. Set dials `VARIANCE / MOTION / DENSITY`.
   - **Auto-dial (gated):** if `taste-signals.jsonl` holds **≥5 rows for this register (brand/product)** OR a distill has already run, pre-set the starting dials from the learned per-register axis leanings (color-temp/ornament/type → V, motion-amount → M, density → D). State the auto-set values in the Design Read; the user overrides with words. **Below the gate, stay passive** — use `data/` + priors, no auto-dial (thin data overfits).
   - All 5 lanes still generate regardless; auto-dial only moves the *starting point*, never prunes divergence. Explore-1-in-4 still fires.
   Ask at most ONE clarifying question, only if the read genuinely diverges.

### Stage 1 — Effort tier (governor, Q6)
Auto-detect job size from the Design Read; this gates everything downstream:
- **Tweak** (one component / color / copy) → no bake-off. Single pass, judges only. Seconds.
- **Page** (one full page / section) → round-robin OR 2-variant bake-off. Ask which.
- **Site** (multi-page / new brand / redesign) → full 5-variant bake-off + grounding + winner port.

**Scope default — build the WHOLE page, not just the hero.** "landing" / "page" / "site" means every standard section for that page kind, e.g. landing = hero + value-prop / how-it-works + features + social-proof + pricing/plans + CTA + footer. Only build a fragment when the user explicitly scopes one ("hero", "pricing section", "this button"). If the user said a fragment, build that fragment; otherwise default to the full page. State the section list in the Design Read so scope is confirmed before generating.

### Stage 2 — Generators with divergence contracts (Q4)
**Scope guard:** non-landing surface → drop A (taste-skill refuses it). No Google Stitch → drop C. If only B is eligible (e.g. dashboard), B generates all five variants with distinct direction lanes — treat each as a separate invocation with its own divergence contract, not one.

**Variant count by tier:** Site → **5 variants** (five distinct lanes below). Page → 2 variants (pick two lanes farthest apart). Tweak → no bake-off. When fewer generators are eligible than variants needed, the eligible generators cover the extra lanes (e.g. B alone builds all 5, one per lane).

**Visual mockup first (optional but high-value):** before writing HTML, run `imagegen-frontend-web` to generate one reference image per section. Feed these images to the generators as compositional anchors — they'll produce code that matches an art-directed layout rather than inventing one. Skip if imagegen tools unavailable or brief is a minor tweak. For mobile-first briefs, also run `imagegen-frontend-mobile` for app screen concepts.

**Specialized lane guides:** when a variant's direction lane maps to a known aesthetic, inject the matching guide into that generator's context:
- Minimalist / editorial / calm → `minimalist-ui`
- Brutalist / tactical / raw / declassified → `industrial-brutalist-ui`
- Awwwards / agency / expensive-feel / VARIANCE ≥ 8 → `high-end-visual-design` (Generator D)

**Brand identity gap:** if the brief has no existing logo/brand, run `brandkit` first to generate a brand-kit board, then use its palette/type output to seed Stage 0 tokens before generators spawn.

**Controlled content first (#3) — fair comparison demands it.** Before spawning variants, lock TWO shared inputs so you judge DESIGN, not content:
- **One real copy deck** — write the actual headline, subhead, section copy, CTA labels ONCE (no lorem), then run it through `humanizer` so it doesn't read AI-generated (AI-sounding copy sinks a premium site). Long-form/blog content → `edit-article`. Every variant uses the same humanized words. Different copy across variants confounds the pick.
- **One image strategy** — pick a source and stick to it across variants: real photos (Unsplash/Pexels URLs), AI-gen, or sized placeholders with a written art-direction note. Visual sites (food/travel/product) live on photography — a missing/ugly image sinks a good layout. Same image set per variant = controlled variable.
Only the DESIGN diverges (layout/type/color/motion); copy + imagery are held constant.

Every bake-off variant is **static single-file** (`index.html`, CDN deps, no build) — Q2. This keeps the taste race fast, fair (same render path), and install/port-free. **Variants are built STATIC (no motion) by default** — you judge layout/type/color first, pick the winner, then motion goes on the winner only (Stage 4). Cheaper, no animation work thrown away.

**Exception — motion-first briefs:** when motion IS the message (kinetic-type / Awwwards / "make it move" / any lane with MOTION dial ≥ 7), ship a **motion signature inside each variant** so motion is judged as a divergence axis, not chosen blind. Use CDN GSAP, wrapped in `gsap.matchMedia()` honoring `prefers-reduced-motion`. Default off; turn on only when the brief makes motion the point (state which mode in the Design Read).

Each variant gets a **divergence contract** so they CAN'T converge — assign per variant a **direction lane**, a distinct **dial set**, one **banned crutch** it must avoid, and (motion-first briefs only) a distinct **motion signature** matched to its dial M. The five Site lanes:

| # | Direction lane | Dial set (V/M/D) | Banned crutch | Lane guide |
|---|---|---|---|---|
| 1 | editorial / type-driven | V5 / M3 / D2 | no card grid | `minimalist-ui` |
| 2 | Swiss-grid / restrained | V7 / M4 / D4 | no centered hero | — |
| 3 | minimalist / quiet | V3 / M2 / D2 | no gradient | `minimalist-ui` |
| 4 | kinetic / Awwwards-maximal | V9 / M8 / D4 | no default glassmorphism | `high-end-visual-design` |
| 5 | brutalist / tactical | V8 / M5 / D5 | no soft shadows | `industrial-brutalist-ui` |

Page tier picks the two lanes farthest apart on the read (usually 1 + 4, or 3 + 5). Each lane must diverge on layout/type/color — a shared palette across all five kills color divergence, so high-V lanes (4, 5) push off the seed hue.

The Design Read gates lanes to plausible-for-this-audience only (public-sector never gets lane 4/5; a design studio can take all five). Spawn eligible generators as **parallel subagents**, each carrying its contract + the `references.md` tokens (+ the `data/` palette/font seed when no real reference grounded Stage 0). The seed is a baseline, not a uniform: the restrained lane can take it near-verbatim, but high-VARIANCE and explore lanes must push off it (shifted hue, alt font pair) — a shared palette across all variants kills color divergence.

**Generator timeout resilience:** if a subagent times out or errors mid-run, do not re-spawn — generate the missing variant inline instead. Document what completed vs. what was generated inline in `run-summary.md`. The eval still runs; a partial with fewer variants is better than blocking indefinitely.

Explore rate: ~1 job in 4, ignore `taste-profile.md` and push one variant deliberately off-axis — keeps taste from ossifying.

### Stage 3 — Judging: gates → pixels → your eye (Q1)
LLM judges NARROW, they never DECIDE. Taste is the user's.
1. **Objective gates first, fail-fast** (Q6): render each static variant, run axe / contrast-ratio / Lighthouse a11y+perf. A variant that fails a gate is OUT — never reaches pixel/judge stage. Don't pay to judge broken work.
2. **Responsive gate (#1) — judge mobile AND desktop.** Screenshot each survivor at BOTH **mobile (375px)** and **desktop (1440px)**. Mobile is most traffic; a desktop-only win that breaks on mobile (overflow, unreadable type, broken nav, tap targets <44px) **fails the gate** — same as a11y. This is correctness, not taste. Both viewports go to the judges and to you.
3. **Real pixels** (Q1b): the mobile + desktop screenshots per survivor. For motion-first briefs (variants already animated), also capture motion — short GIF/clip (claude-in-chrome `gif_creator`) or live browser to scrub. `emil-design-eng` reads the IMAGES (feel/motion Before-After table), `impeccable audit` fixes the code. Score on: hierarchy, responsive integrity, motion feel, anti-slop (no AI-purple gradient on hero/background/CTAs — purple in code syntax highlighting is domain-correct for dev tools and is NOT a tell; no Inter as primary display font; no centered-hero over dark mesh; no default glassmorphism), brief fit, reference fidelity.
4. **Your eye decides** (Q1c) — **show survivors in a browser gallery, not just screenshots.** Build `gallery.html` at the project root that embeds every surviving variant and open it in claude-in-chrome so the user compares live:
   - One `<iframe src="variant-N/index.html">` per survivor in a responsive grid; each framed with its lane label + dial set + judge one-liner.
   - A **viewport toggle** (mobile 375px / desktop 1440px) that resizes the iframes so both breakpoints are viewable without leaving the page.
   - An **"open full"** link per variant (loads that variant alone in a new tab) and a **numbered pick control** (1-5) so the user states the winner by number.
   - Motion-first briefs: iframes render live motion; no clip needed. Keep the gallery static-single-file (no build).
   Serve the folder (e.g. `python3 -m http.server`) and open `gallery.html`. The USER picks the winner by number. I only narrowed — never auto-pick on taste.
   - **Capture WHY at pick-time (learning-loop fuel).** The pick control carries **6 fixed dial-aligned chips**, each a +/- toggle — the ONLY vocabulary (freeform tags rot the profile):
     `color-temp` (warmer/cooler) · `density` (denser/airier) · `type-character` (more-expressive/more-neutral) · `motion-amount` (more/less) · `layout-shape` (more-asymmetric/more-grid) · `ornament-level` (more/less). Winner gets the chips clicked (skip any that don't apply) + an **optional free-text note** for the rare reason no axis covers.
     One **reject chip on the runner-up only** (the "almost" variant): too-cold / too-cramped / generic / motion-overdone. The other 3 losers are logged by token-diff automatically in Stage 5 — no user input.
     These map 1:1 to the `VARIANCE / MOTION / DENSITY` dials so the signal reconciles with them directly. The pick + chips + note + runner-up reject are written in Stage 5.

### Stage 4 — Motion (winner only, default path)
Add motion to the chosen winner: `gsap-core`, then `gsap-timeline` / `gsap-scrolltrigger` / `gsap-react` / `gsap-frameworks` per host. Match the winner's MOTION dial — entrance reveals, scroll parallax/pin, hover micro-interactions, count-ups; restraint for low dials, don't add motion the lane didn't call for. Always `gsap.matchMedia()` + `prefers-reduced-motion`. Run `gsap-performance` (transforms only, no layout thrash, 60fps). Then show the user the animated winner to confirm before port. (Motion-first briefs already animated in Stage 2 — here just polish + perf-pass.)

### Stage 4.5 — Video / frames (winner, conditional)
Only when the brief or page wants real video/motion-graphics beyond DOM/GSAP. **Route through `hyperframes` first** (it dispatches intent), then:
- **Accent motion-graphics** (logo sting, stat/number count-up, kinetic headline, animated badge, social/overlay) → `motion-graphics`. Render MP4 or **transparent overlay** to layer on the page.
- **Hero / section background video** (ambient loop, b-roll) → `general-video` (or supply real footage). Embed muted + `loop` + `playsinline` + `poster` (winner's hero frame).
- **Post-launch promo** (capture the finished site → social clip) → `website-to-video`; **product/SaaS launch** → `product-launch-video`.
- React-native video build → `remotion`.

**Web-embed safety (loophole #6, non-negotiable):**
- `prefers-reduced-motion: reduce` AND `prefers-reduced-data: reduce` → show the `poster` still, never autoplay.
- `poster` always set (no blank flash); `preload="none"` / lazy-load below the fold; muted for autoplay.
- Video must not block LCP — poster image is the LCP candidate, not the video.
Skip this stage entirely for static/low-motion briefs.

### Stage 5 — Port + quality + learn
1. **Port winner** (Q2): the single chosen static variant → the user's real framework (Next/Vite/etc). Only the winner pays build cost.
1a. **Redesign path only:** run `redesign-existing-projects` on the existing codebase BEFORE porting — it audits for AI-slop patterns, broken layouts, and dead CSS, then applies targeted upgrades without breaking functionality. Merge its fixes into the port.
2. **Quality pass (loophole #3):** the port is NOT trusted until it passes the relevant best-practices skill — `next-best-practices` (RSC boundaries, hydration, async APIs, no data waterfalls) and `react-best-practices` (bundle size, re-renders, code-split). Fix what they flag.
3. **SEO pass:** `nextjs-seo` — metadata/`generateMetadata`, OG + twitter images, sitemap.xml, robots.txt, canonical, JSON-LD, favicons/manifest, Core Web Vitals. If the site has forms/backend, `api-design-patterns` for the endpoints.
4. **Export design tokens (#5, #7):** emit the winner's colors / type scale / spacing / radius / motion as `DESIGN.md` + CSS custom properties (or `tailwind.config`). **Write `DESIGN.md` to the project root** so `impeccable` reads it next run = future work auto-on-brand (closes the loop). Use `impeccable`'s token output; don't hand-roll.
5. **Append the structured signal (Q3, primary):** write ONE row to `taste-signals.jsonl` per run — the machine-readable raw record that fuels the loop. Schema (see `data/taste-signals.schema.md`):
   `{ date, page_kind, register (brand|product), winner_variant, chips {color_temp, density, type_character, motion_amount, layout_shape, ornament_level} (each -1|0|+1), note, winner_tokens {font, palette, layout, motion, density}, runner_up_reject (too-cold|too-cramped|generic|motion-overdone|null), loser_token_diffs [], dials {V, M, D}, generator }`.
   Chips come from the gallery pick control; the 3 non-runner-up losers get `loser_token_diffs` computed here (winner tokens minus each loser: font/palette/density/lane deltas). This is append-only and NEVER hand-summarized — the prose profile is derived from it.
6. **Prose profile stays human-readable:** `taste-profile.md` is the *derived* narrative, rewritten only by the distill step (9), not appended per-run. Between distills it's stable. (Old per-run appends to the table/rejection list are replaced by the signals log.)
7. **Swipe file**: promote any reference that drove the winner into `references.md` for reuse.
8. **Generator tally** (secondary): log winner's generator to `scoreboard.md`. Used only to retire an engine that never wins.
9. **Distill (#6) — every ~10 signal rows:** read `taste-signals.jsonl`, collapse into `taste-profile.md`'s stable preferences (always true) vs context-dependent ones (true for landing, not dashboard, gated by register/domain), resolving contradictions. The chips aggregate into per-register axis leanings (e.g. brand-landing → color-temp +0.7, density -0.3). Append-only raw + derived summary keeps signal sharp without rot. Trigger when the log passes ~10 rows since last distill.

### Stage 6 — Ship (optional, on user approval)
Only when the user asks to go live. Confirm before deploying (outward-facing, hard to reverse).
1. **Smoke test:** `e2e` / `playwright-cli` on critical flows (nav, forms, CTAs) at mobile + desktop.
2. **Deploy:** `hostinger-deploy` (static frontend + PHP backend default; follows its pre/post-deploy checklist).
3. Report the live URL + post-deploy checklist results.

## Laws
- Judges narrow; the user decides. Never auto-pick a winner on taste.
- Site tier ships 5 divergent variants (one per lane); surface them in a live browser gallery, not screenshots alone. The user picks by number.
- The gallery captures WHY at pick-time: 6 fixed dial-aligned chips + optional note on the winner, one reject chip on the runner-up. Fixed vocabulary only — freeform tags rot the profile.
- Learned signal lives raw in `taste-signals.jsonl`; `taste-profile.md` is derived by distill, never hand-appended. Auto-dial gated behind ≥5 rows/register or first distill; it moves the starting dials only, never prunes the 5 lanes.
- Engines are never edited — all intelligence lives in this file + the owned artifacts.
- A generated UI is unfinished until gates pass (a11y + responsive) AND both judges run.
- Copy + imagery are held constant across variants; only design diverges (fair comparison).
- Ground in real computed styles, not memory of a site; judge mobile + desktop, not desktop alone.
- Grounding precedence: real pixels > `data/` lookup tables > raw LLM priors. Tables seed a variant, never decide it; gates and judges still rule.
- Embedded video never autoplays under reduced-motion/data; always poster + lazy + muted; poster is the LCP, not the video.
- The port is unfinished until it passes best-practices + SEO; `DESIGN.md` goes to project root so the loop closes.
- Ship only on explicit approval — deploy is outward-facing and hard to reverse.
- Cost bends down as `taste-profile.md` / `references.md` mature; quality bends up. Reuse the cache.
- Match implementation complexity to the dials: maximalism needs elaborate code, minimalism needs precision.
