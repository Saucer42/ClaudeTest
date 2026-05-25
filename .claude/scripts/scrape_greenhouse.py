"""Scrape job postings from Greenhouse-hosted company boards.

Greenhouse exposes a public JSON API per company:
    https://boards-api.greenhouse.io/v1/boards/<slug>/jobs
This script consumes that API for each configured company slug, normalises
each posting to the per-posting frontmatter contract defined in
postings/CLAUDE.md, dedupes by URL against the existing postings/
subdirectories, and writes new postings to postings/inbox/.

Inputs
------
- company_slugs : iterable[str]  — Greenhouse board slugs (CLI args or
  config file; TBD).
- repo_root     : Path           — repository root, used to resolve
  postings/{inbox,interested,applied,archived} for dedupe.

Outputs
-------
- One .md file per new posting written to postings/inbox/. Filename:
  greenhouse_<company-slug>_<role-slug>.md
- A short summary printed to stdout: fetched / new / skipped.

Behaviour
---------
- Paginated API write-as-you-go: each posting that survives dedupe is
  written to disk immediately. A crash mid-run leaves a partial but
  consistent inbox.
- Dedupe key: canonical posting URL.
- ATS classification: every record produced here carries
  `ats: greenhouse` and `auto_apply_supported: true`.

TODO
----
- Decide where company_slugs lives (CLI? .claude/scripts/sources.yaml?).
- Implement HTTP fetch with httpx, JSON parsing, slugification, frontmatter
  serialisation, dedupe walk.
- Add retry with backoff on 429/5xx.
"""

from __future__ import annotations


def main() -> None:
    """Entry point. TODO: implement."""
    raise NotImplementedError("scrape_greenhouse: see module docstring")


if __name__ == "__main__":
    main()
