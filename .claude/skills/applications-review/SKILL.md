---
name: applications-review
description: Weekly sweep of applications.md. Compute age per active and submitted entry, flag ghosted applications (>2 weeks since last contact) for follow-up, surface interviews that need prep. Trigger phrases - "weekly review", "review applications", "follow up on applications", "ghost check", "applications review".
---

# applications-review

## When to use

- Weekly cadence, or whenever the operator asks for a status sweep.

## When not to use

- For terminal-state knowledge capture — that is handled inline by the
  applications-tracker protocol gate in root `CLAUDE.md`, not by this
  skill.

## Inputs

- `applications.md` (all sections).
- Each application folder's `submission-log.md` for last-event dates.

## Steps

1. Read `applications.md`. Parse every entry into:
   - status prefix
   - date (from the entry line)
   - folder path
2. For each entry, open the folder's `submission-log.md` and find the most
   recent event date.
3. Compute age = today - most-recent-event-date.
4. Categorise:
   - `[ACTIVE]` aged > 7d: stalled draft — surface for action.
   - `[SUBMITTED]` aged > 14d with no `reply` event: ghosted — propose
     follow-up.
   - `[INTERVIEW]` with an upcoming `next` date within 7d: prep prompt.
   - `[BLOCKED]` of any age: surface diagnosis from the log.
5. Print a single grouped report:

   ```
   STALLED DRAFTS (n):
     - 2026-05-10 — Acme / Sr DE   (active 14d, last event drafted)

   GHOSTED (n):
     - 2026-05-01 — Foo / Mgr DE   (submitted 17d, no reply)

   INTERVIEWS NEEDING PREP (n):
     - 2026-05-26 — Bar / Director (screen Wed)

   BLOCKED (n):
     - 2026-05-15 — Baz / Staff DE (auth expired on lever)
   ```

6. Do not auto-act. The operator decides each follow-up.

## Output

- A grouped report printed to chat.
- No file changes.

## Notes

- This is a read-only skill by design. Any actions taken on the report
  (sending a follow-up, scheduling prep) are done through the relevant
  tools and recorded in the affected application's `submission-log.md`.
