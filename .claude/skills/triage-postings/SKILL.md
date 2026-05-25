---
name: triage-postings
description: Walk postings/inbox/ interactively, present a 5-line summary per posting, accept i (interested) / a (archive) / s (skip), and move the file to the matching subdirectory while updating its frontmatter status. Trigger phrases - "triage", "review inbox", "go through new postings", "triage postings".
---

# triage-postings

## When to use

- `postings/inbox/` has unreviewed postings and the operator wants to sort
  them.

## When not to use

- The inbox is empty — run `scrape-postings` first.
- The operator wants to apply — that is `tailor-application`.

## Inputs

- All `.md` files in `postings/inbox/`.
- `profile/targets.md` to bias the summary toward relevant signals.

## Steps

1. List files in `postings/inbox/`. For each, in chronological order
   (newest first):
   a. Read frontmatter + body.
   b. Render a 5-line summary:
      - line 1: `<company> — <role>` (`<source>`, `<ats>`)
      - line 2: `<location>` (`<remote>`) | comp `<comp_min>–<comp_max>`
      - line 3: first sentence of the JD
      - line 4: top match against `profile/targets.md` (one signal)
      - line 5: top mismatch / risk (one signal)
   c. Prompt the operator: `[i]nterested / [a]rchive / [s]kip`.
2. Apply the choice:
   - `i`: set frontmatter `status: interested`, move file to
     `postings/interested/`.
   - `a`: set frontmatter `status: archived`, move file to
     `postings/archived/`.
   - `s`: leave in `inbox/` for the next run.
3. After the walk, append a run entry to `postings/log.md`: counts
   interested / archived / skipped.
4. Update `postings/index.md` counts.

## Output

- File moves between `postings/` subdirectories.
- Updated frontmatter on moved files.
- Log entry in `postings/log.md`.

## Notes

- This is an interactive skill. Do not auto-classify without prompting; the
  point is operator judgement.
- If the operator says "show me the full JD", read the file body before
  re-prompting.
