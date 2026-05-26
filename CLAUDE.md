# Claude Session Memory — Personal Knowledge Hub

This file is read automatically at the start of every Claude Code session.
It defines how this repository works and what the LLM's job is.

---

## Who This Is For

**Michael Marchese** — Toronto-based senior data leader.
- Current role: Manager, Data Integration & Reporting Solutions at VitalHub Corp (May 2024–Present)
- 7-person distributed team, 25+ client orgs, healthcare/enterprise domain
- Key skills: SQL Server (T-SQL), Data Migration Architecture, Metadata-Driven ETL, WebFOCUS, Fabric/Synapse, Kimball, AI-Augmented Workflow Design
- Targeting: Manager/Director AND Senior IC/Architect roles, any industry, any location (Toronto, remote Canada, remote NA)
- Contact: Michael.Marchese92@gmail.com | 647-284-0570 | linkedin.com/in/michael-d-marchese

For a deeper, evolving picture of Michael, see `wiki/self/Michael.md` and the rest of `wiki/self/`.

---

## What This Repo Is

A **personal knowledge hub** built on the LLM-Wiki pattern, with a job-search workflow layered on top.

Two parallel systems live here:

1. **The wiki** (`raw/` + `wiki/`) — an LLM-maintained personal knowledge base. Michael curates sources; Claude reads them and incrementally builds out an interlinked Markdown wiki covering everything Michael wants to track: career, companies, people, concepts, reading, goals, projects.

2. **The job-search hub** (`resume/`, `applications/`, `cover-letters/`, `interview-prep/`, `tools/`, `job-search/`) — the original domain-specific workflow for finding, tailoring, and applying to jobs. It still works the same way. The wiki *informs* it (e.g. a company page in the wiki can deepen a tailored cover letter), but neither system depends on the other.

---

## The Wiki Pattern (Core Idea)

Most RAG systems re-derive knowledge on every query. This wiki is different: it's a **persistent, compounding artifact**. When a new source is ingested, Claude reads it once, extracts what matters, and integrates it into the existing wiki — updating entity pages, revising summaries, flagging contradictions, strengthening the synthesis. Cross-references are already there. Synthesis already reflects everything read. The wiki gets richer with every source.

**Michael's job:** curate sources, ask good questions, direct exploration.
**Claude's job:** everything else — reading, summarizing, filing, cross-referencing, maintaining consistency.

Michael (almost) never writes wiki pages by hand. Claude writes and maintains all of `wiki/`.

---

## Three Layers

| Layer | Path | Who Owns It | Mutability |
|---|---|---|---|
| **Raw sources** | `raw/` (+ `applications/jds/` for job descriptions) | Michael curates | Immutable. Claude reads but never modifies. |
| **Wiki** | `wiki/` | Claude maintains | Mutable. Claude creates, edits, restructures freely. |
| **Schema** | `CLAUDE.md` (this file) | Co-evolved | Updated together when conventions change. |

---

## Repository Structure

