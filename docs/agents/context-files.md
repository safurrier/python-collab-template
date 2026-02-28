# Context Files Agent

Keeps `AGENTS.md` and `CLAUDE.md` up to date in a repository. When these files are missing, Claude generates them from scratch. When they exist, Claude audits and updates them to reflect the current codebase.

## Files

| File | Path |
|---|---|
| Skill | `skills/context-files/SKILL.md` |
| Workflow (shared) | `.github/workflows/claude_pr_agent.yml` |

## Skill frontmatter

```yaml
---
name: context-files
description: Create, update, or evaluate AGENTS.md and CLAUDE.md files for a repository. Follows WHY/WHAT/HOW structure with validated commands and progressive disclosure.
argument-hint: "[mode] [scope]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---
```

The `argument-hint` documents what the `args:` workflow input expects. The frontmatter is stripped at load time — Claude only sees the body.

## What it does

Claude reads the repo structure, config files, CI workflows, and any existing context docs, then:

1. **If no context files exist** (`auto` → `quick-start` mode): generates `AGENTS.md` with a WHY/WHAT/HOW structure and creates `CLAUDE.md` as a symlink
2. **If files already exist** (`auto` → `update + evaluate` mode): validates commands, removes stale content, improves conciseness, and creates nested `AGENTS.md` files for subdirectories with distinct workflows
3. **Commits the result** directly to the PR branch so the updated context files are part of the PR

Every command in the generated docs is validated against Makefiles, CI configs, or package manifests before being included.

## Output files

| File | Role |
|---|---|
| `AGENTS.md` | Source of truth — WHY/WHAT/HOW, validated commands, progressive disclosure pointers |
| `CLAUDE.md` | Symlink to `AGENTS.md` (Claude Code auto-discovers `CLAUDE.md` files) |
| `ai_agent_docs/*.md` | Cross-cutting topic docs created when content warrants it |
| `<subdir>/AGENTS.md` | Nested docs for subdirectories with distinct tooling |

## Triggers

| Event | Runs? |
|---|---|
| PR first opened (non-draft) | Yes |
| PR marked Ready for review | Yes |
| New commits pushed to open PR | No |
| Draft PR | No |

## Minimal caller workflow

```yaml
name: Context files agent

on:
  pull_request:
    types: [opened, ready_for_review]

concurrency:
  group: context-files-${{ github.repository }}-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  context-files:
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_agent.yml@v1
    with:
      skill: "context-files"
      args: "auto ."
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Customizing scope or mode

Pass mode and scope via the `args:` input (substituted for `$ARGUMENTS` in the skill):

```yaml
with:
  skill: "context-files"
  args: "auto src/"         # scope to src/ only
  # args: "quick-start ."  # always generate fresh, never update
  # args: "evaluate ."     # audit and report in chat without writing
```

Modes:

| Mode | Behavior |
|---|---|
| `auto` (default) | Generate if missing; update + evaluate if present. No confirmation prompts. |
| `quick-start` | Generate from scratch. Asks before overwriting existing files. |
| `update` | Update existing files only. |
| `evaluate` | Audit and propose improvements without modifying files. |

## Use a local skill from the target repo

Target repos can override the central skill entirely with their own `SKILL.md`:

```yaml
with:
  skill: ".claude/skills/context-files"   # loads from target repo
  args: "auto ."
```

Or use a raw prompt for a simpler custom format:

```yaml
with:
  prompt: |
    Look at this repo and create AGENTS.md with:
    1. A one-sentence description of what the repo does
    2. How to run tests
    3. How to run the linter
    Keep it under 30 lines.
```

## Permissions

```yaml
permissions:
  contents: write      # required: commits AGENTS.md / CLAUDE.md to the branch
  pull-requests: write
  issues: write
```
