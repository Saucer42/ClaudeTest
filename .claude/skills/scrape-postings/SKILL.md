---
name: scrape-postings
description: Run all configured source scrapers (Greenhouse, Lever, Ashby, HN Who's Hiring, Wellfound, Indeed, LinkedIn), dedupe against existing postings, and write new posting .md files to postings/inbox/. Trigger phrases - "scrape jobs", "refresh inbox", "pull new postings", "run scrapers", "fetch jobs from <source>".
---

# scrape-postings

## When to use

- The operator wants to refresh `postings/inbox/` with new jobs.
- A new company slug has been added to a scraper's input list and they want
  it ingested.
- A scheduled weekly refresh.

## When not to use

- The operator wants to read or triage existing postings — that is
  `triage-postings`.
- The operator wants to apply to a posting — that is `tailor-application`.

## Inputs

- Per-scraper configuration (company slug lists, search queries) — location
  TBD; for now, scripts accept CLI args.
- `postings/{inbox,interested,applied,archived}/` for dedupe.

## Steps

1. For each configured source, invoke the matching script in
   `.claude/scripts/scrape_<source>.py`.
2. For every posting returned, build a posting .md file matching the
   frontmatter contract in `postings/CLAUDE.md`.
3. Dedupe by `url` against all four subdirectories. Skip duplicates.
4. Write new postings to `postings/inbox/` as
   `<source>_<company-slug>_<role-slug>.md`. Write-as-you-go: do not batch.
5. Append a run entry to `postings/log.md`: source, count fetched, count new
   after dedupe, errors.
6. Update `postings/index.md` counts.

## Output

- New `.md` files in `postings/inbox/`.
- Log entry in `postings/log.md`.
- Updated counts in `postings/index.md`.
- A short summary printed to the chat: per-source count fetched / new /
  skipped.

## Failure handling

- If a single source errors, log the error in `postings/log.md` and
  continue with the remaining sources. Do not abort the whole run.
- Partial writes are acceptable; the dedupe rule will protect a re-run.
