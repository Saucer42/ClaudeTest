# Raw Sources

This directory holds **immutable** source documents that the wiki is built from.

## Rules

- **Immutable.** Once a file lands here, Claude reads it but never edits it. If a source needs to be corrected, drop in a new version with a dated filename.
- **Curated by Michael, not the LLM.** Michael decides what goes in. Claude only reads.
- **Plain text where possible.** Markdown preferred. PDFs and images are fine but markdown is friendliest.
- **One source per file.** Don't concatenate; each file should be a single article/chapter/entry/transcript.

## Naming

Use a date prefix when one is meaningful (article publish date, journal date, transcript date):

```
raw/articles/2026-04-12 - HBR - Building Data Teams That Last.md
raw/journal/2026-05-26 - reflections on q2.md
raw/transcripts/2026-03-08 - Lex Fridman with Demis Hassabis.md
```

For evergreen reference material, the date is optional:

```
raw/books/Designing Data-Intensive Applications - Ch 3.md
```

## Subdirectories

| Dir | Use for |
|---|---|
| `articles/` | Web articles, blog posts, newsletters (e.g. from Obsidian Web Clipper) |
| `books/` | Book notes, chapter excerpts, summaries |
| `journal/` | Michael's own writing — entries, voice-note transcripts, freeform thoughts |
| `transcripts/` | Podcasts, talks, meeting notes, interview recordings |
| `assets/` | Images referenced by raw or wiki pages |
| `misc/` | Anything that doesn't fit above |

## Note on job descriptions

JDs live in `applications/jds/` (the job-search hub uses them there). They also count as raw sources — Claude can ingest them into the wiki to deepen company and role pages. No need to duplicate them under `raw/`.

## Ingesting

Once a source is dropped here, tell Claude in a Code session:

> *"Ingest `raw/articles/2026-04-12 - HBR - Building Data Teams That Last.md`."*

Claude will follow the **Ingest** workflow defined in `CLAUDE.md`.
