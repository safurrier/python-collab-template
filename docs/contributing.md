# Contributing a New Agent

Adding an agent takes three files and a tag bump. No framework, no registration step.

## The pattern

Every agent is:

1. A **prompt file** in `prompts/` — the instruction text Claude receives
2. A **reusable workflow** in `.github/workflows/` — the Actions plumbing
3. A **doc page** in `docs/agents/` — how to use it and what it does

That's it. The reusable workflow is almost identical for every agent; you're mostly just changing the prompt file name and adjusting permissions if the agent needs to write files.

---

## Step 1 — Write the prompt

Create `prompts/<your-agent-name>.md`.

Write the prompt as you'd write a Claude system prompt or slash-command definition. A few guidelines:

- Be specific about the **output format** (what Claude should post, commit, or return)
- Describe the **scope** (what Claude should read — diff only, full repo, specific files)
- If the prompt is parameterizable (like context files' mode/scope), use a `$ARGUMENTS` placeholder and document the substitution in the workflow
- Keep it focused — one agent, one job

---

## Step 2 — Create the reusable workflow

Create `.github/workflows/<your-agent-name>.yml`.

Use the existing agents as templates. The structure is always:

```yaml
name: <Human-readable agent name>

on:
  workflow_call:
    inputs:
      prompt_override:
        type: string
        required: false
        default: ""
      # Add any agent-specific inputs here (e.g., agent_args)
    secrets:
      ANTHROPIC_API_KEY:
        required: true

jobs:
  <job-name>:
    runs-on: ubuntu-latest
    permissions:
      contents: read          # bump to write if the agent commits files
      pull-requests: write
      issues: write

    steps:
      - name: Checkout target repo
        uses: actions/checkout@v4

      - name: Checkout workflow repo (for prompt)
        uses: actions/checkout@v4
        with:
          repository: safurrier/python-collab-template
          path: _ai_workflows

      - name: Load prompt
        id: prompt
        shell: bash
        run: |
          if [ -n "${{ inputs.prompt_override }}" ]; then
            echo "text<<EOF" >> "$GITHUB_OUTPUT"
            printf "%s\n" "${{ inputs.prompt_override }}" >> "$GITHUB_OUTPUT"
            echo "EOF" >> "$GITHUB_OUTPUT"
          else
            echo "text<<EOF" >> "$GITHUB_OUTPUT"
            cat _ai_workflows/prompts/<your-agent-name>.md >> "$GITHUB_OUTPUT"
            echo "EOF" >> "$GITHUB_OUTPUT"
          fi

      - name: Run <your agent name>
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: ${{ steps.prompt.outputs.text }}
```

**Key decisions:**

- `contents: read` vs `contents: write` — use `write` only if the agent commits files back to the branch
- Add extra inputs (like `agent_args`) if the prompt is parameterizable
- Use `sed "s|\$ARGUMENTS|${ARGS}|g"` in the Load prompt step when substituting arguments into the prompt

---

## Step 3 — Write the doc page

Create `docs/agents/<your-agent-name>.md`. Include:

- What it does (1–2 sentences)
- The files table (reusable workflow + prompt path)
- Trigger event table
- Minimal caller workflow (copy-paste ready)
- Customization options (`prompt_override`, any extra inputs)
- Permissions block

Then add it to the nav in `mkdocs.yml`:

```yaml
nav:
  - Agents:
    - Overview: agents/index.md
    - PR Code Review: agents/pr-review.md
    - Context Files: agents/context-files.md
    - Your Agent: agents/your-agent-name.md  # add this line
```

And add a row to the table in `docs/agents/index.md`.

---

## Step 4 — Tag a new release

```bash
git add prompts/<your-agent-name>.md \
        .github/workflows/<your-agent-name>.yml \
        docs/agents/<your-agent-name>.md \
        docs/agents/index.md \
        mkdocs.yml
git commit -m "feat: add <your agent name> agent"
git tag v1.1   # or next semver
git push origin main --tags
```

Target repos that want the new agent update their caller workflow to reference `@v1.1`.

---

## Checklist

- [ ] `prompts/<name>.md` — prompt written and reviewed
- [ ] `.github/workflows/<name>.yml` — reusable workflow using `workflow_call`
- [ ] `prompt_override` input present with `default: ""`
- [ ] Permissions set to minimum required (`contents: write` only if needed)
- [ ] `docs/agents/<name>.md` — doc page with trigger table and caller snippet
- [ ] Row added to `docs/agents/index.md`
- [ ] Entry added to `mkdocs.yml` nav
- [ ] New semver tag pushed
