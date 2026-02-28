# PR Code Review Agent

Reviews PR diffs using the official [Codex Code Review prompt](https://developers.openai.com/cookbook/examples/codex/build_code_review_with_codex_sdk/) and posts findings directly to the PR.

## Files

| File | Path |
|---|---|
| Skill | `skills/codex-code-review/SKILL.md` |
| Workflow (shared) | `.github/workflows/claude_pr_agent.yml` |

## Skill frontmatter

```yaml
---
name: codex-code-review
description: Reviews PR diffs using the official Codex Code Review prompt. Posts actionable findings by category and a correctness verdict with confidence score.
argument-hint: ""
allowed-tools: Read, Grep, Glob, Bash
---
```

The body after the frontmatter is the verbatim Codex prompt text. The frontmatter is stripped at load time — Claude only sees the body.

## What it does

Claude reads the PR diff and flags issues in these categories:

- **Correctness** — logic errors, wrong assumptions, broken edge cases
- **Performance** — algorithmic problems, unnecessary work
- **Security** — OWASP top-10 class issues, injection risks, credential exposure
- **Maintainability** — API misuse, dead code, structural problems
- **Developer experience** — confusing interfaces, missing context

It produces an overall verdict — `patch is correct` or `patch is incorrect` — with a confidence score between 0 and 1.

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
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_agent.yml@v1
    with:
      skill: "codex-code-review"
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Customization options

### Use a local skill from the target repo

Target repos can ship their own `SKILL.md` and pass its path instead of a central skill name:

```yaml
with:
  skill: ".claude/skills/security-review"   # loads .claude/skills/security-review/SKILL.md
```

This follows the standard Claude Code skill directory convention — the `SKILL.md` file is in a named subdirectory.

### Use a raw prompt (no skill file)

For a one-off instruction without creating a skill file:

```yaml
with:
  prompt: |
    Review this diff for REST API convention violations:
    - snake_case paths only
    - responses must have a top-level "data" key
    Flag each violation with file and line. Give a pass/fail verdict.
```

### Run multiple skills sequentially

Use `needs:` to chain skills across jobs. Each job calls the same generic workflow with a different skill:

```yaml
jobs:
  review:
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_agent.yml@v1
    with:
      skill: "codex-code-review"
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  conventions:
    needs: review
    if: ${{ github.event.pull_request.draft == false }}
    uses: safurrier/python-collab-template/.github/workflows/claude_pr_agent.yml@v1
    with:
      skill: ".claude/skills/team-conventions"
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Permissions

```yaml
permissions:
  contents: write
  pull-requests: write
  issues: write
```

`contents: write` is present on the shared workflow for compatibility with write-enabled skills. The review skill itself doesn't write files.

## Skill body (verbatim)

> You are acting as a reviewer for a proposed code change made by another engineer. Focus on issues that impact correctness, performance, security, maintainability, or developer experience. Flag only actionable issues introduced by the pull request. When you flag an issue, provide a short, direct explanation and cite the affected file and line range. Prioritize severe issues and avoid nit-level comments unless they block understanding of the diff. After listing findings, produce an overall correctness verdict ("patch is correct" or "patch is incorrect") with a concise justification and a confidence score between 0 and 1. Ensure that file citations and line numbers are exactly correct using the tools available; if they are incorrect your comments will be rejected.
