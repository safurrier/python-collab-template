# PR Code Review Agent

Reviews PR diffs using the official [Codex Code Review prompt](https://developers.openai.com/cookbook/examples/codex/build_code_review_with_codex_sdk/) and posts findings directly to the PR.

## Files

| File | Path |
|---|---|
| Reusable workflow | `.github/workflows/claude_pr_review.yml` |
| Prompt | `prompts/codex_code_review_prompt.md` |

## What it does

Claude reads the PR diff and flags issues in these categories:

- **Correctness** — logic errors, wrong assumptions, broken edge cases
- **Performance** — algorithmic problems, unnecessary work
- **Security** — OWASP top-10 class issues, injection risks, credential exposure
- **Maintainability** — API misuse, dead code, structural problems
- **Developer experience** — confusing interfaces, missing context

It then produces an overall verdict — `patch is correct` or `patch is incorrect` — with a confidence score between 0 and 1.

## Triggers

| Event | Runs? |
|---|---|
| Draft PR opened or pushed | No |
| PR marked Ready for review | Yes |
| New commits pushed to open PR | Yes |
| PR reopened (non-draft) | Yes |

## Minimal caller workflow

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

## Customizing the prompt

The `prompt_override` input replaces the entire default prompt. This makes the workflow a generic "run Claude on a PR with any prompt" mechanism — the code review prompt just happens to be the default.

```yaml
jobs:
  review:
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_review.yml@v1
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    with:
      prompt_override: |
        Review this diff for any violation of our REST API conventions:
        - All endpoints must use snake_case paths
        - Response envelopes must include a top-level "data" key
        - Error responses must include "code" and "message" fields
        Flag each violation with file and line number. Give a pass/fail verdict.
```

Because the workflow is generic, you can use `prompt_override` to turn this into any kind of PR agent — a changelog enforcer, a migration validator, a documentation checker — without adding a new workflow.

## Permissions

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

`pull-requests: write` and `issues: write` are needed for Claude to post comments to the PR.

## Default prompt

The prompt is the verbatim text from the OpenAI Codex cookbook. Source: [prompts/codex_code_review_prompt.md](https://github.com/safurrier/python-collab-template/blob/main/prompts/codex_code_review_prompt.md)

> You are acting as a reviewer for a proposed code change made by another engineer. Focus on issues that impact correctness, performance, security, maintainability, or developer experience. Flag only actionable issues introduced by the pull request. When you flag an issue, provide a short, direct explanation and cite the affected file and line range. Prioritize severe issues and avoid nit-level comments unless they block understanding of the diff. After listing findings, produce an overall correctness verdict ("patch is correct" or "patch is incorrect") with a concise justification and a confidence score between 0 and 1. Ensure that file citations and line numbers are exactly correct using the tools available; if they are incorrect your comments will be rejected.
