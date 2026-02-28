# Agents

Each agent is a self-contained pair of files:

| File | Purpose |
|---|---|
| `prompts/<name>.md` | The instruction text sent to Claude |
| `.github/workflows/<name>.yml` | The reusable `workflow_call` that loads the prompt and runs the action |

Target repos reference the reusable workflow with a `uses:` line and supply `ANTHROPIC_API_KEY`. The prompt loading, checkout, and Claude invocation all happen inside the reusable workflow here.

---

## Available agents

| Agent | Reusable workflow | Prompt file |
|---|---|---|
| [PR Code Review](pr-review.md) | `claude_pr_review.yml` | `codex_code_review_prompt.md` |
| [Context Files](context-files.md) | `context_files_agent.yml` | `context_files_prompt.md` |

---

## Shared design principles

**Every agent:**

- Accepts a `prompt_override` input so any repo can swap in custom instructions without forking
- Uses the same checkout pattern: target repo first, then this workflow repo for the prompt
- Runs on `ubuntu-latest` with least-privilege permissions (only escalating `contents` to `write` when the agent needs to commit files)
- Can be called independently — agents don't depend on each other

**Prompt files** live in `prompts/` and are loaded at runtime, not embedded in the workflow YAML. This means you can update a prompt and tag a new release without touching any workflow logic.
