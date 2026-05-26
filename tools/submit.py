#!/usr/bin/env python3
"""
Submit job applications using Playwright browser automation.

Reads '👍 Approved' jobs from tracker.md, finds pre-generated cover letter
and tailored resume, converts the resume to PDF, then fills the application
form on Greenhouse or Lever portals. Pauses before submitting so you can
review everything before clicking Submit yourself.

Usage:
    python tools/submit.py                   # process all approved jobs
    python tools/submit.py --company "Acme"  # one company only

Supported portals: Greenhouse (boards.greenhouse.io), Lever (jobs.lever.co)
Unknown portals: browser opens at the job URL for manual submission.

Prerequisites:
    pip install playwright fpdf2
    playwright install chromium

Generate materials first (in a Claude Code session):
    "Generate cover letter and tailored resume for <Company> — here's the JD: ..."
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    sys.exit("Run: pip install playwright && playwright install chromium")

try:
    from fpdf import FPDF
except ImportError:
    sys.exit("Run: pip install fpdf2")

REPO_ROOT = Path(__file__).parent.parent
TRACKER_PATH = REPO_ROOT / "applications" / "tracker.md"
COVER_LETTERS_DIR = REPO_ROOT / "cover-letters" / "generated"
RESUMES_DIR = REPO_ROOT / "applications" / "resumes"
PDF_DIR = REPO_ROOT / "applications" / "pdfs"

APPROVED_STATUS = "👍 Approved"
APPLIED_STATUS  = "✉️ Applied"

MICHAEL = {
    "first_name": "Michael",
    "last_name":  "Marchese",
    "full_name":  "Michael Marchese",
    "email":      "Michael.Marchese92@gmail.com",
    "phone":      "647-284-0570",
    "linkedin":   "https://linkedin.com/in/michael-d-marchese",
    "location":   "Toronto, ON",
    "current_org": "VitalHub Corp",
}


# ---------------------------------------------------------------------------
# Tracker helpers
# ---------------------------------------------------------------------------

def parse_approved_jobs(company_filter: str | None = None) -> list[dict]:
    tracker = TRACKER_PATH.read_text()
    pattern = r"\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|"
    jobs = []
    for m in re.finditer(pattern, tracker):
        cells = [c.strip() for c in m.groups()]
        date, company, role, url, status = cells[:5]
        if APPROVED_STATUS not in status:
            continue
        if company.lower() in ("company", "---"):
            continue
        if company_filter and company_filter.lower() not in company.lower():
            continue
        jobs.append({"date": date, "company": company, "role": role, "url": url})
    return jobs


def mark_applied(company: str, role: str):
    tracker = TRACKER_PATH.read_text()
    lines = []
    for line in tracker.splitlines():
        if APPROVED_STATUS in line and company.lower() in line.lower() and role.lower() in line.lower():
            line = line.replace(APPROVED_STATUS, APPLIED_STATUS)
        lines.append(line)
    TRACKER_PATH.write_text("\n".join(lines))


# ---------------------------------------------------------------------------
# Material lookup
# ---------------------------------------------------------------------------

def latest(directory: Path, slug: str, ext: str) -> Path | None:
    matches = sorted(directory.glob(f"{slug}_*.{ext}"), reverse=True)
    return matches[0] if matches else None


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

def _safe(text: str) -> str:
    return text.encode("latin-1", "replace").decode("latin-1")


def md_to_pdf(md_path: Path, pdf_path: Path) -> Path:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    raw = md_path.read_text()
    # Strip YAML frontmatter
    raw = re.sub(r"^---\n.*?\n---\n\n?", "", raw, flags=re.DOTALL)

    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()

    for line in raw.split("\n"):
        stripped = line.strip()
        # Strip inline markdown markers for display
        clean = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", stripped)
        clean = re.sub(r"`([^`]+)`", r"\1", clean)
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)

        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 9, _safe(clean[2:].strip() if clean.startswith("# ") else clean), ln=True)
        elif line.startswith("## "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, _safe(clean[3:].strip() if clean.startswith("## ") else clean), ln=True)
            pdf.set_draw_color(180, 180, 180)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
        elif line.startswith("### "):
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, _safe(clean[4:].strip() if clean.startswith("### ") else clean), ln=True)
        elif stripped == "":
            pdf.ln(2)
        else:
            pdf.set_font("Helvetica", "", 9)
            try:
                pdf.multi_cell(0, 5, _safe(clean))
            except Exception:
                pass

    pdf.output(str(pdf_path))
    return pdf_path


# ---------------------------------------------------------------------------
# Form helpers
# ---------------------------------------------------------------------------

def _fill(page, selector: str, value: str):
    try:
        el = page.locator(selector).first
        if el.count():
            el.fill(value)
    except Exception:
        pass


def _click(page, selector: str):
    try:
        page.locator(selector).first.click()
    except Exception:
        pass


def _pause(job: dict):
    print()
    print("  ✅ Form filled. Review everything in the browser.")
    print("  Submit the form yourself, then press Enter here to continue →", end=" ", flush=True)
    input()


# ---------------------------------------------------------------------------
# Portal submitters
# ---------------------------------------------------------------------------

def submit_greenhouse(page, job: dict, resume_pdf: Path, cover_letter_md: Path):
    page.goto(job["url"], wait_until="networkidle", timeout=30_000)

    # Some Greenhouse URLs land directly on the form; others need a click
    try:
        page.locator("a:has-text('Apply'), button:has-text('Apply for this Job')").first.click(timeout=5_000)
        page.wait_for_load_state("networkidle")
    except PWTimeout:
        pass

    _fill(page, "#first_name", MICHAEL["first_name"])
    _fill(page, "#last_name",  MICHAEL["last_name"])
    _fill(page, "#email",      MICHAEL["email"])
    _fill(page, "#phone",      MICHAEL["phone"])

    # LinkedIn field (varies by company config)
    for sel in [
        "input[id*='linkedin' i]",
        "input[placeholder*='linkedin' i]",
        "input[aria-label*='linkedin' i]",
    ]:
        try:
            el = page.locator(sel).first
            if el.count():
                el.fill(MICHAEL["linkedin"])
                break
        except Exception:
            pass

    # Resume upload — first file input
    file_inputs = page.locator("input[type='file']").all()
    if file_inputs:
        try:
            file_inputs[0].set_input_files(str(resume_pdf))
            print("  Resume uploaded")
        except Exception as exc:
            print(f"  Resume upload failed: {exc}")

    # Cover letter — second file input or a textarea
    if len(file_inputs) > 1:
        try:
            # Generate a cover letter PDF alongside the resume PDF
            cl_pdf = PDF_DIR / f"cl_{resume_pdf.stem}.pdf"
            if not cl_pdf.exists():
                md_to_pdf(cover_letter_md, cl_pdf)
            file_inputs[1].set_input_files(str(cl_pdf))
            print("  Cover letter uploaded (PDF)")
        except Exception as exc:
            print(f"  Cover letter upload failed: {exc}")
    else:
        for sel in ["textarea[id*='cover' i]", "textarea[name*='cover' i]", "textarea"]:
            try:
                el = page.locator(sel).first
                if el.count():
                    # Strip frontmatter for plain-text paste
                    text = cover_letter_md.read_text()
                    text = re.sub(r"^---\n.*?\n---\n\n?", "", text, flags=re.DOTALL)
                    el.fill(text)
                    print("  Cover letter pasted into textarea")
                    break
            except Exception:
                pass

    _pause(job)


def submit_lever(page, job: dict, resume_pdf: Path, cover_letter_md: Path):
    page.goto(job["url"], wait_until="networkidle", timeout=30_000)

    try:
        page.locator("a:has-text('Apply for this job'), a:has-text('Apply')").first.click(timeout=5_000)
        page.wait_for_load_state("networkidle")
    except PWTimeout:
        pass

    # Lever uses name= attributes on its inputs
    _fill(page, "input[name='name']",           MICHAEL["full_name"])
    _fill(page, "input[name='email']",           MICHAEL["email"])
    _fill(page, "input[name='phone']",           MICHAEL["phone"])
    _fill(page, "input[name='org']",             MICHAEL["current_org"])
    _fill(page, "input[name='urls[LinkedIn]']",  MICHAEL["linkedin"])
    _fill(page, "input[name='location']",        MICHAEL["location"])

    # Resume upload
    try:
        resume_input = page.locator("input[type='file']").first
        if resume_input.count():
            resume_input.set_input_files(str(resume_pdf))
            print("  Resume uploaded")
    except Exception as exc:
        print(f"  Resume upload failed: {exc}")

    # Cover letter / comments textarea
    text = cover_letter_md.read_text()
    text = re.sub(r"^---\n.*?\n---\n\n?", "", text, flags=re.DOTALL)
    for sel in ["textarea[name='comments']", "textarea[data-field='comments']", "textarea"]:
        try:
            el = page.locator(sel).first
            if el.count():
                el.fill(text)
                print("  Cover letter filled")
                break
        except Exception:
            pass

    _pause(job)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Submit approved jobs via Playwright")
    parser.add_argument("--company", help="Filter by company name (partial match)")
    args = parser.parse_args()

    jobs = parse_approved_jobs(args.company)
    if not jobs:
        print("No '👍 Approved' jobs found in tracker.md")
        return

    print(f"Found {len(jobs)} approved job(s).\n")
    submitted = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=80)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for job in jobs:
            company = job["company"]
            role    = job["role"]
            url     = job["url"]
            slug    = company.lower().replace(" ", "_").replace("/", "_")

            print(f"\n{'='*60}")
            print(f"  {role} at {company}")
            print(f"  {url}")
            print(f"{'='*60}")

            cl_path = latest(COVER_LETTERS_DIR, slug, "md")
            tr_path = latest(RESUMES_DIR,       slug, "md")

            if not cl_path or not tr_path:
                missing = []
                if not cl_path: missing.append(f"cover-letters/generated/{slug}_*.md")
                if not tr_path: missing.append(f"applications/resumes/{slug}_*.md")
                print("  Missing generated materials:")
                for m in missing:
                    print(f"    {m}")
                print("  → Ask Claude to generate them first, then re-run submit.py")
                continue

            print(f"  Cover letter : {cl_path.name}")
            print(f"  Resume (MD)  : {tr_path.name}")

            print("  Converting resume to PDF...")
            pdf_path = PDF_DIR / f"{slug}_{datetime.now().strftime('%Y%m%d')}.pdf"
            md_to_pdf(tr_path, pdf_path)
            print(f"  PDF          : {pdf_path.name}")

            if not url or url in ("#", "—", "Job URL", ""):
                print("  No URL recorded — skipping automation. Add the URL to tracker.md first.")
                continue

            portal = (
                "greenhouse" if "greenhouse.io" in url else
                "lever"      if "lever.co"      in url else
                "unknown"
            )
            print(f"  Portal: {portal}")

            try:
                if portal == "greenhouse":
                    submit_greenhouse(page, job, pdf_path, cl_path)
                elif portal == "lever":
                    submit_lever(page, job, pdf_path, cl_path)
                else:
                    print("  Unrecognised portal — opening browser for manual submission.")
                    page.goto(url, timeout=30_000)
                    _pause(job)

                mark_applied(company, role)
                print(f"  Tracker updated → {APPLIED_STATUS}")
                submitted.append(f"{role} at {company}")

            except KeyboardInterrupt:
                print("\n  Skipped.")
            except Exception as exc:
                print(f"  Error: {exc}")
                print("  Browser left open — complete manually. Press Enter to continue →", end=" ", flush=True)
                input()

        browser.close()

    print(f"\n{'='*60}")
    if submitted:
        print(f"Submitted {len(submitted)} application(s):")
        for s in submitted:
            print(f"  ✅ {s}")
    else:
        print("No applications submitted this run.")


if __name__ == "__main__":
    main()
