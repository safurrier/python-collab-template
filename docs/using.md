# Using in Your Repo

Each agent is independent. Add only the ones you want.

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

## Add an agent to a repo

### Step 1 — Create the caller workflow file

Create `.github/workflows/ai_pr_review.yml` in your target repo with the agents you want. Each agent is a separate job.

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
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_review.yml@v1
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
    uses: safurrier/python-collab-template/.github/workflows/context_files_agent.yml@v1
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

**Both agents together** — put them in one file as separate jobs:

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
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_review.yml@v1
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  context-files:
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/context_files_agent.yml@v1
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

Open a draft PR, then mark it **Ready for review**. The workflow should appear in the **Actions** tab and Claude should post output to the PR within a minute or two.

---

## Customizing a prompt

Every agent accepts a `prompt_override` input that replaces the default prompt entirely. Use this when you want different review criteria for a specific repo.

```yaml
jobs:
  review:
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_review.yml@v1
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    with:
      prompt_override: |
        You are reviewing a security-sensitive payments service.
        Flag any use of eval(), exec(), unsanitized SQL, or raw HTTP calls.
        Produce a pass/fail verdict with severity ratings.
```

The context files agent additionally accepts `agent_args` to control mode and scope without needing a full override:

```yaml
jobs:
  context-files:
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/context_files_agent.yml@v1
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    with:
      agent_args: "auto src/"   # scope to src/ instead of repo root
```

---

## Trigger policy reference

| Event | Review agent | Context files agent |
|---|---|---|
| PR opened as draft | Skipped | Skipped |
| Draft PR gets new commits | Skipped | Skipped |
| PR marked Ready for review | Runs | Runs |
| New commits pushed to open PR | Runs | Not triggered |
| Closed PR reopened | Runs (if not draft) | Not triggered |
| PR first opened (non-draft) | Not triggered | Runs |

---

## Private vs public repos

Use `pull_request` (not `pull_request_target`) — this is the correct event for repos without forks. The `ANTHROPIC_API_KEY` secret is accessible to `pull_request` workflows run from branches in the same repo.

If your central workflow repo (this one) is **private**, target repos must be granted access: **Settings → Actions → Access → Accessible from repositories in your account**.
