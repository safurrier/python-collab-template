# Context Files Agent

Keeps `AGENTS.md` and `CLAUDE.md` up to date in a repository. When these files are missing, Claude generates them from scratch. When they exist, Claude audits and updates them to reflect the current codebase.

## Files

| File | Path |
|---|---|
| Reusable workflow | `.github/workflows/context_files_agent.yml` |
| Prompt | `prompts/context_files_prompt.md` |

## What it does

Claude reads the repo structure, config files, CI workflows, and any existing context docs, then:

1. **If no context files exist** (`auto` → `quick-start` mode): generates `AGENTS.md` with a WHY/WHAT/HOW structure and creates `CLAUDE.md` as a symlink
2. **If files already exist** (`auto` → `update + evaluate` mode): validates commands, removes stale content, improves conciseness, and creates nested `AGENTS.md` files for subdirectories with distinct workflows
3. **Commits the result** directly to the PR branch so the updated context files are part of the PR

The prompt follows a strict principle: **validate what you write**. Every command in the generated docs is confirmed to exist in Makefiles, CI configs, or package manifests before being included.

## Output files

| File | Role |
|---|---|
| `AGENTS.md` | Source of truth for agent onboarding — WHY/WHAT/HOW, validated commands, progressive disclosure pointers |
| `CLAUDE.md` | Symlink to `AGENTS.md` (Claude Code auto-discovers `CLAUDE.md` files when navigating a repo) |
| `ai_agent_docs/*.md` | Cross-cutting topic docs (architecture, conventions, etc.) created when content warrants it |
| `<subdir>/AGENTS.md` | Nested docs for subdirectories with their own distinct tooling |

## Triggers

| Event | Runs? |
|---|---|
| PR first opened (non-draft) | Yes |
| PR marked Ready for review | Yes |
| New commits pushed to open PR | No (use review agent for that) |
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
    uses: safurrier/python-collab-template/.github/workflows/context_files_agent.yml@v1
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Customizing scope or mode

Use `agent_args` to change which directory Claude targets or which mode it runs in:

```yaml
with:
  agent_args: "auto src/"         # scope to src/ only
  # agent_args: "quick-start ."  # always generate fresh, never update
  # agent_args: "evaluate ."     # audit and propose improvements, report in chat
```

Modes:

| Mode | Behavior |
|---|---|
| `auto` (default) | Generate if missing; update + evaluate if present. No confirmation prompts. |
| `quick-start` | Always generate from scratch. Asks before overwriting. |
| `update` | Update existing files only. |
| `evaluate` | Audit files against quality principles and propose improvements. |

## Full prompt override

To replace the entire prompt (e.g., for a simpler or domain-specific context file format):

```yaml
with:
  prompt_override: |
    Look at this repo and create AGENTS.md with:
    1. A one-sentence description of what the repo does
    2. How to run tests
    3. How to run the linter
    Keep it under 30 lines.
```

## Permissions

```yaml
permissions:
  contents: write      # needed to commit AGENTS.md / CLAUDE.md to the branch
  pull-requests: write
  issues: write
```

Unlike the review agent, this one needs `contents: write` because it commits files.
