# Using in Your Repo

Each skill is independent — add only the ones you want. All skills run through the same generic `claude_pr_agent.yml` workflow.

## Prerequisites

- An Anthropic API key ([get one here](https://console.anthropic.com/))
- Write access to your target repo
- This central repo tagged at `v1` (one-time, see below)

---

## One-time: tag this repo

Before any target repo can call a reusable workflow, you need a stable tag to pin to.

```bash
git tag v1
git push origin v1
```

Future releases follow the same pattern: `v1.1`, `v2`, etc. Target repos stay pinned to their chosen tag until you update the `uses:` line.

---

## Add skills to a repo

### Step 1 — Create the caller workflow

Create `.github/workflows/claude_agents.yml` in your target repo. Each skill is a separate job pointing at the same `claude_pr_agent.yml` workflow.

**Code review only:**

```yaml
name: Claude PR scan

on:
  pull_request:
    types: [ready_for_review, synchronize, reopened]

concurrency:
  group: claude-pr-scan-${{ github.repository }}-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  review:
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_agent.yml@v1
    with:
      skill: "codex-code-review"
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

**Context files only:**

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

**Both skills, sequenced** — review runs first, context-files waits for it:

```yaml
name: Claude PR agents

on:
  pull_request:
    types: [opened, ready_for_review, synchronize, reopened]

concurrency:
  group: claude-agents-${{ github.repository }}-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  review:
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_agent.yml@v1
    with:
      skill: "codex-code-review"
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  context-files:
    needs: review
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_agent.yml@v1
    with:
      skill: "context-files"
      args: "auto ."
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Step 2 — Add the secret

In your target repo: **Settings → Secrets and variables → Actions → New repository secret**

| Field | Value |
|---|---|
| Name | `ANTHROPIC_API_KEY` |
| Value | Your Anthropic API key |

### Step 3 — Open a PR and verify

Open a draft PR, then mark it **Ready for review**. The workflow appears in the **Actions** tab and Claude posts output to the PR within a minute or two.

---

## Customization options

### Use a raw prompt (no skill file)

For a one-off instruction without creating a skill:

```yaml
with:
  prompt: |
    Review this diff for security issues only.
    Flag any use of eval(), exec(), unsanitized SQL, or raw HTTP calls.
    Give a pass/fail verdict.
```

### Use a local skill from the target repo

Target repos can define their own `SKILL.md` files and pass the path:

```yaml
with:
  skill: ".claude/skills/team-conventions"   # .claude/skills/team-conventions/SKILL.md
  # OR
  skill: "./skills/security-review"          # skills/security-review/SKILL.md
  # OR
  skill: "./prompts/quick-check.md"          # flat .md file, no directory
```

This follows the Claude Code skill convention: paths containing `/` are resolved from the target repo checkout; bare names are resolved from the central repo's `skills/` directory.

### Mix central and local skills

```yaml
jobs:
  review:
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_agent.yml@v1
    with:
      skill: "codex-code-review"          # central repo skill
    secrets: { ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }} }

  conventions:
    needs: review
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_agent.yml@v1
    with:
      skill: ".claude/skills/api-conventions"   # target repo local skill
    secrets: { ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }} }
```

---

## Trigger policy reference

| Event | Review skill | Context files skill |
|---|---|---|
| PR opened as draft | Skipped | Skipped |
| Draft PR gets new commits | Skipped | Skipped |
| PR marked Ready for review | Runs | Runs |
| New commits pushed to open PR | Runs | Not triggered |
| Closed PR reopened (non-draft) | Runs | Not triggered |
| PR first opened (non-draft) | Not triggered | Runs |

---

## Private vs public repos

Use `pull_request` (not `pull_request_target`) — correct for repos without forks. The `ANTHROPIC_API_KEY` secret is accessible to `pull_request` workflows from branches in the same repo.

If this central workflow repo is **private**, target repos need access: **Settings → Actions → Access → Accessible from repositories in your account**.
