# AI Writing Tells

Full catalog of signs of AI-generated text, used by the AI-tells pass in `../SKILL.md`. Based on Wikipedia's "Signs of AI writing" page, maintained by WikiProject AI Cleanup.

When cleaning a draft: identify AI patterns, rewrite (don't delete), preserve meaning, match the register. Cover everything the original covers. If the original has five paragraphs, the rewrite has five.

## Personality and Soul

Avoiding AI patterns is only half the job. Sterile, voiceless writing is just as obvious as slop.

**Apply this section only when the content and voice call for it** (blog posts, essays, opinion, personal statements, reflective writing). For formal email, store voice, technical, or reference text, neutral and plain *is* the correct human voice. Do not inject opinions or first person there.

Signs of soulless writing (even if technically clean):
- Every sentence is the same length and structure.
- No opinions, just neutral reporting.
- No acknowledgment of uncertainty or mixed feelings.
- No first-person perspective when appropriate.
- No humor, no edge, no personality.
- Reads like a Wikipedia article or press release.

How to add voice:
- **Have opinions.** React to facts, don't just report them.
- **Vary rhythm.** Short punchy sentences, then longer ones. Mix it up.
- **Let some mess in.** Tangents, asides, half-formed thoughts are human.

Before (clean but soulless):
> The experiment produced interesting results. The agents generated 3 million lines of code. Some developers were impressed while others were skeptical. The implications remain unclear.

After (has a pulse):
> I genuinely don't know how to feel about this one. 3 million lines of code, generated while the humans presumably slept. Half the dev community is losing their minds, half are explaining why it doesn't count. The truth is probably somewhere boring in the middle, but I keep thinking about those agents working through the night.

## Content Patterns

### 1. Undue Emphasis on Significance, Legacy, and Broader Trends
**Watch:** stands/serves as, is a testament/reminder, a vital/significant/crucial/pivotal/key role/moment, underscores/highlights its importance, reflects broader, symbolizing its ongoing/enduring/lasting, contributing to the, setting the stage for, marking/shaping the, represents/marks a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted.
**Fix:** State the plain fact without puffing up its importance.
> Before: The Institute was established in 1989, marking a pivotal moment in the evolution of regional statistics.
> After: The Institute was established in 1989 to collect and publish regional statistics independently.

### 2. Undue Emphasis on Notability and Media Coverage
**Watch:** independent coverage, local/regional/national media outlets, written by a leading expert, active social media presence.
> Before: Her views have been cited in The New York Times, BBC, and The Hindu. She maintains an active social media presence with over 500,000 followers.
> After: In a 2024 New York Times interview, she argued that AI regulation should focus on outcomes rather than methods.

### 3. Superficial Analyses with -ing Endings
**Watch:** highlighting/underscoring/emphasizing..., ensuring..., reflecting/symbolizing..., contributing to..., cultivating/fostering..., encompassing..., showcasing...
> Before: The palette of blue, green, and gold resonates with the region's beauty, symbolizing bluebonnets and the Gulf, reflecting the community's deep connection to the land.
> After: The temple uses blue, green, and gold. The architect chose them to reference local bluebonnets and the Gulf coast.

### 4. Promotional and Advertisement-like Language
**Watch:** boasts a, vibrant, rich (figurative), profound, enhancing its, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking (figurative), renowned, breathtaking, must-visit, stunning.
> Before: Nestled within the breathtaking region of Gonder, Alamata Raya Kobo stands as a vibrant town with rich cultural heritage and stunning natural beauty.
> After: Alamata Raya Kobo is a town in the Gonder region of Ethiopia, known for its weekly market and 18th-century church.

### 5. Vague Attributions and Weasel Words
**Watch:** Industry reports, Observers have cited, Experts argue, Some critics argue, several sources (when few cited).
> Before: Experts believe it plays a crucial role in the regional ecosystem.
> After: The river supports several endemic fish species, according to a 2019 survey by the Chinese Academy of Sciences.

### 6. Outline-like "Challenges and Future Prospects" Sections
**Watch:** Despite its... faces several challenges..., Despite these challenges, Challenges and Legacy, Future Outlook.
> Before: Despite its prosperity, Korattur faces challenges typical of urban areas. Despite these challenges, it continues to thrive.
> After: Traffic congestion increased after 2015 when three IT parks opened. The corporation began a drainage project in 2022 to address floods.

## Language and Grammar Patterns

### 7. Overused AI Vocabulary Words
**High-frequency:** actually, additionally, align with, crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight (verb), interplay, intricate/intricacies, key (adjective), landscape (abstract noun), pivotal, showcase, tapestry (abstract noun), testament, underscore (verb), valuable, vibrant.
> Before: An enduring testament to Italian influence is the widespread adoption of pasta in the local culinary landscape, showcasing how these dishes integrated into the diet.
> After: Pasta dishes, introduced during Italian colonization, remain common, especially in the south.

### 8. Avoidance of is/are (Copula Avoidance)
**Watch:** serves as/stands as/marks/represents [a], boasts/features/offers [a].
> Before: Gallery 825 serves as LAAA's exhibition space and boasts over 3,000 square feet.
> After: Gallery 825 is LAAA's exhibition space. It has four rooms totaling 3,000 square feet.

### 9. Negative Parallelisms and Tailing Negations
Constructions like "Not only...but...", "It's not just about..., it's..." are overused. So are clipped tailing negations ("no guessing", "no wasted motion") tacked onto the end.
> Before: It's not just about the beat; it's part of the aggression. It's not merely a song, it's a statement.
> After: The heavy beat adds to the aggressive tone.
> Before: The options come from the selected item, no guessing.
> After: The options come from the selected item without forcing the user to guess.

### 10. Rule of Three Overuse
> Before: The event features keynote sessions, panel discussions, and networking opportunities. Attendees can expect innovation, inspiration, and industry insights.
> After: The event includes talks and panels. There's also time for informal networking between sessions.

### 11. Elegant Variation (Synonym Cycling)
> Before: The protagonist faces challenges. The main character must overcome obstacles. The central figure triumphs. The hero returns home.
> After: The protagonist faces many challenges but eventually triumphs and returns home.

### 12. False Ranges
"from X to Y" where X and Y aren't on a meaningful scale.
> Before: from the singularity of the Big Bang to the grand cosmic web, from the birth of stars to the dance of dark matter.
> After: The book covers the Big Bang, star formation, and current theories about dark matter.

### 13. Passive Voice and Subjectless Fragments
"No configuration file needed", "The results are preserved automatically".
> Before: No configuration file needed. The results are preserved automatically.
> After: You do not need a configuration file. The system preserves the results automatically.

## Style Patterns

### 14. Em Dashes and En Dashes: Cut Them (HARD GATE)
The final text contains no em dashes (—) or en dashes (–). Replace each, in order of preference: a period (new sentence), a comma (tight aside), a colon (explanation), parentheses (true aside), or restructure. Also catch spaced em dashes (` — `) and double hyphens (` -- `).
> Before: The term is promoted by Dutch institutions—not by the people—even in official documents.
> After: The term is promoted by Dutch institutions, not by the people, even in official documents.
Before delivering, scan for `—` and `–`. Any hit means the draft isn't done.

### 15. Overuse of Boldface
> Before: It blends **OKRs**, **KPIs**, and tools such as the **Business Model Canvas**.
> After: It blends OKRs, KPIs, and tools like the Business Model Canvas.

### 16. Inline-Header Vertical Lists
Items starting with bolded headers followed by colons.
> Before: - **Performance:** Performance has been enhanced through optimized algorithms.
> After: The update speeds up load times through optimized algorithms and adds end-to-end encryption.

### 17. Title Case in Headings
> Before: ## Strategic Negotiations And Global Partnerships
> After: ## Strategic negotiations and global partnerships

### 18. Emojis
Don't decorate headings or bullets with emojis.
> Before: 🚀 **Launch Phase:** The product launches in Q3
> After: The product launches in Q3.

### 19. Curly Quotation Marks
Use straight quotes ("...") not curly (“...”).
> Before: He said “the project is on track” but others disagreed.
> After: He said "the project is on track" but others disagreed.

## Communication Patterns

### 20. Collaborative Communication Artifacts
**Watch:** I hope this helps, Of course!, Certainly!, You're absolutely right!, Would you like..., Want me to...?, Should I continue?, let me know, here is a...
> Before: Here is an overview of the French Revolution. I hope this helps! Let me know if you'd like me to expand.
> After: The French Revolution began in 1789 when financial crisis and food shortages led to unrest.

### 21. Knowledge-Cutoff Disclaimers and Speculative Gap-Filling
**Watch:** as of [date], Up to my last training update, While specific details are limited..., based on available information, maintains a low profile, keeps personal details private, likely [grew up/studied], it is believed that.
Say what isn't known, or cut the sentence. Don't dress a guess up as fact.
> Before: While specific details about the founding are not extensively documented, it appears to have been established sometime in the 1990s.
> After: The company was founded in 1994, according to its registration documents.

### 22. Sycophantic/Servile Tone
> Before: Great question! You're absolutely right that this is complex. That's an excellent point.
> After: The economic factors you mentioned are relevant here.

## Filler and Hedging

### 23. Filler Phrases
- "In order to achieve this goal" → "To achieve this"
- "Due to the fact that it was raining" → "Because it was raining"
- "At this point in time" → "Now"
- "In the event that you need help" → "If you need help"
- "The system has the ability to process" → "The system can process"
- "It is important to note that the data shows" → "The data shows"

### 24. Excessive Hedging
> Before: It could potentially possibly be argued that the policy might have some effect.
> After: The policy may affect outcomes.

### 25. Generic Positive Conclusions
> Before: The future looks bright. Exciting times lie ahead as they continue their journey toward excellence.
> After: The company plans to open two more locations next year.

### 26. Hyphenated Word Pair Overuse
**Watch:** third-party, cross-functional, client-facing, data-driven, decision-making, well-known, high-quality, real-time, long-term, end-to-end. Keep the hyphen when the compound is attributive (`a high-quality report`); drop it when it follows the noun (`the report is high quality`).
> Before: The team is cross-functional, the report is high-quality, and the methodology is data-driven.
> After: The team is cross functional, the report is high quality, and the methodology is data driven.

### 27. Persuasive Authority Tropes
**Watch:** The real question is, at its core, in reality, what really matters, fundamentally, the deeper issue, the heart of the matter.
> Before: The real question is whether teams can adapt. At its core, what really matters is organizational readiness.
> After: The question is whether teams can adapt. That mostly depends on whether the organization is ready to change its habits.

### 28. Signposting and Announcements
**Watch:** Let's dive in, let's explore, let's break this down, here's what you need to know, now let's look at, without further ado.
> Before: Let's dive into how caching works in Next.js. Here's what you need to know.
> After: Next.js caches data at multiple layers, including request memoization, the data cache, and the router cache.

### 29. Fragmented Headers
A heading followed by a one-line paragraph that restates the heading.
> Before: ## Performance / Speed matters. / When users hit a slow page, they leave.
> After: ## Performance / When users hit a slow page, they leave.

### 30. Diff-Anchored Writing
Docs written as if narrating a change rather than describing the thing as it is.
> Before: This function was added to replace the previous approach of iterating through all items, which caused O(n²) performance.
> After: This function uses a hash map for O(1) lookups, avoiding the O(n²) cost of naive iteration.

### 31. Manufactured Punchlines and Staccato Drama
> Before: Then AlphaEvolve arrived. It had no preference for symmetry. No aesthetic prior. No nostalgia for human taste. The old rules were gone.
> After: AlphaEvolve changed the search because it did not favor symmetry or human-looking designs. That made some older assumptions less useful.

### 32. Aphorism Formulas
**Watch:** X is the Y of Z, X becomes a trap, X is not a tool but a mirror, the language of, the currency of, the architecture of.
> Before: Symmetry is the language of trust. Efficiency becomes a trap when teams forget the human layer.
> After: Symmetric layouts often feel more predictable to users. Teams can over-optimize workflows and miss how people actually use them.

### 33. Conversational Rhetorical Openers
**Watch:** Honestly?, Look, Here's the thing, The thing is, Let's be honest, Real talk, as standalone hooks before an ordinary point.
> Before: Is it worth the price? Honestly? It depends on how often you'll use it.
> After: Whether it's worth the price depends on how often you'll use it.

## Detection Guidance

### What NOT to flag (false positives)
Not reliable indicators on their own: perfect grammar, mixed casual/formal registers, "bland" prose, formal vocabulary, salutations/sign-offs, one common transition word, curly quotes alone (auto-curl is default in most editors), one em dash alone, one short emphatic sentence, "honestly"/"look" mid-sentence, unsourced claims, clean formatting, secondhand text (quotes, titles, examples being discussed).

Look for **clusters** of tells, not isolated ones. A single em dash means nothing; em dashes plus rule-of-three plus "vibrant tapestry" plus a "Conclusion" section is a confession.

### Signs of human writing (preserve these)
Specific hard-to-fabricate detail, mixed feelings and unresolved tension, dated era-bound references, first-person editorial choices the writer can defend, variety in sentence length, genuine asides and self-corrections, edits made before November 30, 2022.

## Reference
Based on [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). Key insight: "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases."
