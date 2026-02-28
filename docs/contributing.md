# Contributing a New Agent

Adding an agent takes **two files and a tag bump** — a skill file and a doc page. No new workflow needed.

## The pattern

```
skills/
  <your-skill-name>/
    SKILL.md          ← frontmatter + prompt body

docs/agents/
  <your-skill-name>.md   ← doc page
```

The generic `claude_pr_agent.yml` workflow already handles loading, frontmatter stripping, `$ARGUMENTS` substitution, and running Claude. You only need to write the skill content.

---

## Step 1 — Write the skill

Create `skills/<your-skill-name>/SKILL.md`:

```markdown
---
name: your-skill-name
description: One sentence describing what this skill does and when to use it.
argument-hint: ""
allowed-tools: Read, Grep, Glob, Bash
---

Your prompt body here. This is what Claude receives — the frontmatter above
is stripped before the body is sent.

Write the prompt as you'd write a Claude system prompt:
- Be specific about the output format (what Claude should post, commit, or return)
- Describe the scope (diff only? full repo? specific files?)
- If parameterizable, use $ARGUMENTS and document it in argument-hint
- Keep it focused — one skill, one job
```

**Frontmatter fields:**

| Field | Required | Notes |
|---|---|---|
| `name` | Recommended | Machine name, matches directory name |
| `description` | Recommended | One line; shown in docs and used by Claude Code for auto-invocation |
| `argument-hint` | If using `$ARGUMENTS` | Documents what the `args:` input expects, e.g. `"[mode] [scope]"` |
| `allowed-tools` | Optional | Documents which Claude tools the skill uses |

The frontmatter is **metadata for the framework** — it's stripped ("yanked") before Claude sees the content. Only the markdown body goes to Claude.

**If the skill uses `$ARGUMENTS`:** the workflow substitutes the `args:` input at runtime via `sed`. Default `args` is empty string if not provided.

**Permissions:** `claude_pr_agent.yml` always requests `contents: write`. No changes needed for skills that only read; skills that commit files just work.

---

## Step 2 — Write the doc page

Create `docs/agents/<your-skill-name>.md`. Include:

- What it does (1–2 sentences)
- Files table (skill path + shared workflow)
- Skill frontmatter block (for reference)
- Trigger event table (what events make sense for this skill)
- Minimal caller workflow (copy-paste ready)
- Customization options (`args:`, `skill:` path override, `prompt:` bypass)
- Permissions note

Then add it to the nav in `mkdocs.yml`:

```yaml
nav:
  - Agents:
    - Overview: agents/index.md
    - PR Code Review: agents/pr-review.md
    - Context Files: agents/context-files.md
    - Your Skill: agents/your-skill-name.md   # add this
```

And add a row to the table in `docs/agents/index.md`.

---

## Step 3 — Tag a new release

```bash
git add skills/<your-skill-name>/ docs/agents/<your-skill-name>.md docs/agents/index.md mkdocs.yml
git commit -m "feat: add <your skill name> skill"
git tag v1.1   # bump to next semver
git push origin main --tags
```

Target repos update their `uses: ...@v1` → `@v1.1` to pick up the new skill.

---

## Minimal caller workflow for a new skill

```yaml
name: Your skill name

on:
  pull_request:
    types: [ready_for_review, synchronize, reopened]

concurrency:
  group: your-skill-${{ github.repository }}-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  your-skill:
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_agent.yml@v1
    with:
      skill: "your-skill-name"
      # args: "some args"     # if skill uses $ARGUMENTS
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## Checklist

- [ ] `skills/<name>/SKILL.md` — frontmatter + prompt body
- [ ] `name` field matches directory name
- [ ] `argument-hint` set if skill uses `$ARGUMENTS`
- [ ] `docs/agents/<name>.md` — doc page with trigger table and caller snippet
- [ ] Row added to `docs/agents/index.md`
- [ ] Entry added to `mkdocs.yml` nav
- [ ] New semver tag pushed
