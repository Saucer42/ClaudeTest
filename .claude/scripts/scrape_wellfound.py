"""Scrape postings from Wellfound (formerly AngelList Talent).

Wellfound does not expose a public job API. This script uses Playwright to
load the operator's saved-search results page and extract postings from
the rendered HTML, then normalises each to the per-posting frontmatter
contract in postings/CLAUDE.md.

Inputs
------
- search_url : str   — a Wellfound saved-search results URL.
- repo_root  : Path  — repository root for dedupe.
- storage_state : Path  — Playwright storage state for the operator's
  Wellfound session (gitignored).

Outputs
-------
- One .md file per new posting written to postings/inbox/. Filename:
  wellfound_<company-slug>_<role-slug>.md
- A short summary printed to stdout.

Behaviour
---------
- Write-as-you-go per posting.
- Paginate by clicking 'Load more' until exhausted or until a configurable
  page cap is hit.
- Dedupe by canonical posting URL.
- ATS classification: best-effort from any 'Apply' link on the posting;
  default `ats: unknown`, `auto_apply_supported: false`.

TODO
----
- Implement Playwright session load, page scroll, posting card extraction.
- Be resilient to Wellfound's DOM changes; isolate selectors at the top.
- Detect bot-challenge interstitials and abort cleanly.
"""

from __future__ import annotations


def main() -> None:
    """Entry point. TODO: implement."""
    raise NotImplementedError("scrape_wellfound: see module docstring")


if __name__ == "__main__":
    main()
