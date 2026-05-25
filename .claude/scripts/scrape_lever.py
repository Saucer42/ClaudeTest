"""Scrape job postings from Lever-hosted company boards.

Lever exposes a public JSON API per company:
    https://api.lever.co/v0/postings/<company>?mode=json
This script consumes that API for each configured company, normalises each
posting to the per-posting frontmatter contract defined in
postings/CLAUDE.md, dedupes by URL against the existing postings/
subdirectories, and writes new postings to postings/inbox/.

Inputs
------
- companies : iterable[str]  — Lever company slugs.
- repo_root : Path           — repository root for dedupe.

Outputs
-------
- One .md file per new posting written to postings/inbox/. Filename:
  lever_<company-slug>_<role-slug>.md
- A short summary printed to stdout.

Behaviour
---------
- Write-as-you-go per posting.
- Dedupe by `hostedUrl`.
- Every record carries `ats: lever` and `auto_apply_supported: true`.

TODO
----
- Implement HTTP fetch, JSON parsing, frontmatter serialisation, dedupe.
- Handle Lever's `categories.commitment` for full-time filter.
- Retry on 429/5xx.
"""

from __future__ import annotations


def main() -> None:
    """Entry point. TODO: implement."""
    raise NotImplementedError("scrape_lever: see module docstring")


if __name__ == "__main__":
    main()
