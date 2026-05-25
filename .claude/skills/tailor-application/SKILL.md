---
name: tailor-application
description: For each posting in postings/interested/, create applications/YYYY-MM-DD_company_role/, draft a tailored resume, cover letter, and screening answers via Claude (model claude-sonnet-4-6, prompt caching on master-resume.md and bullets-library.md), then render PDFs via the render-pdf skill. Trigger phrases - "tailor application", "apply to <job>", "draft materials for <company>", "tailor resume for <posting>".
---

# tailor-application

## When to use

- `postings/interested/` has untreated postings the operator wants to apply
  to.
- The operator names a specific interested posting and asks for materials.

## When not to use

- The posting is still in `inbox/` — run `triage-postings` first.
- The materials already exist — re-run `render-pdf` directly instead of
  re-tailoring.

## Inputs

- One or more posting files from `postings/interested/`.
- `profile/master-resume.md` (cached as a system message — see Caching).
- `profile/bullets-library.md` (cached).
- `profile/screening-answers.md` (reference, not cached).
- `profile/cover-letter-templates/` (reference).
- `profile/targets.md` (reference).
- `templates/` (for the subsequent PDF render).

## Steps

1. Resolve the target posting(s). If multiple, process one at a time.
2. Slugify company and role; compute folder name
   `applications/<today>_<company-slug>_<role-slug>/`.
3. Create the folder. Copy the posting file into it as `posting.md`.
4. Build the Claude request:
   - System message blocks (cached, `cache_control: ephemeral`):
     - the contents of `profile/master-resume.md`
     - the contents of `profile/bullets-library.md`
   - User message: the JD body + a structured instruction to draft
     `resume.md`, `cover-letter.md`, and (if the posting requires it)
     `answers.md`.
   - Model: `claude-sonnet-4-6`.
5. Write the three files into the application folder. Write-as-you-go: do
   not batch.
6. Invoke `render-pdf` for `resume.md` and `cover-letter.md`.
7. Create `submission-log.md` with the initial `drafted` event (date, model,
   skill version).
8. Add an entry to `applications.md` under `## Active` with prefix
   `[ACTIVE]`.

## Caching

The first two system blocks (master resume + bullets library) carry
`cache_control: {"type": "ephemeral"}`. Subsequent tailoring runs within the
cache TTL re-use the prefix.

## Output

- New folder `applications/<date>_<company>_<role>/` containing
  `posting.md`, `resume.md`, `resume.pdf`, `cover-letter.md`,
  `cover-letter.pdf`, optionally `answers.md`, and `submission-log.md`.
- New entry in `applications.md` under `## Active`.
- Posting file remains in `postings/interested/` until `auto-apply` moves
  it.

## Notes

- Do not invent experience. Drafts must reuse content from
  `bullets-library.md` and `master-resume.md`; if a JD asks for a skill not
  in the library, flag it for the operator rather than fabricate.
- Cover letter length: 3 short paragraphs unless the posting explicitly
  asks for more.
