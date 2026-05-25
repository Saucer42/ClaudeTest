# CLAUDE.md — Job Search Monorepo

Read this at session start. Cross-reference sub-area `CLAUDE.md` files rather
than duplicating their contents here.

## Purpose

End-to-end job-search workflow: scrape postings from company boards and
aggregators, triage them, draft tailored materials (resume, cover letter,
screening answers) with Claude, render to PDF via Pandoc, submit via
Playwright for supported ATSes, and track lifecycle in `applications.md`.

## Layout

- `profile/`          — master resume, bullets library, screening answers, targets
- `postings/`         — scraped postings; inbox / interested / applied / archived lifecycle
- `applications/`     — one folder per application (the artifact)
- `templates/`        — Pandoc LaTeX templates and defaults
- `applications.md`   — top-level tracker (source of truth for status)
- `.claude/skills/`   — automation skills (each with a `SKILL.md`)
- `.claude/scripts/`  — Python helpers invoked by skills
- `_legacy/`          — previous job-search hub layout, preserved for reference

Each sub-area carries its own `CLAUDE.md` (local conventions), `index.md`
(canonical listing), `log.md` (chronological record), `backlog.md` (pending
work).

## Shared Conventions

### Tool preference

Prefer built-in tools (`Read`, `Edit`, `Write`, `Bash`) over invoking shell
wrappers from inside agents. Reach for a skill or script when one exists;
otherwise drive the workflow directly.

### Paginated APIs — write as you go

When iterating through a paginated source (job boards, REST APIs), write
results to disk after each page rather than accumulating in memory. A long
ingest that crashes on page 17 must still leave pages 1–16 on disk.

### Secrets policy

- `.env` and `.envrc` are gitignored. Never commit them.
- Playwright auth/storage state (`*.storage.json`, `playwright/.auth/`) is
  gitignored.
- API keys live in `.env` and are read via `os.environ`. Never hardcode.

### Frontmatter spec

All structured Markdown pages start with YAML frontmatter. Minimum keys:

```yaml
---
title: <human readable>
status: <area-specific or "stable">
last_reviewed: YYYY-MM-DD
---
```

Postings and applications have additional required keys — see
`postings/CLAUDE.md` and `applications/CLAUDE.md`.

### Authorship standards

- No speculation. State only what is observed, documented, or confirmed.
- Mark uncertain items inline:
  > **Uncertain:** <what is unknown, why>
- Mark assumptions:
  > **Assumed:** <the assumption and what would invalidate it>
- Mark TODOs:
  > **TODO:** <action item, with owner if known>

### No emojis

In Markdown, code, commit messages — none.

## Applications-Tracker Protocol

`applications.md` at the repo root is the single source of truth for
application lifecycle. Folders under `applications/` are the artifacts;
`applications.md` is the index.

Sections:

- `## Active`     — drafted or in flight, not yet submitted
- `## Submitted`  — submitted, awaiting response or in interview
- `## Done`       — terminal state (offer, rejected, withdrawn)

Each entry begins with a status prefix. Valid prefixes:

`[ACTIVE]` `[BLOCKED]` `[SUBMITTED]` `[INTERVIEW]` `[OFFER]` `[REJECTED]` `[WITHDRAWN]`

Entry format:

```markdown
- [SUBMITTED] 2026-05-24 — Acme Corp / Senior Data Engineer
  - folder: applications/2026-05-24_acme_senior-data-engineer/
  - ats: greenhouse
  - next: follow up 2026-06-07 if no reply
```

### Knowledge-capture gate (on terminal state)

When an entry transitions to `[OFFER]`, `[REJECTED]`, or `[WITHDRAWN]`, the
agent (or operator) driving the move MUST prompt:

> This application is terminal. Do you want to file anything back to the
> knowledge base?
> - `profile/bullets-library.md`   — a bullet that worked, or one that would have
> - `profile/screening-answers.md` — a screening question + answer worth keeping
> - `profile/targets.md`           — an updated must-have or deal-breaker
> - skip

The chosen answer is recorded in the application's `submission-log.md`
before the gate is considered closed. No transition to a terminal state
without this entry.
