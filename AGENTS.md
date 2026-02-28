# AGENTS.md

## WHY — What this repo is

Central GitHub Actions workflow host for **Claude PR agents** — reusable, prompt-driven automation that attaches to pull requests. Instead of duplicating workflow logic across repos, any target repo references this one with a single `uses:` line and gets automated code review, context file generation, or any other Claude-powered task.

The repo is intentionally minimal: workflow YAML, prompt files, and documentation. No build system, no runtime dependencies.

---

## WHAT — Repo map

```
.github/workflows/
  claude_pr_agent.yml       # Reusable: generic skill runner (workflow_call)
  ai_pr_review.yml          # Caller example: code review for this repo
  context_files_pr.yml      # Caller example: context files agent for this repo
  docs.yml                  # MkDocs build + GitHub Pages deploy

skills/
  codex-code-review/
    SKILL.md                # Codex Code Review prompt (verbatim body + frontmatter)
  context-files/
    SKILL.md                # Context files generator/updater prompt (with $ARGUMENTS)

docs/                       # MkDocs documentation site source
  index.md                  # Overview and architecture
  user-stories.md           # Who uses this and why
  using.md                  # Step-by-step setup for target repos
  contributing.md           # How to add a new agent
  agents/
    index.md                # Agent catalog
    pr-review.md            # Code review skill docs
    context-files.md        # Context files skill docs
```

---

## HOW — How to work here

### Adding a new agent

1. Create `skills/<name>/SKILL.md` — YAML frontmatter + prompt body (frontmatter is stripped before Claude sees it)
2. Create `docs/agents/<name>.md` — trigger table, caller snippet, customization options
3. Add entry to `docs/agents/index.md` and `mkdocs.yml` nav
4. Tag a new release: `git tag vX.Y && git push origin vX.Y`

No new workflow file needed — `claude_pr_agent.yml` handles all skills generically.

See `docs/contributing.md` for the full checklist.

### Updating a skill

Edit `skills/<name>/SKILL.md`. Bump the version tag so target repos can opt in to the updated skill on their own schedule.

### Working on docs

```bash
# Preview locally (requires mkdocs-material)
pip install mkdocs-material
mkdocs serve
```
⏸️ Not executed — requires network install. Confirm `mkdocs.yml` exists: ✅

```bash
# Strict build (catches broken links, missing pages)
mkdocs build --strict
```
⏸️ Not executed — same prerequisite.

### Validating workflow YAML

```bash
yamllint .github/workflows/
```
⏸️ Not executed — `yamllint` not confirmed in this environment. Workflows are validated by GitHub Actions on push.

---

## Common commands (validated)

| Command | Status | Notes |
|---|---|---|
| `mkdocs serve` | ⏸️ not executed | Requires `pip install mkdocs-material`; run from repo root |
| `mkdocs build --strict` | ⏸️ not executed | Same prerequisite; used in CI (`docs.yml`) |
| `git tag vX.Y && git push origin vX.Y` | ⏸️ not executed | Release process; target repos pin to these tags |

No test suite, linter, or build step for the workflows themselves — validation happens when GitHub Actions parses them on push.

---

## Progressive disclosure

- `docs/using.md` — full setup walkthrough for target repos
- `docs/contributing.md` — step-by-step skill contribution guide
- `docs/agents/pr-review.md` — review skill: triggers, local skill override, sequencing
- `docs/agents/context-files.md` — context files skill: modes, `args`, local override
- `.github/workflows/claude_pr_agent.yml` — canonical source for the generic skill runner
- `skills/context-files/SKILL.md` — canonical source for context files skill spec

---

## Gotchas

- **Repo rename breaks callers**: `claude_pr_agent.yml` hard-codes `repository: safurrier/python-collab-template` to check out the skills. If this repo is renamed, update that field.
- **Private repo access**: if this repo is private, target repos must be granted access via Settings → Actions → Access → "Accessible from repositories in your account".
- **Tag before using**: target repos reference `@v1` (or another tag). Push a tag before pointing any repo at this one.
- **`contents: write` always on**: the generic workflow always requests `contents: write` so any skill can commit files. This is intentional.
- **`$ARGUMENTS` substitution**: skills use a `$ARGUMENTS` placeholder that the workflow substitutes via `sed` at runtime using the `args:` input. It is not a shell variable — do not use `${ARGUMENTS}` or `$ARGS`.
- **Frontmatter stripping**: the `awk` command in the workflow strips everything between the first and second `---` blocks. The skill body starts on the line after the closing `---`.
