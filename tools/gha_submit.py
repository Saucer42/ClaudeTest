#!/usr/bin/env python3
"""
Headless job application submission for GitHub Actions.

Fills Greenhouse and Lever application forms using headless Playwright,
takes a full-page screenshot for review, and optionally clicks Submit.
Called by .github/workflows/submit-application.yml — not meant for local use
(use tools/submit.py locally instead, which runs a headed browser).

Usage:
    python tools/gha_submit.py --company "Shopify" --dry-run   # fill + screenshot only
    python tools/gha_submit.py --company "Shopify"             # fill + screenshot + submit

Workflow:
    1. Run workflow with dry_run=true → review screenshot artifact in GitHub Actions
    2. Run workflow with dry_run=false → form submitted, tracker updated to ✉️ Applied
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

REPO_ROOT         = Path(__file__).parent.parent
TRACKER_PATH      = REPO_ROOT / "applications" / "tracker.md"
COVER_LETTERS_DIR = REPO_ROOT / "cover-letters" / "generated"
RESUMES_DIR       = REPO_ROOT / "applications" / "resumes"
PDF_DIR           = REPO_ROOT / "applications" / "pdfs"
SCREENSHOTS_DIR   = REPO_ROOT / "applications" / "screenshots"

APPROVED_STATUS = "👍 Approved"
APPLIED_STATUS  = "✉️ Applied"

MICHAEL = {
    "first_name":  "Michael",
    "last_name":   "Marchese",
    "full_name":   "Michael Marchese",
    "email":       "Michael.Marchese92@gmail.com",
    "phone":       "647-284-0570",
    "linkedin":    "https://linkedin.com/in/michael-d-marchese",
    "location":    "Toronto, ON",
    "current_org": "VitalHub Corp",
}


# ---------------------------------------------------------------------------
# Tracker
# ---------------------------------------------------------------------------

def find_job(company: str) -> dict:
    tracker = TRACKER_PATH.read_text()
    pattern = r"\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|"
    for m in re.finditer(pattern, tracker):
        cells = [c.strip() for c in m.groups()]
        _date, comp, role, url, status = cells[:5]
        if APPROVED_STATUS not in status:
            continue
        if comp.lower() in ("company", "---"):
            continue
        if company.lower() in comp.lower():
            # Strip Markdown link syntax: [text](url) → url
            md_link = re.match(r"\[.*?\]\((.*?)\)", url)
            clean_url = md_link.group(1) if md_link else url
            return {"company": comp, "role": role, "url": clean_url}
    return {}


def mark_applied(company: str, role: str):
    tracker = TRACKER_PATH.read_text()
    lines = []
    for line in tracker.splitlines():
        if (APPROVED_STATUS in line
                and company.lower() in line.lower()
                and role.lower() in line.lower()):
            line = line.replace(APPROVED_STATUS, APPLIED_STATUS)
        lines.append(line)
    TRACKER_PATH.write_text("\n".join(lines))


# ---------------------------------------------------------------------------
# File lookup
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
    raw = re.sub(r"^---\n.*?\n---\n\n?", "", raw, flags=re.DOTALL)

    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()

    for line in raw.split("\n"):
        clean = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", line.strip())
        clean = re.sub(r"`([^`]+)`",               r"\1", clean)
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)",   r"\1", clean)

        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 9, _safe(clean), new_x="LMARGIN", new_y="NEXT")
        elif line.startswith("## "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, _safe(clean), new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(200, 200, 200)
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.line(x, y, x + 170, y)
        elif line.startswith("### "):
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, _safe(clean), new_x="LMARGIN", new_y="NEXT")
        elif line.strip() == "":
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
# Form filling — shared helper
# ---------------------------------------------------------------------------

def _fill(page, selector: str, value: str):
    try:
        el = page.locator(selector).first
        if el.count():
            el.fill(value)
    except Exception:
        pass


def _click_submit(page):
    try:
        page.locator(
            "input[type='submit'], button[type='submit'], button:has-text('Submit')"
        ).first.click(timeout=10_000)
        page.wait_for_load_state("networkidle", timeout=15_000)
        print("  Submitted.")
    except Exception as exc:
        print(f"  Submit click failed: {exc}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Greenhouse
# ---------------------------------------------------------------------------

def fill_greenhouse(page, url: str, resume_pdf: Path, cover_letter_md: Path, dry_run: bool):
    page.goto(url, wait_until="networkidle", timeout=30_000)

    try:
        page.locator(
            "a:has-text('Apply'), button:has-text('Apply for this Job')"
        ).first.click(timeout=5_000)
        page.wait_for_load_state("networkidle")
    except PWTimeout:
        pass

    _fill(page, "#first_name", MICHAEL["first_name"])
    _fill(page, "#last_name",  MICHAEL["last_name"])
    _fill(page, "#email",      MICHAEL["email"])
    _fill(page, "#phone",      MICHAEL["phone"])

    for sel in ["input[id*='linkedin' i]", "input[placeholder*='linkedin' i]"]:
        try:
            el = page.locator(sel).first
            if el.count():
                el.fill(MICHAEL["linkedin"])
                break
        except Exception:
            pass

    file_inputs = page.locator("input[type='file']").all()
    if file_inputs:
        try:
            file_inputs[0].set_input_files(str(resume_pdf))
            print("  Resume uploaded")
        except Exception as exc:
            print(f"  Resume upload failed: {exc}")

    if len(file_inputs) > 1:
        try:
            cl_pdf = PDF_DIR / f"cl_{resume_pdf.stem}.pdf"
            if not cl_pdf.exists():
                md_to_pdf(cover_letter_md, cl_pdf)
            file_inputs[1].set_input_files(str(cl_pdf))
            print("  Cover letter uploaded (PDF)")
        except Exception as exc:
            print(f"  Cover letter file upload failed: {exc}")
    else:
        text = _strip_frontmatter(cover_letter_md.read_text())
        for sel in ["textarea[id*='cover' i]", "textarea[name*='cover' i]", "textarea"]:
            try:
                el = page.locator(sel).first
                if el.count():
                    el.fill(text)
                    print("  Cover letter pasted into textarea")
                    break
            except Exception:
                pass

    if not dry_run:
        _click_submit(page)


# ---------------------------------------------------------------------------
# Lever
# ---------------------------------------------------------------------------

def fill_lever(page, url: str, resume_pdf: Path, cover_letter_md: Path, dry_run: bool):
    page.goto(url, wait_until="networkidle", timeout=30_000)

    try:
        page.locator(
            "a:has-text('Apply for this job'), a:has-text('Apply')"
        ).first.click(timeout=5_000)
        page.wait_for_load_state("networkidle")
    except PWTimeout:
        pass

    _fill(page, "input[name='name']",          MICHAEL["full_name"])
    _fill(page, "input[name='email']",          MICHAEL["email"])
    _fill(page, "input[name='phone']",          MICHAEL["phone"])
    _fill(page, "input[name='org']",            MICHAEL["current_org"])
    _fill(page, "input[name='urls[LinkedIn]']", MICHAEL["linkedin"])

    # Location — Lever uses several different field names across companies
    for sel in [
        "input[name='location']",
        "input[name='currentLocation']",
        "input[placeholder*='location' i]",
        "input[placeholder*='city' i]",
    ]:
        try:
            el = page.locator(sel).first
            if el.count():
                el.fill(MICHAEL["location"])
                print("  Location filled")
                break
        except Exception:
            pass

    try:
        resume_input = page.locator("input[type='file']").first
        if resume_input.count():
            resume_input.set_input_files(str(resume_pdf))
            print("  Resume uploaded")
    except Exception as exc:
        print(f"  Resume upload failed: {exc}")

    # Cover letter — only fill if a dedicated comments/cover-letter textarea exists.
    # Do NOT fall back to a generic textarea selector — Lever uses textareas for
    # custom questions and a greedy match will paste the letter into the wrong field.
    text = _strip_frontmatter(cover_letter_md.read_text())
    cl_filled = False
    for sel in ["textarea[name='comments']", "textarea[data-field='comments']"]:
        try:
            el = page.locator(sel).first
            if el.count():
                el.fill(text)
                print("  Cover letter filled")
                cl_filled = True
                break
        except Exception:
            pass
    if not cl_filled:
        print("  No dedicated cover letter field found — skipping (paste manually if needed)")

    if not dry_run:
        _click_submit(page)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_frontmatter(text: str) -> str:
    return re.sub(r"^---\n.*?\n---\n\n?", "", text, flags=re.DOTALL)


def detect_portal(url: str) -> str:
    if "greenhouse.io" in url:
        return "greenhouse"
    if "lever.co" in url:
        return "lever"
    return "unknown"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--company",  required=True, help="Company name (partial match against tracker)")
    parser.add_argument("--dry-run",  action="store_true", help="Fill form but do not submit")
    args = parser.parse_args()

    job = find_job(args.company)
    if not job:
        print(f"No '👍 Approved' job found for '{args.company}' in tracker.md")
        sys.exit(1)

    company = job["company"]
    role    = job["role"]
    url     = job["url"]
    slug    = re.sub(r"[^a-z0-9]+", "_", company.lower()).strip("_")
    ts      = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n{'='*60}")
    print(f"  {role} at {company}")
    print(f"  {url}")
    print(f"  Mode: {'DRY RUN — screenshot only' if args.dry_run else 'LIVE — will submit'}")
    print(f"{'='*60}\n")

    cl_path = latest(COVER_LETTERS_DIR, slug, "md")
    tr_path = latest(RESUMES_DIR,       slug, "md")

    if not cl_path or not tr_path:
        missing = []
        if not cl_path: missing.append(f"cover-letters/generated/{slug}_*.md")
        if not tr_path: missing.append(f"applications/resumes/{slug}_*.md")
        print("Missing generated materials — generate them in a Claude Code session first:")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)

    print(f"Cover letter : {cl_path.name}")
    print(f"Resume (MD)  : {tr_path.name}")

    print("Converting resume to PDF...")
    pdf_path = PDF_DIR / f"{slug}_{ts}.pdf"
    md_to_pdf(tr_path, pdf_path)
    print(f"PDF          : {pdf_path.name}")

    portal = detect_portal(url)
    print(f"Portal       : {portal}\n")

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    screenshot_path = SCREENSHOTS_DIR / f"{slug}_{ts}.png"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        try:
            if portal == "greenhouse":
                fill_greenhouse(page, url, pdf_path, cl_path, dry_run=args.dry_run)
            elif portal == "lever":
                fill_lever(page, url, pdf_path, cl_path, dry_run=args.dry_run)
            else:
                print("Unknown portal — navigating to URL for screenshot only")
                page.goto(url, timeout=30_000)
        except Exception as exc:
            print(f"  Error during form filling: {exc}")
            page.screenshot(path=str(screenshot_path), full_page=True)
            browser.close()
            sys.exit(1)

        page.screenshot(path=str(screenshot_path), full_page=True)
        browser.close()

    print(f"\nScreenshot   : {screenshot_path.relative_to(REPO_ROOT)}")

    if not args.dry_run:
        mark_applied(company, role)
        print(f"Tracker      : updated to {APPLIED_STATUS}")

    print(f"\n{'='*60}")
    if args.dry_run:
        print("Dry run complete.")
        print("→ Download the screenshot from the Actions run Artifacts to review.")
        print("→ Re-run the workflow with 'Dry run' unchecked to submit for real.")
    else:
        print(f"Application submitted: {role} at {company}")


if __name__ == "__main__":
    main()