```
.
├── CLAUDE.md                  ← you are here (the schema)
├── README.md                  ← human-facing usage guide
├── requirements.txt
├── .gitignore
│
├── raw/                       ← IMMUTABLE source documents
│   ├── articles/              ← clipped web articles, blog posts (markdown preferred)
│   ├── books/                 ← book notes, chapters, excerpts
│   ├── journal/               ← Michael's own entries, voice notes, freeform thoughts
│   ├── transcripts/           ← podcast/meeting/talk/interview transcripts
│   ├── assets/                ← images referenced by raw or wiki pages
│   └── misc/                  ← anything that doesn't fit above
│
├── wiki/                      ← LLM-MAINTAINED knowledge base
│   ├── index.md               ← catalog of every wiki page (kept current)
│   ├── log.md                 ← append-only event log
│   ├── _templates/            ← page-type templates (entity, concept, topic, source, synthesis)
│   ├── self/                  ← Michael (canonical "who I am", goals, skills, values)
│   ├── people/                ← recruiters, mentors, colleagues, contacts, public figures
│   ├── companies/             ← organizations, employers, vendors
│   ├── roles/                 ← role pattern analyses (e.g. "Director of Data" across postings)
│   ├── concepts/              ← frameworks, methodologies, ideas (Kimball, negotiation, etc.)
│   ├── topics/                ← deep-dive subject pages (Fabric, Toronto data market, etc.)
│   ├── sources/               ← per-source summary pages (one per ingested raw doc)
│   └── synthesis/             ← higher-order analyses spanning multiple pages
│
├── resume/                    ← (job-search hub) master resume
├── cover-letters/             ← (job-search hub) templates + generated letters
├── applications/              ← (job-search hub) tracker, JD archive, tailored resumes
│   ├── tracker.md             ← application pipeline (functions as job-search domain log)
│   └── jds/                   ← job descriptions (also serve as raw sources for the wiki)
├── interview-prep/            ← (job-search hub) STAR stories, prep notes
├── job-search/                ← (job-search hub) cached search results (gitignored)
└── tools/                     ← (job-search hub) Python scripts: job_board.py, apply.py, etc.
```

---

## Wiki Conventions

### Page types

Every wiki page (except `index.md`, `log.md`, and files under `_templates/`) has a **type** declared in its frontmatter. Use the template in `wiki/_templates/<type>.md` as a starting point.

| Type | Purpose | Examples |
|---|---|---|
| `entity` | A specific thing in the world: a person, company, product, place | `wiki/companies/Shopify.md`, `wiki/people/Jane Doe.md` |
| `concept` | An abstract idea, framework, methodology, or principle | `wiki/concepts/Kimball Dimensional Modeling.md`, `wiki/concepts/Salary Negotiation.md` |
| `topic` | A deep-dive subject area that synthesizes multiple sources | `wiki/topics/Microsoft Fabric.md`, `wiki/topics/Toronto Data Job Market.md` |
| `source` | A summary of one ingested raw document | `wiki/sources/2026-05-12 HBR Article on Data Teams.md` |
| `synthesis` | An LLM-generated higher-order analysis answering a specific question | `wiki/synthesis/Comparison of Fabric vs Databricks for Healthcare.md` |

### Frontmatter

Every wiki page begins with YAML frontmatter:

```yaml
---
type: entity            # entity | concept | topic | source | synthesis
tags: [healthcare, data-platforms]
created: 2026-05-26
updated: 2026-05-26
sources: ["2026-05-12 HBR Article on Data Teams"]   # raw-source page names this page draws from
status: active          # stub | draft | active | stable
---
```

- `type` — required, drives template choice
- `tags` — lowercase, kebab-case, broad categorization
- `created` / `updated` — ISO dates; update `updated` whenever the page changes meaningfully
- `sources` — list of `wiki/sources/` page names that this page synthesizes (empty `[]` for self pages and templates)
- `status` — `stub` (placeholder) → `draft` (rough) → `active` (current and useful) → `stable` (rarely changes)

### Naming and linking

- **Filenames**: Title Case with spaces, `.md` extension. e.g. `wiki/companies/VitalHub Corp.md`.
- **Internal links**: Obsidian-style wikilinks: `[[VitalHub Corp]]`, `[[Director of Data]]`, `[[Kimball Dimensional Modeling]]`. Aliases when the link text should differ: `[[VitalHub Corp|the company]]`.
- **Source links**: link to the source page in `wiki/sources/`, which in turn links to the raw file. Don't link directly from entity/concept/topic pages to `raw/` files — go through the source page so provenance is traceable.
- **Cross-references**: aggressively link related concepts/entities. The graph density is what makes the wiki valuable.

### One file, one idea

Each page covers one entity / concept / topic. If a page is sprawling, split it. If two pages are constantly cross-referenced and small, merge them. Claude makes these calls during ingest and lint passes.

