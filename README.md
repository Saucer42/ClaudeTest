# Job Search Monorepo

End-to-end job-search workflow. Scrape postings, triage them, draft tailored
materials, submit via Playwright for supported ATSes, track lifecycle in one
place.

## Quick map

```
profile/         master resume, bullets library, targets, screening answers
postings/        scraped postings: inbox/ -> interested/ -> applied/ | archived/
applications/    one folder per application (posting, resume, cover letter, log)
templates/       Pandoc LaTeX templates
applications.md  the tracker (source of truth for status)
.claude/skills/  automation skills (scrape, triage, tailor, render, apply, review)
.claude/scripts/ Python helpers invoked by skills
_legacy/         previous layout, preserved for reference
```

Open `CLAUDE.md` for the conventions every sub-area inherits, including the
applications-tracker protocol and the knowledge-capture gate.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
# Playwright browsers — run explicitly when you are ready:
# playwright install
```

Required environment in `.env` (gitignored):

```
ANTHROPIC_API_KEY=...
```

## Loop

1. `scrape-postings`        — refresh `postings/inbox/`
2. `triage-postings`        — walk inbox, accept i/a/s
3. `tailor-application`     — draft resume/cover/answers per interested posting
4. `auto-apply`             — submit for supported ATSes; punch list for the rest
5. `applications-review`    — weekly sweep: ghosts, follow-ups, interview prep

Each step is a skill in `.claude/skills/`. The `SKILL.md` inside each folder
documents when to invoke, inputs, steps, and outputs.
