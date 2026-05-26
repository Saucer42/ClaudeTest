# Wiki Log

Chronological, append-only record of what happened in the wiki. Every entry uses the prefix:

```
## [YYYY-MM-DD] <op> | <short title>
```

Ops: `ingest`, `query`, `lint`, `restructure`, `note`.

Tip: `grep "^## \[" wiki/log.md | tail -10` shows the last 10 events.

---

## [2026-05-26] restructure | Wiki scaffolded

- Created `raw/` (immutable sources) and `wiki/` (LLM-maintained pages).
- Wrote schema in `CLAUDE.md`: page types, frontmatter, naming, ingest/query/lint workflows.
- Added page templates in `wiki/_templates/` (entity, concept, topic, source, synthesis).
- Seeded `wiki/self/` with stubs for Michael, Goals, Skills (drawn from existing resume + CLAUDE.md context).
- Existing job-search hub (`resume/`, `applications/`, `cover-letters/`, `interview-prep/`, `tools/`) preserved alongside.
