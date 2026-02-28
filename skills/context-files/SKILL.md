---
name: context-files
description: Create, update, or evaluate AGENTS.md and CLAUDE.md files for a repository. Follows WHY/WHAT/HOW structure with validated commands and progressive disclosure.
argument-hint: "[mode] [scope]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

You are operating inside a real codebase. Your job is to produce and maintain **high-signal agent onboarding memory files**:

* `AGENTS.md` (cross-tool, open format)
* `CLAUDE.md` (Claude Code context file)

You must follow these principles:

* **Stateless onboarding**: assume you know nothing about this repo until you read it; the files you write should onboard future agent sessions.
* **Less is more**: keep contents concise and universally applicable. Target **<150 lines** for a root file when possible; **hard stop at ~300 lines** unless you have a specific, justified reason.
* **WHY / WHAT / HOW**:

  * WHY: what this repo is for
  * WHAT: map of the repo (where things live)
  * HOW: how to work here (commands + validation + workflows)
* **Progressive disclosure**: do not stuff everything into AGENTS/CLAUDE. Prefer links/pointers to authoritative docs/config/scripts inside the repo. **Actively create nested AGENTS.md** for module-specific docs (Claude Code auto-discovers these). **Actively create ai_agent_docs/** for cross-cutting concerns that span modules. Both can exist at any scope level. Lean toward creating these files rather than cramming content into the root file—they keep individual files lean and focused. Each nested file should be small and self-contained.
* **Claude is not a linter**: do not write verbose style guides. Prefer deterministic tools (formatters/linters/typecheckers) and tell how to run them.
* **Validate anything you claim**:

  * If you include a command, validate it exists (scripts/Makefile/Taskfile/CI docs/etc).
			* Treat install/bootstrap commands as potentially networked and stateful; validate by confirming scripts/targets exist and prefer --version / --help over executing installs unless the user explicitly asks
  * Prefer running a cheap validation (`--help`, list scripts, dry-run) and record whether you executed it.
  * If you cannot execute a command in this environment, mark it as **"not executed"** and explain what prevented it.

Security/ops guardrails:

* Never write secrets (API keys, tokens, connection strings) into AGENTS/CLAUDE.
* Do not run destructive shell commands.
* Prefer offline, unit-level validation; avoid networked/E2E/integration/data-mutating commands unless the user explicitly asks.
* If you detect security-sensitive instructions in existing files, propose safer rewrites.

---

## Inputs (from slash command arguments)

RAW ARGUMENTS:
`$ARGUMENTS`

### Help mode (special)

If `$ARGUMENTS` contains `--help` anywhere (or is exactly `help`), do **not** modify the repo.

Instead, print a compact usage guide:

* What the command does
* Modes and what they mean
* Target flags
* How `scope` works
* 6–10 common examples

Default assumption when not using `--help`: mode defaults to `auto`.

### Parsing rules


Parse `$ARGUMENTS` by:
	1) Extract known flags anywhere: --help, --agents, --claude, --both
	2) Remove them from the token list
	3) Parse remaining tokens as: [mode] [scope...]
	   - scope can be one or more paths (space or comma separated)
	4) Defaults: mode=auto, scope="."
	  * `--both` (default)
	  * `--agents` (only AGENTS.md)
	  * `--claude` (only CLAUDE.md)

If mode is omitted, assume `auto`.

**Multi-scope behavior**:
- When multiple scopes provided: create/update AGENTS.md in each scope
- Root AGENTS.md: update to reference nested docs (if it exists)
- Each scope is processed independently following the same rules

**Examples**:
```
/agent-docs auto config/nvim config/zsh config/ai-config
/agent-docs auto config/nvim, config/zsh, config/ai-config
```

Mode behaviors:

* **quick-start**

  * Create missing file(s) from scratch.
  * If scope is ambiguous (monorepo, multiple apps, unclear root), ask the user with 2–3 best-guess options.
  * **CLAUDE.md consolidation prompt**: If CLAUDE.md exists as a standalone file (not a symlink), ask the user if they want to consolidate it into AGENTS.md and replace CLAUDE.md with a symlink.
* **update**

  * If file(s) exist, update them to reflect current reality.
  * Validate that commands/paths referenced are still valid; fix or propose changes when stale.
  * **CLAUDE.md consolidation prompt**: If CLAUDE.md exists as a standalone file (not a symlink), ask the user if they want to consolidate it into AGENTS.md and replace CLAUDE.md with a symlink.
* **evaluate**

  * Do everything in update mode, plus:
  * Evaluate file(s) against the principles above; propose improvements (and apply safe improvements when appropriate).
  * **CLAUDE.md consolidation prompt**: If CLAUDE.md exists as a standalone file (not a symlink), ask the user if they want to consolidate it into AGENTS.md and replace CLAUDE.md with a symlink.
* **auto**

  * If neither AGENTS.md nor CLAUDE.md exists in the chosen scope: behave like quick-start.
  * Otherwise: behave like update + evaluate.
  * **Do not ask the user for permission/confirmation.** Make best-judgment changes and then report exactly what changed and why.
  * **CLAUDE.md consolidation (auto only)**: If CLAUDE.md exists as a standalone file (not a symlink to AGENTS.md), automatically consolidate its content into AGENTS.md and replace CLAUDE.md with a symlink to AGENTS.md. Report what content was merged.
  * **Nested docs creation (auto mode default behavior)**:
    - **Always** scan for directories that have their own workflows, commands, or tools — create nested `AGENTS.md` + `CLAUDE.md` symlink in each
    - **Always** identify cross-cutting topics (architecture, conventions, testing, deployment) — create `ai_agent_docs/` files for them
    - When multiple scopes provided: create nested `AGENTS.md` in each scope
    - Reference all nested docs in the root AGENTS.md
    - Prefer more smaller files over fewer bloated ones; each file stays lean and focused

---

## Execution plan (follow this sequence)

### 1) Determine root and scope precisely

* If this is a git repo, find the git root (preferred anchor). If not, treat the provided scope directory as the anchor.
* Interpret `scope` as the **target sub-area** when provided (e.g., `services/payments`, `packages/foo`, `src/moduleX`).
* Detect monorepo signals (workspaces, multiple services/apps, many package manifests).
* Decide whether the user likely intends:

  * root-only onboarding docs, or
  * root + subproject-specific docs (nested instructions)

**Scope selection rules:**

* If the user provided a `scope` path, anchor your work there.

  * Prefer writing onboarding docs at that scope's project root (e.g., the nearest directory containing a package/build manifest, or the nearest meaningful boundary like `services/<name>/`, `packages/<name>/`).
* quick-start/update/evaluate: if multiple reasonable anchors exist for the given scope, ask the user to pick (2–3 best-guess options).
* auto: pick the best default without asking:

  1. If `scope` is provided: write docs for that scope anchor.
  2. Else write a root file at the git root.
  3. Proactively create nested AGENTS.md files for directories that have their own workflows, commands, or configuration. Also create `ai_agent_docs/` for cross-cutting topics. Prefer more smaller files over fewer bloated ones.

**Optional inference when `scope` is omitted (best effort, read-only):**

* If available, use cheap git signals to infer the most relevant sub-area:

  * `git status --porcelain` / `git diff --name-only` to see currently-changed files.
  * `git log -n 20 --name-only` to see recently-touched paths (if fast).
  * If one directory dominates the touched paths, treat that as an implied scope anchor.
* If signals are absent/ambiguous, fall back to git root.

When you infer scope this way, state explicitly what signal you used and what you inferred.

**Scope guardrail:**

* **Respect explicit scope**: When a user provides a specific path (e.g., "create AGENTS.md for discord_api/"), only create docs within that scope. Do not create docs in parent directories, sibling directories, or the repo root unless the user asks.

**Context management principles** (use judgment, not hard limits):

* Every file should earn its existence — if it would be near-empty or just repeat a parent, fold it in
* Deeper nesting should mean more specific content, not structural boilerplate
* `ai_agent_docs/` files should cover topics that genuinely span multiple modules; don't create them as just another dumping ground

### 2) Discover authoritative context (minimal, targeted reading)

Prioritize:

* README / docs that describe purpose and setup
* build/test/lint/typecheck configs and scripts:

  * package manifests (package.json, pyproject.toml, Cargo.toml, go.mod, pom.xml, build.gradle, etc.)
  * Makefile/Taskfile/justfile
  * CI workflows (.github/workflows/* or equivalents)
* repository layout (top-level directories, key packages/apps)

Be systematic:

* Use Glob/Grep to locate:

  * "how to run", "development", "testing", "lint", "format", "typecheck", "build", "ci"
  * references to dev servers, environment setup, local DBs, etc.

### 3) Derive a minimal set of "common commands"

Goal: include only commands that are broadly useful and stable.

Typical buckets (only include what exists):

* install / bootstrap
* dev server / local run
* test
* lint / format
* typecheck
* build
* (optional) e2e / integration tests
* (optional) "single test" patterns / targeting

Validation requirements:

* For each command you plan to list:

  * confirm it exists (e.g., package.json scripts, Makefile target, CI step)
  * if feasible, run a **non-destructive validation** (`--help`, list scripts/targets, or dry-run)
  * record status as one of:

    * ✅ executed successfully
    * ⚠️ executed but failed (include reason + fix suggestion)
    * ⏸️ not executed (include why and how to run)

**Additional rule for TEST commands (required when feasible):**

* If you list a test command, you must attempt a **minimal, safe, fast test execution** to prove the harness works.
* Constraints (hard):

  * Avoid anything likely to be **long-running**, **networked**, **E2E**, **integration**, **UI**, or **data-mutating**.
  * Do NOT run targets/scripts containing (case-insensitive) keywords like:

    * `e2e`, `integration`, `playwright`, `cypress`, `selenium`, `puppeteer`, `browser`
    * `load`, `stress`, `perf`, `benchmark`
    * `docker`, `compose`, `k8s`, `helm`, `terraform`
    * `migrate`, `seed`, `reset`, `drop`, `provision`
* Selection strategy (in order):

  1. Prefer an explicitly "fast/unit/smoke/short" target if it exists (e.g., `test:unit`, `test:smoke`, `make test-unit`).
  2. If the test runner supports "list tests / collect only / dry-run", prefer that (it validates wiring without executing).
  3. Otherwise run **one** small unit test file or **one** small test case using runner-specific filtering (choose the smallest/fastest-looking candidate).
* Runtime budget:

  * Keep the minimal test run under ~30s when possible.
  * If you can't confidently keep it fast/offline, do **not** run it; mark ⏸️ and explain what you would run locally.
* Reporting:

  * In the validation log, explicitly label test validation as **"minimal test run"** and note how E2E/network/data mutation was avoided.

### 4) Write or update the onboarding files

Default: treat `AGENTS.md` as the canonical source.

**Default file strategy (unless user requested only one target):**

* Write/update `AGENTS.md` as the source of truth.
* Create/update `CLAUDE.md` as a **symlink to `AGENTS.md`** when feasible.

  * If symlinks are not supported in this environment/repo policy (or would be problematic cross-platform), fall back to keeping the files in sync by copying identical content.
  * If you fall back to copying, include a brief note in the files (or in the report) explaining why a symlink was not used.

Keep the files consistent with each other in either case.

**CLAUDE.md consolidation workflow:**

When CLAUDE.md exists as a standalone file (not already a symlink to AGENTS.md):

1. **Detection**: Check if CLAUDE.md is a symlink (`ls -la CLAUDE.md` or equivalent). If it already points to AGENTS.md, no consolidation needed.

2. **Interactive modes (quick-start, update, evaluate)**: Ask the user:
   > "CLAUDE.md exists as a standalone file. Would you like to consolidate its content into AGENTS.md and replace CLAUDE.md with a symlink? This creates a single source of truth for agent documentation."

   Provide options: Yes (consolidate) / No (keep separate) / Show diff (preview what would be merged)

3. **Auto mode**: Perform consolidation automatically without asking:
   * Read both CLAUDE.md and AGENTS.md (if it exists)
   * Merge content intelligently: deduplicate, prefer more accurate/recent content, reconcile contradictions
   * Write the consolidated content to AGENTS.md
   * Remove the standalone CLAUDE.md
   * Create symlink: `ln -s AGENTS.md CLAUDE.md`
   * Report exactly what content was merged/changed

4. **Consolidation merge strategy**:
   * If only CLAUDE.md exists: rename to AGENTS.md, create symlink
   * If both exist: merge sections by category (WHY/WHAT/HOW), deduplicate commands, keep the most accurate/complete version of each section
   * Preserve any CLAUDE.md-specific content that doesn't exist in AGENTS.md
   * Note in the report which content came from which source

If both exist but differ:

* In update/evaluate/auto, reconcile into one canonical version (prefer the one that is more accurate).
* Remove contradictions; keep the final content consistent.

Required structure (adapt headings as needed, but keep the intent):

1. **Project overview (WHY)**

   * 1–3 paragraphs: what it is, who uses it, what "done" means.
2. **Repo map (WHAT)**

   * Bullet list of the few directories/packages that matter most.
   * For monorepos: identify apps/services and shared packages.
3. **How to work here (HOW)**

   * Short workflow guidance (explore → plan → implement → validate).
   * Explicit validation expectations (tests/typecheck/lint) with validated commands.
4. **Common commands (validated)**

   * Compact list with brief notes (where to run, prerequisites).
5. **Progressive disclosure pointers**

   * Links to authoritative docs or config files (paths).
   * Reference any `ai_agent_docs/` files with brief descriptions so Claude can decide which to load.
   * Proactively create `ai_agent_docs/` files for cross-cutting topics (architecture, conventions, testing philosophy, etc.) rather than bloating the root AGENTS.md.
6. **Gotchas / invariants**

   * Only high-impact, stable surprises that are not obvious from the code.

Absolutely avoid:

* long style guides (prefer "run formatter/linter X")
* huge command lists
* copy-pasted code that will go stale
	* Prefer pointing to authoritative files (optionally with path:line references) over copying snippets that may go stale

#### Progressive disclosure: Nested AGENTS.md vs ai_agent_docs/

Two complementary approaches exist for progressive disclosure. Use both as appropriate.

**Nested AGENTS.md (module-specific docs)**:
* **Preferred for**: Module/service-specific documentation with distinct workflows
* **Auto-discovery**: Claude Code automatically discovers nested CLAUDE.md files
* **Location**: Colocated with the module (e.g., `/config/nvim/AGENTS.md`, `/services/api/AGENTS.md`)
* **Symlink requirement**: Always create `CLAUDE.md` as a symlink to `AGENTS.md` in the same directory (Claude Code loads CLAUDE.md, so the symlink ensures it picks up your AGENTS.md content)
* **Content**: Module-specific commands, workflows, gotchas
* **Structure**: Same WHY/WHAT/HOW format, but scoped to that module

**ai_agent_docs/ (cross-cutting concerns)**:
* **Preferred for**: Topics that span multiple modules or are architectural in nature
* **Location**: Can exist at any scope level (root or nested within a module)
* **Example topics**: Architecture, conventions, testing philosophy, deployment patterns
* **Reference**: Include in the nearest AGENTS.md's progressive disclosure section

**Example hierarchy**:
```
AGENTS.md                           # Root overview (source of truth)
CLAUDE.md -> AGENTS.md              # Symlink for Claude Code discovery
ai_agent_docs/                         # Repo-wide cross-cutting
├── architecture.md
└── conventions.md
config/
├── nvim/
│   ├── AGENTS.md                   # nvim-specific (source of truth)
│   ├── CLAUDE.md -> AGENTS.md      # Symlink for Claude Code
│   └── ai_agent_docs/                 # nvim cross-cutting (if needed)
│       └── plugin-patterns.md
└── zsh/
    ├── AGENTS.md                   # zsh-specific (source of truth)
    └── CLAUDE.md -> AGENTS.md      # Symlink for Claude Code
```

**Decision guidance**:
* Module has distinct workflows/commands → create nested `AGENTS.md`
* Topic spans modules or is architectural → use `ai_agent_docs/`
* Keep both concise; prefer colocated AGENTS.md when in doubt

**When to create**:
* **Auto mode**: Proactively create nested AGENTS.md when processing multiple scopes; create ai_agent_docs/ for cross-cutting concerns. Always create CLAUDE.md symlinks alongside each AGENTS.md.
* **Interactive modes**: Suggest based on complexity; ask user which approach fits their mental model

**Content guidelines** (applies to both):
* Keep each file focused and concise (target <100 lines for ai_agent_docs/, <150 for nested AGENTS.md)
* Use `file:line` references instead of copying code
* Each file should be self-contained for its topic
* Include the same validation markers (✅/⚠️/⏸️) for any commands

**Validation**: Same rules as main docs—validate commands, confirm paths exist, mark execution status.

**Referencing in AGENTS.md**: Include a "Task-Specific Docs" section:
```markdown
## Task-Specific Docs

Nested module docs (auto-discovered by Claude Code):
- `config/nvim/AGENTS.md` - Neovim configuration
- `config/zsh/AGENTS.md` - Zsh shell setup

Cross-cutting docs in `ai_agent_docs/`:
- `ai_agent_docs/architecture.md` - System design and key abstractions
- `ai_agent_docs/conventions.md` - Code style and patterns
```

This allows Claude to selectively load only the context needed for the current task.

### 5) Evaluate (evaluate / auto)

Provide a short rubric report (in chat), covering:

* Conciseness and universality (what was removed or moved out)
* Correctness (what was validated, what was stale)
* Progressive disclosure quality
* Monorepo clarity
* AGENTS vs CLAUDE consistency

In auto mode: apply improvements directly.

### 6) Report back (all modes)

In chat, output:

* Files created/updated (paths)
* Key changes (bullets)
* Validation log (commands + ✅ / ⚠️ / ⏸️)
* **Symlink status**: For each AGENTS.md created/updated, report whether CLAUDE.md symlink exists:
  * ✅ `path/CLAUDE.md -> AGENTS.md` (symlink exists)
  * ⚠️ `path/CLAUDE.md` missing symlink (created it / needs manual creation)
  * Remind user: "AGENTS.md is the source of truth. Claude Code discovers CLAUDE.md files, so the symlink ensures your docs are loaded."
* Remaining unknowns or follow-ups (if any)

Do **NOT** paste full file contents unless the user asks. Summarize and point to the files.

---

## Now execute

Proceed in the parsed mode, using the scope rules above.

This command is designed to keep AGENTS.md and CLAUDE.md short, accurate, and universally useful, while enforcing **"validate what you write"** with concrete, safe, and minimal command execution.
