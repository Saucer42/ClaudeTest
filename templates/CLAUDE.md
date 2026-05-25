# templates/ — CLAUDE.md

Pandoc LaTeX templates used by the `render-pdf` skill. See root `CLAUDE.md`
for shared conventions.

## Contents

- `resume.tex`           — resume template
- `cover-letter.tex`     — cover letter template
- `pandoc-defaults.yaml` — shared Pandoc options (engine, geometry, fonts)

## Composition

```
pandoc resume.md \
  --defaults templates/pandoc-defaults.yaml \
  --template templates/resume.tex \
  -o resume.pdf
```

`render_pdf.py` in `.claude/scripts/` wraps this. Skills should call the
script, not invoke `pandoc` directly.

## Editing rules

- Tailor *content* by editing the markdown source in the application folder.
- Edit templates only when changing *visual structure* (layout, fonts,
  spacing, section headings).
- Template changes apply to every future render. Before committing a
  template change, re-render at least one existing application and confirm
  no regressions.
