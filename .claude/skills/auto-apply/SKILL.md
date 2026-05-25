---
name: auto-apply
description: For each application folder whose posting is on a supported ATS (Greenhouse, Lever, Ashby), run a Playwright submission flow, capture confirmation, update submission-log.md, move the posting to postings/applied/, and update applications.md. Unsupported ATSes go on a manual punch list. Trigger phrases - "submit application", "auto-apply", "apply via playwright", "submit drafts".
---

# auto-apply

## When to use

- `applications.md` has one or more entries under `## Active` whose folder
  contains rendered PDFs and a `posting.md` with `ats` in
  `{greenhouse, lever, ashby}`.
- The operator has reviewed the drafts and given the go-ahead.

## When not to use

- Drafts have not been reviewed.
- The posting's `ats` is not in the supported set — emit a manual punch
  list entry instead.

## Inputs

- `applications.md` (`## Active` section).
- Each candidate application folder's `posting.md`, `resume.pdf`,
  `cover-letter.pdf`, and `answers.md`.
- Playwright auth/storage state under `playwright/.auth/` (gitignored).

## Steps

1. Read `applications.md`. Collect entries with prefix `[ACTIVE]`.
2. For each entry, read the application folder's `posting.md` frontmatter.
3. If `posting.ats` is not in the supported set, append the entry to a
   manual punch list (printed at end of run) and continue.
4. If supported, look up the ATS-specific Playwright flow in
   `.claude/scripts/` (file naming TBD; one per ATS). Pass the application
   folder path and posting URL.
5. The flow:
   a. Loads stored auth state for that ATS.
   b. Navigates to the posting.
   c. Fills the application form using the application folder's files.
   d. Uploads `resume.pdf` and `cover-letter.pdf`.
   e. Submits and captures the confirmation (id, screenshot path).
6. On success:
   - Append a `submitted` event to the folder's `submission-log.md` with
     confirmation id and timestamp.
   - Move the posting file from `postings/interested/` to
     `postings/applied/`, updating its frontmatter `status: applied`.
   - Update the entry in `applications.md`: change prefix from `[ACTIVE]`
     to `[SUBMITTED]`, move from `## Active` to `## Submitted`, add `next:
     follow up <date+14d>`.
7. On failure (form change, auth expired, captcha, etc.):
   - Append a failure event to `submission-log.md` with diagnosis.
   - Change the tracker entry prefix to `[BLOCKED]` with a one-line reason.
   - Do not move the posting file.

## Output

- Updated tracker entries in `applications.md`.
- Updated `submission-log.md` in each touched folder.
- File moves for successful submissions.
- A summary printed to chat: submitted / blocked / unsupported counts,
  plus the manual punch list.

## Notes

- This is the riskiest skill. Always run after explicit operator approval
  of the drafts in the application folder.
- Captchas or human-verification challenges abort the flow and mark the
  entry `[BLOCKED]`. Do not attempt to bypass.
