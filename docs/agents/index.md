# Agents

Each agent is a **skill** — a markdown file with YAML frontmatter — run by one generic reusable workflow.

```
skills/
  <name>/
    SKILL.md      ← frontmatter (metadata) + body (prompt sent to Claude)

.github/workflows/
  claude_pr_agent.yml   ← single generic workflow_call for all skills
```

Target repos reference `claude_pr_agent.yml` and pass a `skill:` name. The workflow checks out this central repo, strips the frontmatter from the skill file, substitutes any `$ARGUMENTS`, and runs `anthropics/claude-code-action`.

---

## Available skills

| Skill | Directory | What it does |
|---|---|---|
| [PR Code Review](pr-review.md) | `skills/codex-code-review/` | Reviews diff; posts findings and correctness verdict |
| [Context Files](context-files.md) | `skills/context-files/` | Creates or updates `AGENTS.md` / `CLAUDE.md` |

---

## Shared design principles

**Every skill:**

- Has YAML frontmatter (stripped before Claude sees it) with `name`, `description`, `argument-hint`, `allowed-tools`
- Uses `$ARGUMENTS` for runtime substitution when parameterizable
- Is independent — skills don't depend on each other

**The generic workflow (`claude_pr_agent.yml`):**

- Accepts a `skill:` name (central repo) or a target-repo-relative path (local skill)
- Accepts `args:` for `$ARGUMENTS` substitution
- Accepts `prompt:` as a raw prompt bypass (no skill file needed)
- Always has `contents: write` so any skill can commit files if needed

**Adding a new agent** = adding a `skills/<name>/SKILL.md` file + a doc page. No new workflow needed. See [Contributing](../contributing.md).
