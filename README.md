# Personal Knowledge Hub

A version-controlled knowledge base maintained by an LLM, with a job-search workflow layered on top.

Two systems live here:

1. **The wiki** (`raw/` + `wiki/`) — drop sources into `raw/`, ask Claude to ingest them, and an interlinked Markdown wiki gets built and maintained for you. See [`CLAUDE.md`](CLAUDE.md) for the full schema.
2. **The job-search hub** (`resume/`, `applications/`, `cover-letters/`, `interview-prep/`, `tools/`) — the original job board + auto-apply pipeline. Still works exactly as before.

The wiki informs the job search (company pages deepen tailored cover letters, role pages reveal patterns across postings). Neither system depends on the other.

---

## The Wiki

### How it works

- **You curate, Claude maintains.** Drop articles, book notes, transcripts, journal entries into `raw/`. Tell Claude to ingest them. It reads, summarizes, and weaves the new content into the existing wiki — updating entity pages, flagging contradictions, growing cross-references.
- **Three operations**: `ingest` (add a source), `query` (ask a question), `lint` (health-check).
- **Two index files** keep the wiki navigable: `wiki/index.md` (content catalog) and `wiki/log.md` (chronological event log).

See [`CLAUDE.md`](CLAUDE.md) for the full pattern, page types, frontmatter conventions, and workflow specs.

### Quick examples

In a Claude Code session:

- *"I dropped an article in `raw/articles/`. Ingest it."*
- *"What do we know about Microsoft Fabric so far?"*
- *"Compare VitalHub's stack with what we've seen at Shopify."*
- *"Lint the wiki — what's missing?"*

### Recommended viewer

Use [Obsidian](https://obsidian.md) pointed at this repo as a vault. The wiki uses Obsidian-style `[[wikilinks]]`, YAML frontmatter, and Title-Case filenames so the graph view, backlinks, and Dataview queries all work out of the box.

---

## The Job-Search Hub

### Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."   # only needed for the Python tools
```

### Weekly workflow

```bash
python tools/job_board.py
```

Opens a local dashboard at `http://localhost:5000` with listings from RemoteOK + whatever you paste in manually.

1. **Browse cards** — click "Show more" for the full description
2. **Add jobs manually** — paste in roles from LinkedIn, Indeed, etc.
3. **👍 Approve** — adds to `applications/tracker.md` and saves the JD to `applications/jds/`
4. **Skip** — hides the card for this session

Then in a Claude Code session, ask Claude to generate tailored materials. Optionally, ingest the JD as a wiki source first so company/role context compounds.

If you have API access, the Python pipeline also runs end-to-end:

```bash
python tools/apply.py --dry-run   # preview materials
python tools/apply.py             # generate + open URLs + update tracker
```

### Status legend

| Status | Meaning |
|--------|---------|
| 🔍 Researching | Evaluating the role |
| 📝 Preparing | Tailoring materials |
| 👍 Approved | Queued for auto-apply |
| ✉️ Applied | Submitted |
| 📞 Screening | Screen scheduled/done |
| 🔄 Interviewing | In process |
| ⏳ Waiting | Awaiting response |
| ✅ Offer | Offer received |
| ❌ Rejected | Not moving forward |
| 🚫 Withdrawn | Withdrawn |

---

## Directory Structure

```
.
├── CLAUDE.md                      # the schema — read this first
├── README.md                      # this file
├── requirements.txt
│
├── raw/                           # IMMUTABLE source documents (you curate)
│   ├── articles/
│   ├── books/
│   ├── journal/
│   ├── transcripts/
│   ├── assets/                    # images
│   └── misc/
│
├── wiki/                          # LLM-maintained knowledge base
│   ├── index.md                   # catalog of every page
│   ├── log.md                     # chronological event log
│   ├── _templates/                # page-type templates
│   ├── self/                      # Michael (profile, goals, skills)
│   ├── people/
│   ├── companies/
│   ├── roles/
│   ├── concepts/
│   ├── topics/
│   ├── sources/                   # one summary page per ingested raw doc
│   └── synthesis/                 # higher-order analyses
│
├── resume/                        # job-search: master resume
├── cover-letters/                 # job-search: template + generated letters
├── applications/                  # job-search: tracker, JDs, tailored resumes
├── interview-prep/                # job-search: STAR stories, prep notes
├── job-search/                    # job-search: cached results (gitignored)
└── tools/                         # job-search: Python scripts
```
