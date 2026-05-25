# postings/ — CLAUDE.md

Scraped job postings. See root `CLAUDE.md` for shared conventions.

## Lifecycle

```
inbox/      newly scraped, untriaged
interested/ accepted in triage; queued for tailoring
applied/    application has been submitted (folder exists in applications/)
archived/   rejected in triage, or applied long enough ago to retire
```

`inbox/` -> `interested/` -> `applied/`
`inbox/` -> `archived/`

One file per posting. Filename:

```
<source>_<company-slug>_<role-slug>.md
```

## Per-posting frontmatter contract

Every posting file starts with this frontmatter. All keys are required; use
`null` when a value is genuinely unknown rather than guessing.

```yaml
---
source: greenhouse | lever | ashby | hn-whoshiring | wellfound | indeed | linkedin
url: <canonical posting url>
company: <display name>
role: <display title>
location: <city, region, country | "remote">
remote: true | false | hybrid
comp_min: <integer or null>
comp_max: <integer or null>
posted_date: YYYY-MM-DD | null
scraped_date: YYYY-MM-DD
status: inbox | interested | applied | archived
ats: greenhouse | lever | ashby | workday | icims | unknown
auto_apply_supported: true | false
---
```

The body of the file is the cleaned JD text (no nav, no footer, no
boilerplate "About Us" filler that does not differ between roles at the
same company).

## Dedupe rule

Scrapers dedupe by `url` across all four subdirectories. If a posting at a
given URL already exists in any of `inbox/`, `interested/`, `applied/`,
`archived/`, the scraper skips. It does not overwrite.

## Status transitions

`status` in the frontmatter MUST match the subdirectory the file lives in.
A transition is: edit frontmatter, then move the file. Do not leave a file
in `inbox/` with `status: interested`.
