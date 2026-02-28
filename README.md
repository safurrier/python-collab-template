# Claude PR BugScan

Reusable GitHub Actions workflow that runs [Claude Code Action](https://github.com/anthropics/claude-code-action) to review PR diffs using the official Codex Code Review prompt.

## What this does

- Automatically reviews PRs when they transition from **Draft → Ready for review**
- Re-runs on **new commits pushed** to an open PR
- Skips draft PRs entirely
- Posts review output back to the PR as comments
- Uses the [official Codex Code Review prompt](https://developers.openai.com/cookbook/examples/codex/build_code_review_with_codex_sdk/) verbatim

## Repository layout

```
.github/workflows/
  claude_pr_review.yml   # Reusable workflow (workflow_call) — lives here
  ai_pr_review.yml       # Caller workflow for this repo (also an example)
prompts/
  codex_code_review_prompt.md   # Official Codex prompt text (verbatim)
```

## How to use this in another repo

This repo acts as the **central workflow host**. Any other repo can call the reusable workflow with three lines — no workflow code to copy or maintain.

### 1. Tag this repo first (one-time setup)

```bash
git tag v1
git push origin v1
```

Bump to `v1.1`, `v2`, etc. for future breaking changes.

### 2. Add a two-line caller workflow to each target repo

Create `.github/workflows/ai_pr_review.yml` in the target repo:

```yaml
name: Claude PR scan (Draft->Ready + Push)

on:
  pull_request:
    types: [ready_for_review, synchronize, reopened]

concurrency:
  group: claude-pr-scan-${{ github.repository }}-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  scan:
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_review.yml@v1
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

The `uses:` line is the only thing that points back here. Everything else — prompt loading, checkout, Claude invocation — runs inside the reusable workflow in this repo.

### 3. Add the secret to each target repo

**Settings → Secrets and variables → Actions → New repository secret**

- Name: `ANTHROPIC_API_KEY`
- Value: your Anthropic API key

That's it. Future updates to the prompt or workflow logic only need to be made here; target repos pick them up automatically on the next tagged release.

---

## Customizing the prompt per repo

To override the default Codex prompt for a specific repo, pass `prompt_override`:

```yaml
jobs:
  scan:
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_review.yml@v1
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    with:
      prompt_override: |
        <your custom review instructions here>
```

## Trigger policy

| Event | Runs? |
|---|---|
| PR opened as draft | No (skipped by `if` guard) |
| Draft PR gets new commits | No (skipped by `if` guard) |
| PR marked Ready for review | Yes (`ready_for_review`) |
| New commits pushed to open PR | Yes (`synchronize`) |
| Closed PR reopened | Yes (`reopened`), skipped if still draft |

Concurrency is keyed on `github.repository + PR number` so rapid pushes cancel the in-progress scan and start fresh.

## Versioning

| Tag | Notes |
|---|---|
| `v1` | Initial release |

Breaking changes → new major tag (`v2`). Non-breaking improvements → minor tag (`v1.1`).

## Permissions

The reusable workflow requests only:
- `contents: read`
- `pull-requests: write`
- `issues: write`

## License

MIT
