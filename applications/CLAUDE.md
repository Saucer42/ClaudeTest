# applications/ — CLAUDE.md

One folder per application. See root `CLAUDE.md` for shared conventions and
the applications-tracker protocol (including the knowledge-capture gate on
terminal states).

## Folder convention

```
applications/YYYY-MM-DD_<company-slug>_<role-slug>/
```

`YYYY-MM-DD` is the date the folder is created, not the submission date.
Slugs are lowercase, hyphenated, ASCII.

## Files inside each folder

| File | Required | Purpose |
|---|---|---|
| `posting.md`        | yes | Copy of the posting (with frontmatter) at the moment of application |
| `resume.md`         | yes | Tailored resume source (Markdown) |
| `resume.pdf`        | yes | Pandoc-rendered resume, committed (audit trail) |
| `cover-letter.md`   | yes | Tailored cover letter source |
| `cover-letter.pdf`  | yes | Pandoc-rendered cover letter, committed |
| `answers.md`        | conditional | Screening-question drafts if the posting requires them |
| `submission-log.md` | yes | Chronological record of this application's lifecycle |

## submission-log.md format

Each event is a dated entry. Required events:

- `drafted`     — initial materials generated
- `reviewed`    — human review pass done
- `submitted`   — submission completed (record ATS confirmation id or screenshot path)
- `reply`       — any response from the employer
- `knowledge-capture` — the answer to the gate prompt on terminal transition

Example:

```markdown
## 2026-05-24

- drafted: tailor-application skill, model claude-sonnet-4-6
- reviewed: human pass, 3 bullet edits applied

## 2026-05-25

- submitted: greenhouse, confirmation id GH-12345
- next-check: 2026-06-08

## 2026-06-15

- reply: rejected via standard auto-mail
- knowledge-capture: filed bullet "Reduced cross-team incident response from 4h to 45m" to bullets-library.md as skill:incident-response, role:manager
```

## Status authority

The folder is the artifact. `applications.md` at the repo root is the index.
Do not duplicate status into the folder; update the tracker entry and rely
on `submission-log.md` for chronology.