---

## Operations

These are the three core workflows. When Michael invokes one, follow the workflow rather than improvising.

### Ingest

Trigger: Michael drops a file into `raw/` (or a `.txt` JD into `applications/jds/`) and says "ingest this" or names the file.

Workflow:
1. **Read** the source end-to-end. For images, view them via the Read tool. For long sources, summarize before integrating.
2. **Discuss** the key takeaways with Michael in chat — what's new, what surprised you, what conflicts with existing wiki content. Ask what to emphasize.
3. **Create a source page** at `wiki/sources/<YYYY-MM-DD Title>.md` using the source template. Include: one-paragraph summary, key claims (bulleted), notable quotes, link back to the raw file, list of wiki pages updated.
4. **Update or create related wiki pages** — entities mentioned, concepts touched, topics expanded. Add `[[wikilinks]]` everywhere relevant. Add the source page to each updated page's `sources:` frontmatter.
5. **Flag contradictions**: if a new source disagrees with existing wiki content, don't silently overwrite. Add a `> [!note] Contradicts [[Source X]]` callout and surface it to Michael.
6. **Update `wiki/index.md`** — add new pages, update one-line summaries for changed pages.
7. **Append to `wiki/log.md`**: `## [YYYY-MM-DD] ingest | <Title>` followed by what changed.

A single ingest may touch 10-15 wiki pages. That's expected and desired.

### Query

Trigger: Michael asks a question.

Workflow:
1. **Read `wiki/index.md` first** to find relevant pages. Drill into the top candidates.
2. **Answer with citations** — every non-trivial claim should link to a wiki page or a `wiki/sources/` page. e.g. *"VitalHub uses Fabric for analytics ([[VitalHub Corp]])."*
3. **Offer to file the answer back into the wiki** when the answer represents new synthesis (a comparison, an analysis, a connection). File it under `wiki/synthesis/<Question or Title>.md` and link to it from `wiki/index.md` and any source pages it draws on. Don't let valuable explorations evaporate into chat history.
4. **Append to `wiki/log.md`** for substantive queries that resulted in new pages.

### Lint

Trigger: Michael says "lint the wiki" or "health-check."

