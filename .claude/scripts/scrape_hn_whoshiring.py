"""Scrape postings from the HN 'Who is hiring?' monthly thread.

Hacker News publishes a 'Who is hiring?' thread on the first of each month.
This script resolves the current month's thread id (via HN search API or
algolia), walks top-level comments, and extracts postings that match
operator-provided keyword filters (e.g. 'remote', 'data', 'staff').

Each surviving comment is normalised to the per-posting frontmatter
contract in postings/CLAUDE.md. HN does not expose structured fields, so
several frontmatter values will be inferred from comment text and many
will land as null.

Inputs
------
- keywords  : iterable[str]  — case-insensitive substrings; AND across the
  list within a comment.
- repo_root : Path           — repository root for dedupe.
- month     : str | None     — 'YYYY-MM' override; default = current month.

Outputs
-------
- One .md file per surviving comment, written to postings/inbox/.
  Filename: hn-whoshiring_<company-slug>_<role-slug>.md (company/role
  parsed best-effort from the comment's first line).
- A short summary printed to stdout.

Behaviour
---------
- Write-as-you-go per comment.
- Dedupe by HN comment permalink URL.
- Every record carries `ats: unknown` and `auto_apply_supported: false`
  unless the comment links to a recognised ATS URL, in which case promote
  to the matching ats value.

TODO
----
- Resolve current 'Who is hiring?' thread id via Algolia HN API.
- Parse the loose 'Company | role | location | remote | comp' convention
  most comments follow; fall back to nulls when missing.
- Heuristic for ATS classification from linked URLs (greenhouse.io,
  jobs.lever.co, jobs.ashbyhq.com).
"""

from __future__ import annotations


def main() -> None:
    """Entry point. TODO: implement."""
    raise NotImplementedError("scrape_hn_whoshiring: see module docstring")


if __name__ == "__main__":
    main()
