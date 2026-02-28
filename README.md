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
  claude_pr_review.yml   # Reusable workflow (workflow_call)
  ai_pr_review.yml       # Caller workflow for this repo (example)
prompts/
  codex_code_review_prompt.md   # Official Codex prompt text (verbatim)
```

## Using this in another repo

### 1. Add the caller workflow

Create `.github/workflows/ai_pr_review.yml` in your target repo:

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

### 2. Add the secret

In your target repo: **Settings → Secrets and variables → Actions → New repository secret**

- Name: `ANTHROPIC_API_KEY`
- Value: your Anthropic API key

### 3. Pin to a release tag

Reference `@v1` (or a specific tag) to pin to a stable version. Check the [releases](../../releases) page for available tags.

## Customizing the prompt

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

- `v1` — initial release
- Tag releases with `git tag v1 && git push origin v1`

## Permissions

The reusable workflow requests only:
- `contents: read`
- `pull-requests: write`
- `issues: write`

## License

MIT
