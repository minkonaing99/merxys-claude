# merxys-claude

Personal Claude Code configuration - agents, commands, hooks, skills, plugins, and rules.

---

## Install on New Machine

```bash
git clone https://github.com/minkonaing99/merxys-claude.git ~/.claude
cd ~/.claude/hooks && npm install
```

**Requirements:** Node.js (for hooks), Claude Code CLI.

---

## What Gets Ignored (not in repo)

| Path | Why excluded |
|------|-------------|
| `history.jsonl` | Session conversation history |
| `sessions/`, `session-env/` | Runtime session state |
| `projects/` | Machine-specific path data |
| `cache/`, `paste-cache/` | Temporary cache |
| `backups/` | Auto-generated backups |
| `tasks/`, `telemetry/`, `ide/` | Runtime artifacts |
| `plugins/cache/`, `plugins/data/` | Plugin download cache |
| `plugins/installed_plugins.json` | Regenerated on `claude plugin install` |

---

## Directory Structure

```
~/.claude/
├── CLAUDE.md               # Global rules Claude follows in every project
├── settings.json           # Permissions, hooks, statusline config
├── statusline-command.sh   # Terminal statusline script
├── skills-lock.json        # Locked skill versions
├── agents/                 # Subagent definitions
├── commands/               # Slash commands (/plan, /tdd, etc.)
├── hooks/                  # Lifecycle hook scripts (Node.js)
├── plugins/                # Plugin marketplace config
│   └── marketplaces/
│       ├── ponytail/       # Ponytail plugin (DietrichGebert/ponytail)
│       └── apple-skills/   # Apple/iOS skills (local, disabled by default)
├── rules/                  # Coding standards loaded per language
│   ├── typescript/
│   └── python/
└── skills/                 # Skill definitions (user-invocable tools)
```

---

## Plugins

| Plugin | Source | Status | Purpose |
|--------|--------|--------|---------|
| `ponytail` | `DietrichGebert/ponytail` (GitHub) | Active | Lazy-senior dev mode (YAGNI enforcer) |
| `apple-skills` | Local directory | Disabled by default | 151 iOS/Apple dev skills |

### Ponytail

Lazy senior dev mode. Enforces YAGNI via a ladder: does it need to exist? -> stdlib? -> native platform feature? -> existing dep? -> one line? -> minimum code. Marks deliberate shortcuts with `// ponytail:` comments naming the ceiling and upgrade path.

Activate: `/ponytail [lite|full|ultra]` - Stop: `stop ponytail` or `normal mode`

### Apple Skills

151 iOS/Apple development skills. Disabled by default to avoid polluting non-iOS sessions.

Enable for iOS work: `claude plugin enable apple-skills`

---

## Hooks

Wired via `settings.json`.

| Event | What it does |
|-------|-------------|
| `PreToolUse` | Starts a 5-min `caffeinate` to keep the machine awake while Claude works |
| `Stop` | Kills the `caffeinate` process when Claude finishes |
| `Notification` | Plays a sound (`Glass.aiff`) on notifications |

---

## Agents

Subagents Claude spawns for specialized work. Defined in `agents/`. Claude invokes automatically or you can ask explicitly.

| Agent | Model | When Claude uses it |
|-------|-------|---------------------|
| `architect` | Opus | System design, scalability decisions, architectural planning |
| `build-error-resolver` | Sonnet | Build failures, TypeScript errors - minimal diffs only |
| `code-reviewer` | Sonnet | After every code change - quality, security, maintainability |
| `dependency-checker` | Sonnet | Auditing npm/pip/SwiftPM packages for vulnerabilities |
| `doc-updater` | Haiku | Updating codemaps and docs, generating `docs/CODEMAPS/*` |
| `e2e-runner` | Sonnet | Playwright E2E tests - generate, run, capture artifacts |
| `migration-guide` | Sonnet | Major version upgrades, breaking change analysis, codemods |
| `perf-profiler` | Sonnet | Runtime bottlenecks, memory leaks, bundle size, slow queries |
| `planner` | Opus | Feature planning before coding - PRD, architecture, task list |
| `refactor-cleaner` | Sonnet | Dead code removal using knip/depcheck/ts-prune |
| `security-reviewer` | Sonnet | Secrets, SSRF, injection, OWASP Top 10 before commits |
| `tdd-guide` | Sonnet | Enforces RED->GREEN->REFACTOR, ensures 80%+ coverage |

**Workflow gates from `CLAUDE.md`:** planner before non-trivial work, code-reviewer after every change, security-reviewer before commits.

---

## Commands (Slash Commands)

Commands live in `commands/`. Invoke with `/command-name` in any session.

| Command | What it does |
|---------|-------------|
| `/plan` | Spawns `planner`. Restates requirements, assesses risks, creates step-by-step plan. Waits for confirm before touching code. |
| `/tdd` | Spawns `tdd-guide`. Writes failing tests first, then minimal implementation. Enforces 80%+ coverage. |
| `/code-review` | Reviews uncommitted changes. Reports CRITICAL/HIGH issues. |
| `/security-review` | Language-appropriate security audit (npm audit, pip-audit, etc.). Checks OWASP Top 10. |
| `/test-coverage` | Measures coverage, generates missing tests to hit 80%+. |
| `/build-fix` | Runs build, fixes errors incrementally with minimal diffs. |
| `/lint` | Detects linting tools (ESLint, Ruff, SwiftLint, etc.), auto-fixes what's possible. |
| `/deps` | Audits npm/pip/SwiftPM for outdated, vulnerable, and unused packages. |
| `/e2e` | Spawns `e2e-runner`. Generates and runs Playwright E2E tests, captures screenshots/videos/traces. |
| `/refactor-clean` | Finds dead code with knip/depcheck/ts-prune, removes safely with test verification. |
| `/update-docs` | Syncs documentation with codebase. |
| `/update-codemaps` | Scans project structure, generates token-lean architecture docs in `docs/CODEMAPS/`. |
| `/necessary-docs` | Scaffolds full `docs/` structure: api.md, database.md, architecture.md, release_notes.md. |