Workflow:
1. **Scan `wiki/index.md`** and walk the structure.
2. **Look for**:
   - **Contradictions** between pages (especially flagged callouts that haven't been resolved)
   - **Stale claims** that newer sources have superseded
   - **Orphan pages** with no inbound `[[wikilinks]]`
   - **Implicit concepts** — terms mentioned in 3+ pages that don't have their own page yet
   - **Missing cross-references** — pages that should link to each other but don't
   - **Frontmatter drift** — pages missing required fields, stale `updated` dates
   - **Gaps** — topics where the wiki has thin coverage and a web search could fill it
3. **Produce a report** in chat: prioritized findings + suggested fixes. Don't auto-fix without Michael's approval (lint is advisory).
4. **Append to `wiki/log.md`**: `## [YYYY-MM-DD] lint | summary of findings`.

---

## index.md and log.md

These two files are not optional — they make the wiki navigable.

### `wiki/index.md` — content catalog

Organized by directory (`self`, `people`, `companies`, `roles`, `concepts`, `topics`, `sources`, `synthesis`). Each entry: `[[Page Name]]` — one-line summary. Optionally annotate with status or source count.

Update on **every ingest** and **every new page**. If the index gets out of sync, fix it during the next lint pass.

### `wiki/log.md` — chronological event log

Append-only. Every entry starts with a consistent prefix so it's grep-able:

```
## [YYYY-MM-DD] <op> | <short title>
- bullet 1
- bullet 2
```

Where `<op>` is one of: `ingest`, `query`, `lint`, `restructure`, `note`.

Example tip: `grep "^## \[" wiki/log.md | tail -10` gives the last 10 events.

---

## Job-Search Hub (preserved domain workflow)

The original job-search system still works. It coexists with the wiki and benefits from it.

### Tracker status legend

| Status | Meaning |
|--------|---------|
| 🔍 Researching | Evaluating the role |
| 📝 Preparing | Tailoring materials manually |
| 👍 Approved | Queued — `python tools/apply.py` processes these |
| ✉️ Applied | Submitted |
| 📞 Screening | Screen scheduled/done |
| 🔄 Interviewing | In process |
| ⏳ Waiting | Awaiting response |
| ✅ Offer | Offer received |
| ❌ Rejected | Not moving forward |
| 🚫 Withdrawn | Withdrawn |

### Weekly workflow

1. `python tools/job_board.py` — opens dashboard at `localhost:5000`
2. Browse RemoteOK auto-fetches + paste in jobs from LinkedIn/Indeed
3. Click **👍 Approve** → auto-saves to `applications/tracker.md` and writes the JD to `applications/jds/`
4. In a Claude session: ask Claude to generate tailored cover letter + resume
5. Claude writes outputs to `cover-letters/generated/` and `applications/resumes/`
6. Submit; update tracker status to ✉️ Applied

### Tool usage note

Michael is on Claude Max (no separate API plan), so the Python tools (`generate_cover_letter.py`, `tailor_resume.py`, `apply.py`) cannot be invoked directly — they require `ANTHROPIC_API_KEY`. Use Claude Code sessions instead:
- "Write a cover letter for [role] at [company]"
- "Tailor my resume for this JD: …"
- "Update the tracker — I applied to Acme today"

`job_board.py` works without an API key (Flask + RemoteOK public API only).

### Wiki ↔ job-search integration

- A JD in `applications/jds/<company>_<role>.txt` can be **ingested as a raw source**. Create `wiki/sources/<YYYY-MM-DD JD - Company - Role>.md`, update `wiki/companies/<Company>.md`, update `wiki/roles/<Role pattern>.md`.
- When generating a tailored cover letter or resume, **read relevant wiki pages first** for company context, role patterns, and Michael's evolving self-profile.
- Tracker movements (Approved, Applied, Offer, etc.) are domain-specific events. Don't duplicate them in `wiki/log.md` unless they trigger a wiki update (e.g. interview notes filed back as a source).

---

## Key Technical Notes

- **Markdown everywhere**. Plain text, version-controlled, viewable in Obsidian.
- **Obsidian-friendly**: filenames with spaces, `[[wikilinks]]`, YAML frontmatter, attachments under `raw/assets/`. Michael may use Obsidian as the IDE — keep the wiki readable there.
- **No embeddings, no vector DB.** `index.md` + filesystem grep is enough at moderate scale (~hundreds of pages). Add a search tool (e.g. `qmd`) only if/when grep stops scaling.
- **Claude API model in tools/**: `claude-opus-4-7` with `thinking: {"type": "adaptive"}` (no `budget_tokens` on Opus 4.7). Resume cached via `cache_control: {"type": "ephemeral"}` on the system message.

---

## Git

- **Branch**: `claude/affectionate-hawking-jFv3U`
- **Remote**: `saucer42/claudetest`
- All work goes to this branch. Do not push to main without Michael's instruction.

---

## How to Resume This Session

1. Read this file.
2. Read `wiki/index.md` to see what's in the wiki.
3. Read the last 10 entries in `wiki/log.md` to see recent activity (`grep "^## \[" wiki/log.md | tail -10`).
4. If the user is asking about job-search status, also read `applications/tracker.md`.
5. Ask Michael what he wants to work on. Likely modes:
   - **Ingest** a new source he's about to drop in `raw/`
   - **Query** the wiki on something he's exploring
   - **Lint** the wiki for health
   - **Job search**: review tracker, generate materials, run the dashboard, set up Playwright MCP for auto-apply (still pending)
