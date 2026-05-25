# profile/ — CLAUDE.md

Master profile material that feeds tailoring. See root `CLAUDE.md` for
shared conventions (frontmatter, secrets, authorship, no emojis).

## Contents

- `master-resume.md`        — canonical long-form resume. Tailoring selects subsets.
- `versions/`               — historical and source variants. Never edited in place; new variants land with a date prefix.
- `bullets-library.md`      — tagged inventory of bullets drawn from past resumes and accomplishments. Source for tailoring selection.
- `cover-letter-templates/` — reusable cover-letter fragments by role family or industry.
- `screening-answers.md`    — answers to common screening questions, tagged.
- `targets.md`              — roles, locations, comp floor, must-haves, deal-breakers.

## Bullets-library tagging

Each bullet carries three tag axes. Multiple tags per axis are allowed.

- `skill:`   — concrete technical or leadership skill (e.g. `skill:t-sql`, `skill:team-management`)
- `role:`    — role family the bullet fits (e.g. `role:data-engineer`, `role:manager`)
- `keyword:` — ATS keyword to match (e.g. `keyword:etl`, `keyword:kimball`)

## Ingest flow

1. Drop a new resume variant into `versions/` as `YYYY-MM-DD_<slug>.md`.
2. Reconcile net-new content into `master-resume.md`.
3. Extract any net-new bullets into `bullets-library.md` with tags.
4. Record the ingest in `log.md` with date, source variant, and what changed.