---

## Skills

Skills are richer tools beyond commands. Located in `skills/`. Plugin skills come from their respective marketplaces. Symlinked skills (`->`) come from a shared `.agents/skills/` pack.

### Ponytail Skills

| Skill | What it does |
|-------|-------------|
| `/ponytail [mode]` | Activate lazy-senior mode (YAGNI + shortest-path enforcement) |
| `/ponytail-help` | Show ponytail commands and the YAGNI ladder |
| `/ponytail-audit` | Audit current code for over-engineering and unnecessary abstractions |
| `/ponytail-debt` | Surface `// ponytail:` tagged shortcuts and their upgrade paths |
| `/ponytail-review` | Review diff/PR for complexity debt |

### Dev Workflow Skills

| Skill | What it does |
|-------|-------------|
| `/security-audit [scope] [path]` | Full codebase security audit - secrets, injection, OWASP Top 10 across TS/Python/Swift/Java/PHP |
| `/dep-audit [--fix] [--unused] [--licenses]` | Dependency vulnerabilities, outdated packages, unused deps, license risks |
| `/test-coverage [path] [--threshold N]` | Coverage gap analysis + generate missing tests |
| `/hostinger-deploy [scaffold\|deploy\|checklist] [name]` | Deploy to Hostinger shared hosting via rsync |
| `/playwright-cli` | Playwright test generation and browser automation |
| `/next-best-practices` | (auto) Next.js best practices - App Router patterns, RSC, caching |
| `/nextjs-seo` | Next.js SEO setup - metadata, OG, sitemap, robots.txt |
| `/react-best-practices` | (auto) React patterns, hooks discipline, performance |
| `/api-design-patterns` | (auto) REST/GraphQL API design patterns |
| `/php-best-practices` | (auto) PHP patterns and idioms |
| `/php-error-handling` | (auto) PHP error handling patterns |
| `/php-security` | (auto) PHP security pitfalls and mitigations |
| `/php-testing` | (auto) PHP testing with PHPUnit/Pest |

### Design / UI Skills

| Skill | What it does |
|-------|-------------|
| `/design-bakeoff` | Full website design pipeline - diverging variants, objective gates, real-pixel judging, taste profile |
| `/impeccable [target]` | Frontend UI review - UX, visual hierarchy, accessibility, motion, design systems |
| `/design-an-interface` | Design a UI interface from scratch |
| `/emil-design-eng` | (auto) Emil Kowalski's UI polish philosophy - animation, invisible details |

### Video / Motion Skills

| Skill | What it does |
|-------|-------------|
| `/hyperframes` | Hyperframes video framework (core orchestrator) |
| `/remotion` | Remotion video creation in React |
| `/remotion-to-hyperframes` | (auto) Migrate Remotion projects to Hyperframes |
| `/motion-graphics` | Motion graphics design and animation |
| `/gsap-core` | (auto) GSAP animation library - core, ScrollTrigger, timeline, plugins, React, performance, utils |
| `/general-video` | General video production workflow |
| `/faceless-explainer` | Faceless explainer video creation |
| `/embedded-captions` | Burn subtitles/captions into video |
| `/graphic-overlays` | Motion graphic overlays for video |
| `/pr-to-video` | Convert PR/diff into explainer video |
| `/product-launch-video` | Product launch video production |
| `/website-to-video` | Convert website/design to video walkthrough |
| `/slideshow` | Create animated slideshow |
| `/stitch-skill` | (auto) Stitch video clips together |

### Utility Skills

| Skill | What it does |
|-------|-------------|
| `/humanizer` | Remove AI-sounding patterns from text |
| `/grill-me` | Stress-test a plan via relentless interviewing |
| `/grill-with-docs` | Grill mode with documentation context |
| `/handoff` | Compact conversation into handoff doc for another agent |
| `/write-a-skill` | Generate a new skill definition |

---

## Rules

Rules in `rules/` loaded by Claude on demand. `CLAUDE.md` specifies when to load each set.

### Language Rules (loaded per language)

Each language folder (`typescript/`, `python/`) contains `coding-style.md`, `patterns.md`, `testing.md`, `security.md`.

---

## Settings (`settings.json`)

**Permissions** - pre-approved tools that skip prompts:
`Read`, `Write`, `Edit`, `Glob`, `Grep`, `git`, `gh`, `npm`, `node`, `python3`, `swift`, `find`, `grep`, `ls`, `pnpm`, `tsc`, `npx`, select Chrome extension tools

**Statusline** - runs `statusline-command.sh` in the terminal.

**Hooks** - `caffeinate` keep-awake (PreToolUse/Stop) and a notification sound (Notification).

**Plugins** - ponytail enabled; apple-skills disabled by default.

---

## CLAUDE.md (Global Rules Summary)

- Never mutate - always return new copies
- Files 200-400 lines typical, functions <50 lines
- Research before writing anything new (GitHub, registries, docs)
- No hardcoded secrets, validate all input at boundaries
- 80%+ test coverage, TDD mandatory (RED -> GREEN -> REFACTOR)
- Touch only what the request requires
- State bug, show fix, stop - no extra suggestions during review
- No em dashes or smart quotes in output
- `docs/` is single source of truth for all project documentation
