"""Scrape postings from Indeed search results.

Indeed does not expose a public job API for unauthenticated callers and
aggressively rate-limits scrapers. This script uses Playwright with a
real-browser fingerprint to walk operator-supplied search-result URLs,
extract postings, and normalise each to the per-posting frontmatter
contract in postings/CLAUDE.md.

Inputs
------
- search_urls : iterable[str]  — Indeed search-result URLs (already
  filtered to role / location / remote).
- repo_root   : Path           — repository root for dedupe.
- storage_state : Path | None  — optional Playwright storage state for an
  Indeed session (helps with rate limits; gitignored).

Outputs
-------
- One .md file per new posting written to postings/inbox/. Filename:
  indeed_<company-slug>_<role-slug>.md
- A short summary printed to stdout.

Behaviour
---------
- Write-as-you-go per posting.
- Paginate by clicking the next-page link until exhausted or capped.
- Dedupe by `jk` query parameter in the posting URL (Indeed's canonical id).
- ATS classification: default `ats: unknown`, `auto_apply_supported: false`.
  Indeed-hosted apply (the 'Easily Apply' button) is its own ATS variant;
  if encountered set `ats: indeed-easy-apply` (not yet in the supported
  auto-apply list).

TODO
----
- Implement Playwright fetch with sensible user agent, headed-mode fallback.
- Handle Indeed's anti-bot interstitials: detect and abort, do not bypass.
- Add a strict request-rate cap (one page every N seconds).
"""

from __future__ import annotations


def main() -> None:
    """Entry point. TODO: implement."""
    raise NotImplementedError("scrape_indeed: see module docstring")


if __name__ == "__main__":
    main()
