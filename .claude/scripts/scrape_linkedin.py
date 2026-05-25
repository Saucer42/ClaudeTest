"""Scrape postings from LinkedIn Jobs search.

LinkedIn does not expose a public job API and explicitly prohibits
scraping in its ToS. This script uses Playwright with the operator's
authenticated session to walk LinkedIn Jobs search-result URLs, extract
postings, and normalise each to the per-posting frontmatter contract in
postings/CLAUDE.md.

> **Uncertain:** LinkedIn ToS compliance. The operator is responsible for
> assessing whether their use case falls within acceptable use. This
> script exists because the operator explicitly requested it.

Inputs
------
- search_urls   : iterable[str]  — LinkedIn Jobs search URLs.
- repo_root     : Path           — repository root for dedupe.
- storage_state : Path           — Playwright storage state for the
  operator's LinkedIn session (required; gitignored).

Outputs
-------
- One .md file per new posting written to postings/inbox/. Filename:
  linkedin_<company-slug>_<role-slug>.md
- A short summary printed to stdout.

Behaviour
---------
- Write-as-you-go per posting.
- Paginate by scrolling the results pane until exhausted or capped.
- Dedupe by posting id from the canonical URL.
- ATS classification: best-effort from any external apply link. If the
  posting uses LinkedIn's 'Easy Apply', set `ats: linkedin-easy-apply`
  (not yet in the supported auto-apply list); otherwise classify the
  external destination.

TODO
----
- Implement Playwright session load, results pane scroll, posting
  extraction.
- Detect session expiry and emit a clear re-auth instruction.
- Strict request-rate cap.
"""

from __future__ import annotations


def main() -> None:
    """Entry point. TODO: implement."""
    raise NotImplementedError("scrape_linkedin: see module docstring")


if __name__ == "__main__":
    main()
