# User Stories

## Solo developer maintaining multiple repos

**As a developer who maintains several personal or side-project repositories,**
I want a code review pass to run automatically whenever I mark a PR ready,
so that I catch correctness issues and security problems before merging without having to remember to trigger it manually.

**As a solo developer working quickly,**
I want the review to re-run when I push a follow-up commit to address feedback,
so that I get a fresh verdict on the updated code without creating a new PR.

**As a solo developer who forgets to write agent context files,**
I want a workflow that notices when `AGENTS.md` / `CLAUDE.md` are missing and generates them automatically when I open a PR,
so that future AI-assisted sessions in that repo are pre-oriented without extra effort.

---

## Team lead or engineering manager

**As a team lead responsible for code quality across multiple repos,**
I want a consistent, documented review standard applied to every PR across all our repos,
so that automated reviews use the same criteria regardless of who's reviewing.

**As a team lead,**
I want to be able to override the review prompt per-repo when one codebase has unique concerns (e.g., a security-sensitive service or a performance-critical library),
so that the review is targeted without having to fork the workflow logic.

**As a team lead,**
I want to pin to a specific release tag of the central workflow repo,
so that I control when my team picks up changes and can test upgrades in a staging repo first.

---

## Platform / DevEx engineer

**As a DevEx engineer building internal tooling,**
I want a single central repo of reusable workflows that any team can reference with one `uses:` line,
so that maintaining or updating the review logic is a one-place change rather than a PR to every repo.

**As a platform engineer,**
I want to contribute a new agent (e.g., a dependency audit agent, a documentation coverage agent) by following a clear pattern,
so that onboarding new automated tasks is predictable and doesn't require understanding a complex framework.

**As a platform engineer,**
I want each agent to be independently callable,
so that repos can mix and match agents without coupling.

---

## What these stories drive

| Story theme | Feature |
|---|---|
| Automatic, no-remember trigger | `ready_for_review` + `synchronize` events; draft guard |
| No double-run on rapid pushes | Concurrency with `cancel-in-progress: true` |
| Per-repo prompt customization | `prompt_override` input on every reusable workflow |
| Version pinning | Semver tags (`@v1`, `@v1.1`) on this repo |
| Extend without duplication | New agent = prompt file + reusable workflow + doc page |
| Context files on autopilot | `context_files_agent.yml` on `opened` + `ready_for_review` |
