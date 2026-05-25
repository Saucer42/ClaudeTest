---
title: Bullets Library
status: stub
last_reviewed: 2026-05-24
---

# Bullets Library

Tagged inventory of resume bullets. The `tailor-application` skill selects
from here per posting.

## Tag scheme

Each bullet is a list item followed by an inline tag block. Tag axes
(repeatable per axis):

- `skill:<value>`   — concrete technical or leadership skill
- `role:<value>`    — role family the bullet fits
- `keyword:<value>` — ATS keyword to match

Example:

```markdown
- Migrated 25-client healthcare data platform from legacy WebFOCUS to
  metadata-driven ETL on Synapse, cutting per-client onboarding from 6 weeks
  to 9 days.
  `skill:metadata-etl` `skill:t-sql` `skill:synapse`
  `role:data-engineer` `role:manager`
  `keyword:etl` `keyword:data-migration` `keyword:healthcare`
```

## Bullets

> **TODO:** seed from `master-resume.md` after the reconcile step. One bullet
> per list item. Every bullet must carry at least one `skill:` tag and one
> `role:` tag.
