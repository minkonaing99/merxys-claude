---
name: teach
description: Teach the user a new skill or concept, within this workspace.
argument-hint: "What would you like to learn about?"
---

The user has asked you to teach them something. This is a stateful request - they intend to learn the topic over multiple sessions.

## First Invocation: Scaffold the Workspace

On every invocation, check whether the workspace files below exist. If they don't, create them immediately before teaching anything:

1. Ask the user why they want to learn this topic, then write `MISSION.md` (see [MISSION-FORMAT.md](./MISSION-FORMAT.md)).
2. Create the directories `./lessons/`, `./reference/`, `./deep-dive/`, and `./learning-records/`.
3. Create `RESOURCES.md` and populate it with an initial set of high-quality resources (see [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md)).
4. Create an empty `GLOSSARY.md` for the topic (see [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md)). Add terms only as the user demonstrates understanding.
5. Create `NOTES.md` with any teaching preferences the user has already expressed.

Then produce the first lesson in `./lessons/`.

## Teaching Workspace

Treat the current directory as a teaching workspace. The state of their learning is captured in this directory in several files:

- `MISSION.md`: A document capturing the _reason_ the user is interested in the topic. This should be used to ground all teaching. Use the format in [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `./reference/*.html`: A directory of reference materials. These are the compressed learnings from the lessons - cheat sheets, reference algorithms, syntax, yoga poses, glossaries. They are the raw units of learning. They should be beautiful documents which print out well, and are designed for quick reference.
- `RESOURCES.md`: A list of resources which can be explored to ground your teaching in contextual knowledge, or to acquire knowledge and wisdom. Use the format in [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `GLOSSARY.md`: The canonical terminology for the topic. All lessons and reference documents must adhere to it. Use the format in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).
- `./learning-records/*.md`: A directory of learning records, which capture what the user has learned. These are loosely equivalent to architectural decision records in software development - they capture non-obvious lessons and key insights that may need to be revised later, or drive future sessions. These should be used to calculate the zone of proximal development. They are titled `0001-<dash-case-name>.md`, where the number increments each time. Use the format in [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `./lessons/*.html`: A directory of lessons. A **lesson** is a single, self-contained HTML output that teaches one tightly-scoped thing tied to the mission. This is the primary unit of teaching in this workspace.
- `./deep-dive/*.html`: A directory of **deep dives** — long-form teaching documents that explain a unit in full, for the user who wants to learn deeply and be tested rigorously (exams, interviews, real mastery). See [DEEP-DIVE-FORMAT.md](./DEEP-DIVE-FORMAT.md).
- `NOTES.md`: A scratchpad for you to jot down user preferences, or working notes.

## Philosophy

To learn at a deep level, the user needs three things:

- **Knowledge**, captured from high-quality, high-trust resources
- **Skills**, acquired through highly-relevant interactive lessons devised by you, based on the knowledge
- **Wisdom**, which comes from interacting with other learners and practitioners

Before the `RESOURCES.md` is well-populated, your focus should be to find high-quality resources which will help the user acquire knowledge. Never trust your parametric knowledge.

Some topics may require more skills than knowledge. Learning more about theoretical physics might be more knowledge-based. For yoga, more skills-based.

## Lessons

A lesson is the main thing you produce — the unit in which knowledge and skills reach the user. Each lesson is one self-contained HTML file, saved to `./lessons/` and titled `0001-<dash-case-name>.html` where the number increments each time.

A lesson should be **beautiful** — clean, readable typography and layout — since the user will return to these later to review.

The lesson should teach ONE THING only. It should be completable very quickly - but give the user a tangible win that they can build on. It should be directly tied to the mission, and should be in the user's zone of proximal development.

Make opening a lesson as easy as possible — ideally a single CLI command the user can run to open the HTML file in their browser.

## The Three Layers Per Unit

A well-taught topic is broken into **units** (chapters, modules, poses, whatever the topic's natural division is). Each unit is taught in up to three layers, each serving a different moment in the learning cycle:

1. **Deep dive** (`./deep-dive/NN-*.html`) — long-form teaching text to **learn deeply**. Read to understand and to prepare for exams/interviews.
2. **Lesson** (`./lessons/NNNN-*.html`) — interactive drill + applied exercise to **test yourself**. The tight feedback loop.
3. **Reference** (`./reference/NN-*.html`) — one-page compressed sheet to **revise fast**. What you review the night before.

Match the layers to the mission. If the user wants surface familiarity, a lesson + reference may be enough. **If the user's goal is mastery, top grades, certification, or an interview — build all three, deep dive included.** When a user says the material feels "too thin" or asks to "go deeper / know more," that is the signal to add (or thicken) the deep-dive layer. Record the chosen depth in `NOTES.md` so future units match it without re-asking.

## Deep Dives

A **deep dive** is the study-to-master document: comprehensive, long-form, and dense with worked examples and exam-style practice. Where a lesson teaches one skill and a reference compresses, a deep dive teaches a whole unit in full and prepares the user to be tested on it. Build one per unit (and one per synthesis topic) whenever the mission calls for depth. Full structure and rules are in [DEEP-DIVE-FORMAT.md](./DEEP-DIVE-FORMAT.md); the essentials:

- **Full teaching narrative**, not bullet fragments — explain the *why*, not just the *what*.
- **Many worked examples**, fully solved. For quantitative topics, show every step and vary which value is hidden.
- **A common-mistakes table** (wrong vs right) targeting the exact errors the topic's exams punish.
- **An exam long-answer bank** with model answers, marked by weight, so the user learns answer *structure*.
- **An extended glossary** and **citations on every claim**, drawn from `RESOURCES.md`.
- Beautiful, print-friendly HTML in the same design system as the lessons and references.

Deep dives are the layer users return to most when the stakes are high, so invest in them accordingly.

## The Mission

Every lesson should be tied into the mission - the reason that the user is interested in learning about the topic.

If the user is unclear about the mission, or the `MISSION.md` is not populated, your first job should be to question the user on why they want to learn this.

Failing to understand the mission will mean knowledge acquisition is not grounded in real-world goals. Lessons will feel too abstract. You will have no way of judging what the user should do next.

## Zone Of Proximal Development

Each lesson, the learner should always feel as if they are being challenged 'just enough'.

The user may specify an exact thing they want to learn. If they don't, figure out their zone of proximal development by:

- Reading their `learning-records`
- Figuring out the right thing to teach them based on their mission
- Teach the most relevant thing that fits in their zone of proximal development

A user may tell you that they already know about that topic. If so, record it in their `learning-records`.

## Acquiring Knowledge & Skills

Lessons should be designed around a skill the user is going to learn. The knowledge in the lesson should be only what's required to acquire that skill. You teach the knowledge first, then get the user to practice the skills via an interactive feedback loop.

Knowledge should first be gathered from trusted resources. Use `RESOURCES.md` to keep track of them. Lessons should be littered with citations - links to external resources to back up any claim made. This increases the trustworthiness of the lesson, and gives the user a path to acquire more knowledge if they want to go deeper.

### Researching Knowledge (search first, never guess)

Before writing any lesson, reference, or deep dive, **research the topic from authoritative sources**. Never build teaching material from parametric memory alone; it is how errors get taught. The search order:

1. **The topic's own primary source.** If it is a course, find the real syllabus/curriculum (search the institution's site, program page, official PDFs). If a standard or law, read the standard/regulation itself. If a tool or language, read its official docs. This anchors scope to what the user will actually be tested on or use.
2. **Recognised authorities.** Standards bodies (ISO, NIST, RFCs), canonical textbooks, peer-reviewed work, official documentation. For code topics, search GitHub and package registries for battle-tested implementations before writing your own examples.
3. **Reputable secondary sources** only to fill gaps: well-known courses, expert explainers, high-signal community wikis.

Then: record every source in `RESOURCES.md` with an annotation, cite them throughout the material, and **be honest about gaps**. If the authoritative source (e.g. a detailed public syllabus) does not exist, say so in the material, reconstruct the scope from the best available authorities, and flag that it must be reconciled against the official version when the user obtains it. When new primary information arrives (the real syllabus is published), reconcile the unit map against it.

Each lesson should contain a reminder to ask followup questions to the agent. The agent is their teacher, and can assist with anything that's unclear.

### Skills

Skills should be taught through interactive lessons. There are several tools at your disposal:

- Interactive lessons, using quizzes and light in-browser tasks
- Lessons which guide the user through a list of real-world steps to take (for instance, yoga poses)
- In-agent quizzes, where you ask the user scenario-based questions about what they've learned

Each of these should be based on a **feedback loop**, where the user receives feedback on their performance. This feedback loop should be as tight as possible, giving feedback immediately - and ideally automatically.

## Acquiring Wisdom

Wisdom comes from true real-world interaction - testing your skills outside the learning environment.

When the user asks a question that appears to require wisdom, your default posture should be to attempt to answer - but to ultimately delegate to a **community**.

A community is a place (online or offline) where the user can test their skills in the real world. This might be a forum, a subreddit, a real-world class (budget permitting) or a local interest group.

You should attempt to find high-reputation communities the user can join. If the user expresses a preference that they don't want to join a community, respect it.

## Reference Documents

While creating lessons, you should also create reference documents. Lessons can reference these documents - they are useful for tracking raw units of knowledge useful across lessons.

Lessons will rarely be revisited later - reference documents will be. They should be the compressed essence of the lesson, in a format designed for quick reference.

Some learning topics lend themselves to reference:

- Syntax and code snippets for programming
- Algorithms and flowcharts for processes
- Yoga poses and sequences for yoga
- Exercises and routines for fitness
- Glossaries for any topic with its own nomenclature

Glossaries, in particular, are an essential reference. Once one is created, it should be adhered to in every lesson.

## `NOTES.md`

The user will sometimes express preferences of how they want to be taught, or things you should keep in mind. This is the place to record those preferences, so you can refer back to them when designing lessons or working with the user.
