#!/usr/bin/env python3
"""
Auto-apply workflow:
  1. Read jobs with '👍 Approved' status from applications/tracker.md
  2. For each, generate a tailored resume and cover letter via Claude API
  3. Open the job URL in the browser (or send via email if configured)
  4. Update tracker status to '✉️ Applied'

Usage:
  python tools/apply.py                    # process all approved jobs
  python tools/apply.py --dry-run          # generate files only, don't update tracker or open URLs
  python tools/apply.py --company "Acme"   # process only one company

Prerequisites:
  - Job description saved to applications/jds/<company_slug>_<anything>.txt
  - ANTHROPIC_API_KEY set in environment
  - (Optional) SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM set for email applications
"""

import argparse
import os
import re
import smtplib
import sys
import webbrowser
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).parent.parent
TRACKER_PATH = REPO_ROOT / "applications" / "tracker.md"
JDS_DIR = REPO_ROOT / "applications" / "jds"
RESUME_PATH = REPO_ROOT / "resume" / "resume.md"
COVER_LETTERS_DIR = REPO_ROOT / "cover-letters" / "generated"
TAILORED_RESUMES_DIR = REPO_ROOT / "applications" / "resumes"

APPROVED_STATUS = "👍 Approved"
APPLIED_STATUS = "✉️ Applied"


# ---------------------------------------------------------------------------
# Tracker parsing
# ---------------------------------------------------------------------------

def parse_approved_jobs(company_filter: str | None = None) -> list[dict]:
    """Return rows from the Active Applications table with Approved status."""
    tracker = TRACKER_PATH.read_text()
    # Matches any pipe-delimited table row with 8 cells
    pattern = r"\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|"
    jobs = []
    for m in re.finditer(pattern, tracker):
        cells = [c.strip() for c in m.groups()]
        date, company, role, url, status, cover_letter, followup, notes = cells
        if APPROVED_STATUS not in status:
            continue
        if company_filter and company_filter.lower() not in company.lower():
            continue
        # Skip header row
        if company.lower() in ("company", "---"):
            continue
        jobs.append({
            "date": date,
            "company": company,
            "role": role,
            "url": url.strip(),
            "notes": notes,
            "raw_match": m.group(0),
        })
    return jobs


def update_tracker_status(company: str, role: str, cover_letter_rel_path: str):
    """Replace Approved status with Applied and record the cover letter link."""
    tracker = TRACKER_PATH.read_text()
    lines = tracker.splitlines()
    updated = []
    for line in lines:
        if APPROVED_STATUS in line and company.lower() in line.lower() and role.lower() in line.lower():
            line = line.replace(APPROVED_STATUS, APPLIED_STATUS)
            parts = line.split("|")
            if len(parts) >= 7:
                parts[6] = f" [cover letter]({cover_letter_rel_path}) "
                line = "|".join(parts)
        updated.append(line)
    TRACKER_PATH.write_text("\n".join(updated))


# ---------------------------------------------------------------------------
# Job description lookup
# ---------------------------------------------------------------------------

def find_jd(company: str) -> str | None:
    """Find a job description file whose name contains the company slug."""
    slug = company.lower().replace(" ", "_")
    for f in JDS_DIR.glob("*.txt"):
        if slug in f.stem.lower():
            return f.read_text()
    return None


# ---------------------------------------------------------------------------
# Claude API calls
# ---------------------------------------------------------------------------

def _stream(client, system_blocks, prompt, max_tokens) -> str:
    text = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=max_tokens,
        system=system_blocks,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for chunk in stream.text_stream:
            print(chunk, end="", flush=True)
            text += chunk
    print()
    return text


def generate_cover_letter(client, resume: str, company: str, role: str, jd: str) -> str:
    system = [
        {
            "type": "text",
            "text": (
                "You are an expert career coach and professional cover letter writer.\n"
                "Write compelling, concise cover letters (under 400 words) tailored to the job description.\n"
                "Write in first person, in flowing paragraphs. Reference the company and role directly.\n"
                "Highlight 2-3 concrete achievements from the resume that map to key requirements.\n"
                "End with a confident call to action. Do not use bullet points.\n\n"
                f"Candidate resume:\n\n{resume}"
            ),
            "cache_control": {"type": "ephemeral"},
        }
    ]
    prompt = (
        f"Write a tailored cover letter for:\n\nCompany: {company}\nRole: {role}\n\n"
        f"Job Description:\n{jd}\n\n"
        f"Today's date: {datetime.now().strftime('%B %d, %Y')}\n\n"
        "Write the full cover letter, ready to send."
    )
    return _stream(client, system, prompt, 2048)


