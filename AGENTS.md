# AGENTS.md

## WHY — What this repo is

Central GitHub Actions workflow host for **Claude PR agents** — reusable, prompt-driven automation that attaches to pull requests. Instead of duplicating workflow logic across repos, any target repo references this one with a single `uses:` line and gets automated code review, context file generation, or any other Claude-powered task.

The repo is intentionally minimal: workflow YAML, prompt files, and documentation. No build system, no runtime dependencies.

---

## WHAT — Repo map

```
.github/workflows/
  claude_pr_review.yml      # Reusable: code review agent (workflow_call)
  context_files_agent.yml   # Reusable: AGENTS.md / CLAUDE.md generator (workflow_call)
  ai_pr_review.yml          # Caller example: code review for this repo
  context_files_pr.yml      # Caller example: context files agent for this repo
  docs.yml                  # MkDocs build + GitHub Pages deploy

prompts/
  codex_code_review_prompt.md    # Verbatim Codex Code Review prompt (OpenAI cookbook)
  context_files_prompt.md        # Context files generator/updater prompt

docs/                       # MkDocs documentation site source
  index.md                  # Overview and architecture
  user-stories.md           # Who uses this and why
  using.md                  # Step-by-step setup for target repos
  contributing.md           # How to add a new agent
  agents/
    index.md                # Agent catalog
    pr-review.md            # Code review agent docs
    context-files.md        # Context files agent docs
```

---

## HOW — How to work here

### Adding a new agent

1. Create `prompts/<name>.md` — the Claude instruction text
2. Create `.github/workflows/<name>.yml` — copy an existing reusable workflow, swap the prompt filename, adjust permissions if the agent writes files
3. Create `docs/agents/<name>.md` — trigger table, caller snippet, customization options
4. Add entry to `docs/agents/index.md` and `mkdocs.yml` nav
5. Tag a new release: `git tag vX.Y && git push origin vX.Y`

See `docs/contributing.md` for the full checklist.

### Updating a prompt

Edit the file in `prompts/`. Bump the version tag so target repos can opt in to the updated prompt on their own schedule.

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
- `docs/contributing.md` — step-by-step agent contribution guide
- `docs/agents/pr-review.md` — code review agent: triggers, prompt override, permissions
- `docs/agents/context-files.md` — context files agent: modes, `agent_args`, permissions
- `.github/workflows/claude_pr_review.yml` — canonical source for reusable workflow structure
- `prompts/context_files_prompt.md` — canonical source for context files prompt spec

---

## Gotchas

- **Repo rename breaks callers**: the reusable workflows hard-code `repository: safurrier/python-collab-template` to check out the prompt files. If this repo is renamed, update that field in every reusable workflow.
- **Private repo access**: if this repo is private, target repos must be granted access via Settings → Actions → Access → "Accessible from repositories in your account".
- **Tag before using**: target repos reference `@v1` (or another tag). Push a tag before pointing any repo at this one.
- **`contents: write` scope**: the context files agent needs `contents: write` to commit `AGENTS.md` / `CLAUDE.md`. The review agent only needs `read`.
- **`$ARGUMENTS` substitution**: the context files prompt uses a `$ARGUMENTS` placeholder that the workflow substitutes via `sed` at runtime. Do not treat it as a shell variable in the prompt file itself.
