# taste-signals.jsonl — schema

Append-only, one JSON object per line, one line per bake-off run. Machine-readable raw record of every pick. `taste-profile.md` is DERIVED from this by the Stage 5 distill; never hand-edit the prose to match, rewrite it from here.

Written in **Stage 5 step 5**. Read in **Stage 0 step 4** for gated auto-dial (≥5 rows for the register, or after first distill).

## Fields

| Field | Type | Notes |
|---|---|---|
| `date` | string | ISO `YYYY-MM-DD`, run date. |
| `page_kind` | string | e.g. `"full landing"`, `"product register"`, `"dashboard"`. |
| `register` | `"brand" \| "product"` | Brand-landing vs product/app UI. Auto-dial + distill segment by this. |
| `domain` | string | e.g. `"food"`, `"dev-tool"`, `"b2b-services"`. Optional secondary gate. |
| `winner_variant` | int | Lane number 1-5 the user picked. |
| `chips` | object | The 6 fixed dial-aligned axes, each `-1 \| 0 \| +1`. See below. |
| `note` | string | Optional free-text reason no axis covers. `""` when empty. |
| `winner_tokens` | object | `{ font, palette, layout, motion, density }` — concrete winning tokens. |
| `runner_up_reject` | enum\|null | `"too-cold" \| "too-cramped" \| "generic" \| "motion-overdone" \| null`. One reject chip on the "almost" variant only. |
| `loser_token_diffs` | array | The 3 non-runner-up losers: `[{ variant, font_delta, palette_delta, density_delta, lane }]`. Computed in Stage 5, not user-entered. |
| `dials` | object | `{ V, M, D }` — the dial values that produced this run. |
| `generator` | string | Winning generator (`impeccable` / `taste-skill` / `high-end-visual-design` / ...). Also tallied to `scoreboard.md`. |
| `explore` | bool | True if this run's winner was the explore-1-in-4 off-axis lane. Distill down-weights explore picks. |

### `chips` axes (fixed vocabulary — the ONLY tags)

| Axis | `-1` | `+1` | Feeds dial |
|---|---|---|---|
| `color_temp` | cooler | warmer | V |
| `density` | airier | denser | D |
| `type_character` | more-neutral | more-expressive | V |
| `motion_amount` | less | more | M |
| `layout_shape` | more-grid | more-asymmetric | V |
| `ornament_level` | less | more | V |

`0` = axis not clicked / neutral. Chips come straight from the gallery pick control.

## Example row

```json
{"date":"2026-07-25","page_kind":"full landing","register":"brand","domain":"food","winner_variant":4,"chips":{"color_temp":1,"density":-1,"type_character":1,"motion_amount":1,"layout_shape":1,"ornament_level":1},"note":"the ember glow sells the wood-fired story","winner_tokens":{"font":"Fraunces 300 + italic accent","palette":"char-black bg / ember / gold","layout":"full-bleed photo hero + alternating rows","motion":"scroll parallax + reveals (M6)","density":"bold D4"},"runner_up_reject":"too-cold","loser_token_diffs":[{"variant":3,"font_delta":"neutral grotesk vs expressive serif","palette_delta":"greyscale vs warm","density_delta":"airier","lane":"minimalist"},{"variant":2,"font_delta":"grid-neutral","palette_delta":"cool","density_delta":"same","lane":"swiss-grid"},{"variant":1,"font_delta":"same family lighter","palette_delta":"lighter warm","density_delta":"airier","lane":"editorial"}],"dials":{"V":9,"M":8,"D":4},"generator":"high-end-visual-design","explore":false}
```

## Distill aggregation (Stage 5 step 9)

Every ~10 rows: group by `register`, average each chip axis → per-register leaning (e.g. brand → `color_temp +0.7`, `density -0.3`). Cross-check `runner_up_reject` frequencies and `loser_token_diffs` for consistent anti-preferences. Write the result into `taste-profile.md` stable-vs-context sections. Down-weight `explore:true` rows so exploration doesn't skew the baseline.
