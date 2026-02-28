# Claude PR Agents

A collection of reusable GitHub Actions workflows that attach Claude-powered automation to pull requests. Pick an agent, drop a 15-line caller workflow into your repo, add an API key, and every PR gets automated review, context file generation, or any other prompt-driven task.

## Available agents

| Agent | Trigger | What it does |
|---|---|---|
| [PR Code Review](agents/pr-review.md) | Draft→Ready, new commits pushed | Reviews the diff; posts findings and a correctness verdict |
| [Context Files](agents/context-files.md) | PR opened, Draft→Ready | Creates or updates `AGENTS.md` / `CLAUDE.md` so future agents are oriented |

## How it works

This repo is the **central workflow host**. Each agent lives in two files:

- A **prompt** (`prompts/<name>.md`) — the instruction text sent to Claude
- A **reusable workflow** (`.github/workflows/<name>.yml`) — the Actions plumbing

Target repos only need a thin caller workflow:

```
Your repo                                This repo (central host)
─────────────────────────────────────    ────────────────────────────────────────
.github/workflows/ai_pr_review.yml  →   .github/workflows/claude_pr_review.yml
  uses: safurrier/...@v1                  ├── checks out your repo
  secrets: ANTHROPIC_API_KEY              ├── loads prompts/codex_code_review_prompt.md
                                          └── runs anthropics/claude-code-action@v1
```

When a PR event fires, GitHub fetches the reusable workflow from this repo, runs it in your repo's context, and Claude posts its output back to the PR thread.

## Quick start

→ [Using in Your Repo](using.md) — step-by-step setup guide

## Add a new agent

Anyone can contribute a new agent by adding a prompt file, a reusable workflow, and a doc page.

→ [Contributing](contributing.md)
