#!/usr/bin/env python3
"""Generate a tailored cover letter using Claude API."""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import anthropic

RESUME_PATH = Path(__file__).parent.parent / "resume" / "resume.md"
OUTPUT_DIR = Path(__file__).parent.parent / "cover-letters" / "generated"


def load_file_or_text(value: str) -> str:
    p = Path(value)
    if p.exists():
        return p.read_text()
    return value


def main():
    parser = argparse.ArgumentParser(description="Generate a tailored cover letter")
    parser.add_argument("--job", required=True, help="Job description text or path to .txt file")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--role", required=True, help="Role / job title")
    parser.add_argument("--output", help="Output file path (default: auto-generated)")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: ANTHROPIC_API_KEY environment variable not set.")

    resume = RESUME_PATH.read_text()
    job_description = load_file_or_text(args.job)

    client = anthropic.Anthropic(api_key=api_key)

    system = [
        {
            "type": "text",
            "text": (
                "You are an expert career coach and professional cover letter writer.\n"
                "Write compelling, concise cover letters (under 400 words) tailored to the job description.\n"
                "Write in first person, in flowing paragraphs. Be specific — reference the company and role directly.\n"
                "Highlight 2-3 concrete achievements from the resume that map directly to key requirements.\n"
                "End with a confident call to action. Do not use bullet points.\n\n"
                f"Candidate resume:\n\n{resume}"
            ),
            "cache_control": {"type": "ephemeral"},
        }
    ]

    prompt = (
        f"Write a tailored cover letter for the following position:\n\n"
        f"Company: {args.company}\n"
        f"Role: {args.role}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Today's date: {datetime.now().strftime('%B %d, %Y')}\n\n"
        "Write the full cover letter, ready to send."
    )

    print(f"\nGenerating cover letter for {args.role} at {args.company}...\n")
    print("-" * 60)

    full_text = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=2048,
        system=system,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_text += text

    print("\n" + "-" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.output:
        out_path = Path(args.output)
    else:
        slug = args.company.lower().replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = OUTPUT_DIR / f"{slug}_{timestamp}.md"

    header = (
        f"---\n"
        f"company: {args.company}\n"
        f"role: {args.role}\n"
        f"generated: {datetime.now().isoformat()}\n"
        f"---\n\n"
    )
    out_path.write_text(header + full_text)
    print(f"\nSaved to: {out_path}")


if __name__ == "__main__":
    main()
