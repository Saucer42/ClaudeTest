"""Scrape job postings from Ashby-hosted company boards.

Ashby exposes a public JSON API per organisation:
    https://api.ashbyhq.com/posting-api/job-board/<org>
This script consumes that API for each configured org, normalises each
posting to the per-posting frontmatter contract defined in
postings/CLAUDE.md, dedupes by URL against the existing postings/
subdirectories, and writes new postings to postings/inbox/.

Inputs
------
- orgs      : iterable[str]  — Ashby organisation slugs.
- repo_root : Path           — repository root for dedupe.

Outputs
-------
- One .md file per new posting written to postings/inbox/. Filename:
  ashby_<org-slug>_<role-slug>.md
- A short summary printed to stdout.

Behaviour
---------
- Write-as-you-go per posting.
- Dedupe by canonical job URL.
- Every record carries `ats: ashby` and `auto_apply_supported: true`.

TODO
----
- Implement HTTP fetch, JSON parsing, frontmatter serialisation, dedupe.
- Honour Ashby's `isListed` flag (skip unlisted).
- Retry on 429/5xx.
"""

from __future__ import annotations


def main() -> None:
    """Entry point. TODO: implement."""
    raise NotImplementedError("scrape_ashby: see module docstring")


if __name__ == "__main__":
    main()