def generate_tailored_resume(client, resume: str, company: str, role: str, jd: str) -> str:
    system = [
        {
            "type": "text",
            "text": (
                "You are an expert ATS optimization specialist and resume writer.\n"
                "Rewrite the resume to be optimally tailored for the specific job posting.\n"
                "Keep all information truthful — rewrite bullet language to mirror the JD, "
                "reorder skills to emphasise relevance, and revise the summary.\n"
                "Preserve all factual content: dates, companies, titles, numbers.\n\n"
                f"Original resume:\n\n{resume}"
            ),
            "cache_control": {"type": "ephemeral"},
        }
    ]
    prompt = (
        f"Rewrite this resume tailored for:\n\nCompany: {company}\nRole: {role}\n\n"
        f"Job Description:\n{jd}\n\n"
        "Output the full tailored resume in Markdown format."
    )
    return _stream(client, system, prompt, 4096)


# ---------------------------------------------------------------------------
# Email (optional)
# ---------------------------------------------------------------------------

def send_email_application(to_address: str, company: str, role: str, cover_letter: str, resume_path: Path):
    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    from_addr = os.environ.get("SMTP_FROM", user)

    if not all([host, user, password]):
        print("  (Email skipped — SMTP_HOST / SMTP_USER / SMTP_PASS not set)")
        return

    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = to_address
    msg["Subject"] = f"Application for {role} — Michael Marchese"
    msg.attach(MIMEText(cover_letter, "plain"))

    with open(resume_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={resume_path.name}")
    msg.attach(part)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(from_addr, to_address, msg.as_string())
    print(f"  Email sent to {to_address}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Auto-apply to approved jobs from tracker")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate files but don't update tracker, open URLs, or send email")
    parser.add_argument("--company", help="Process only this company (partial match)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser for portal URLs")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: ANTHROPIC_API_KEY environment variable not set.")

    jobs = parse_approved_jobs(args.company)
    if not jobs:
        print("No jobs with '👍 Approved' status found in tracker.")
        return

    print(f"Found {len(jobs)} approved job(s).\n")
    client = anthropic.Anthropic(api_key=api_key)
    resume = RESUME_PATH.read_text()
    COVER_LETTERS_DIR.mkdir(parents=True, exist_ok=True)
    TAILORED_RESUMES_DIR.mkdir(parents=True, exist_ok=True)

    for job in jobs:
        company = job["company"]
        role = job["role"]
        url = job["url"]
        print(f"\n{'='*60}")
        print(f"  {role} at {company}")
        print(f"{'='*60}\n")

        jd = find_jd(company)
        if not jd:
            slug = company.lower().replace(" ", "_")
            print(f"  WARNING: No JD found. Save it to: applications/jds/{slug}_<anything>.txt")
            print("  Skipping.\n")
            continue

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = company.lower().replace(" ", "_")

        print("Generating cover letter...")
        cl_text = generate_cover_letter(client, resume, company, role, jd)
        cl_path = COVER_LETTERS_DIR / f"{slug}_{timestamp}.md"
        cl_header = f"---\ncompany: {company}\nrole: {role}\ngenerated: {datetime.now().isoformat()}\n---\n\n"
        cl_path.write_text(cl_header + cl_text)
        print(f"  Saved: {cl_path.relative_to(REPO_ROOT)}")

        print("\nGenerating tailored resume...")
        tr_text = generate_tailored_resume(client, resume, company, role, jd)
        tr_path = TAILORED_RESUMES_DIR / f"{slug}_{timestamp}.md"
        tr_path.write_text(f"---\ncompany: {company}\nrole: {role}\ngenerated: {datetime.now().isoformat()}\n---\n\n" + tr_text)
        print(f"  Saved: {tr_path.relative_to(REPO_ROOT)}")

        if not args.dry_run:
            cl_rel = str(cl_path.relative_to(REPO_ROOT))
            update_tracker_status(company, role, cl_rel)
            print(f"  Tracker updated → {APPLIED_STATUS}")

            # Email application if URL looks like an email address
            if url and "@" in url:
                send_email_application(url, company, role, cl_text, tr_path)
            elif url and url not in ("#", "—", "Job URL", "") and not args.no_browser:
                print(f"  Opening: {url}")
                webbrowser.open(url)

        print(f"\nApplication package ready for {company}.")
        print(f"  Cover letter : {cl_path.name}")
        print(f"  Resume       : {tr_path.name}")

    print(f"\n{'='*60}")
    print("Done! Review materials in cover-letters/generated/ and applications/resumes/")
    if args.dry_run:
        print("(Dry run — tracker not updated, browser not opened)")


if __name__ == "__main__":
    main()
