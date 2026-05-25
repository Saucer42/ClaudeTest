---
name: render-pdf
description: Render a Markdown source to PDF via Pandoc using a named template. Deterministic, no LLM involvement. Trigger phrases - "render pdf", "build pdf", "regenerate the resume PDF", "rerender cover letter".
---

# render-pdf

## When to use

- Markdown source has changed and the matching PDF is stale.
- A new application folder has just been populated by `tailor-application`.
- The operator hand-edited a tailored resume or cover letter and needs the
  PDF refreshed.

## When not to use

- The Markdown does not exist yet — that is `tailor-application`.
- The template itself is broken — fix the template in `templates/` first.

## Inputs

- A path to a Markdown source (typically inside `applications/<folder>/`).
- A template name (`resume` or `cover-letter`).

## Steps

1. Resolve the source path and verify it exists.
2. Resolve the template — `templates/<name>.tex` and
   `templates/pandoc-defaults.yaml`.
3. Invoke `.claude/scripts/render_pdf.py <source.md> <template-name>`.
4. The script writes `<source>.pdf` next to the source.

## Output

- A PDF written next to the source Markdown.
- No log entry — the source file's git history is the audit trail. The
  application's `submission-log.md` records render events only when they
  are part of a submission flow.

## Notes

- Strictly deterministic. No Claude calls in this skill.
- If `pandoc` or `xelatex` is missing on the host, the script raises a
  clear error rather than falling back to another engine.
