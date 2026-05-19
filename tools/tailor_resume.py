#!/usr/bin/env python3
"""Suggest resume tailoring based on a job description using Claude API."""

import argparse
import os
import sys
from pathlib import Path

import anthropic

RESUME_PATH = Path(__file__).parent.parent / "resume" / "resume.md"


def load_file_or_text(value: str) -> str:
    p = Path(value)
    if p.exists():
        return p.read_text()
    return value


def main():
    parser = argparse.ArgumentParser(description="Get resume tailoring suggestions for a job")
    parser.add_argument("--job", required=True, help="Job description text or path to .txt file")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--role", required=True, help="Role / job title")
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
                "You are an expert ATS optimization specialist and resume coach.\n"
                "Analyze resumes against job descriptions and give specific, actionable tailoring suggestions.\n"
                "Be direct and precise. Focus on changes that will meaningfully improve ATS match rate.\n\n"
                f"Candidate resume:\n\n{resume}"
            ),
            "cache_control": {"type": "ephemeral"},
        }
    ]

    prompt = (
        f"Analyze this resume for the following position and provide tailoring suggestions:\n\n"
        f"Company: {args.company}\n"
        f"Role: {args.role}\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Provide your analysis in exactly this format:\n\n"
        "## Match Score\n"
        "[X/10 with 1-sentence rationale]\n\n"
        "## Key Gaps\n"
        "[Bulleted list of JD requirements not addressed in the resume]\n\n"
        "## Keywords to Add\n"
        "[Comma-separated list of high-value keywords from the JD missing from the resume]\n\n"
        "## Bullet Point Rewrites\n"
        "[3-5 specific rewrites that better match JD language. Format: ORIGINAL → REWRITE]\n\n"
        "## Summary Suggestion\n"
        "[A revised 2-3 sentence summary tailored to this specific role]\n\n"
        "## ATS Tips\n"
        "[2-3 formatting or keyword tips for this specific application]"
    )

    print(f"\nAnalyzing resume for {args.role} at {args.company}...\n")
    print("=" * 60)

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=4096,
        system=system,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
