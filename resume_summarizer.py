"""
AI-Powered Resume Summarizer
=============================
Extracts text from a PDF resume and uses the Anthropic Claude API
to generate a structured, professional summary.

Skills demonstrated: Python, NLP, Prompt Engineering, PDF parsing,
                     Pandas (for structured output), API integration

Requirements:
    pip install anthropic pdfplumber pandas tabulate

Usage:
    python resume_summarizer.py --resume path/to/resume.pdf
    python resume_summarizer.py --resume path/to/resume.pdf --job-title "Data Scientist"
    python resume_summarizer.py --resume path/to/resume.pdf --export summary.csv
"""

import os
import sys
import json
import argparse
import textwrap
from pathlib import Path

# ── Third-party imports ──────────────────────────────────────────────────────
try:
    import pdfplumber
except ImportError:
    sys.exit("Missing dependency: run  pip install pdfplumber")

try:
    import anthropic
except ImportError:
    sys.exit("Missing dependency: run  pip install anthropic")

try:
    import pandas as pd
except ImportError:
    sys.exit("Missing dependency: run  pip install pandas tabulate")


# ── 1. PDF TEXT EXTRACTION ───────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file using pdfplumber."""
    path = Path(pdf_path)
    if not path.exists():
        sys.exit(f"File not found: {pdf_path}")
    if path.suffix.lower() != ".pdf":
        sys.exit("Only PDF files are supported.")

    text_chunks = []
    with pdfplumber.open(path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(f"[Page {page_num}]\n{page_text}")

    full_text = "\n\n".join(text_chunks)
    if not full_text.strip():
        sys.exit("Could not extract any text from the PDF. It may be scanned/image-only.")

    print(f"  Extracted {len(full_text):,} characters from {path.name}")
    return full_text


# ── 2. PROMPT ENGINEERING ────────────────────────────────────────────────────

def build_prompt(resume_text: str, target_job_title: str = "") -> str:
    """
    Craft a structured prompt that instructs Claude to extract and summarize
    key resume sections and return strictly valid JSON.
    """
    job_context = (
        f'The candidate is targeting the role: "{target_job_title}". '
        "Tailor relevance scores and highlights accordingly."
        if target_job_title
        else "No specific target role provided; give a general summary."
    )

    return f"""You are an expert technical recruiter and career coach.
Analyze the resume below and return ONLY a valid JSON object — no markdown, no explanation.

{job_context}

Resume text:
\"\"\"
{resume_text}
\"\"\"

Return this exact JSON structure (all fields required):
{{
  "candidate_name": "string",
  "contact": {{
    "email": "string or null",
    "phone": "string or null",
    "location": "string or null",
    "linkedin": "string or null"
  }},
  "education": [
    {{
      "degree": "string",
      "institution": "string",
      "year": "string or null",
      "gpa": "string or null"
    }}
  ],
  "total_experience_years": "string (e.g. '< 1 year' or '3 years')",
  "top_skills": ["skill1", "skill2", "...up to 10"],
  "skill_gaps": ["gap1", "gap2", "...up to 5 relative to target role"],
  "work_experience": [
    {{
      "title": "string",
      "company": "string",
      "duration": "string",
      "key_contributions": ["point1", "point2"]
    }}
  ],
  "projects": [
    {{
      "name": "string",
      "technologies": ["tech1", "tech2"],
      "impact": "one sentence description"
    }}
  ],
  "certifications": ["cert1", "cert2"],
  "languages": ["lang1", "lang2"],
  "tools": ["tool1", "tool2"],
  "strengths": ["strength1", "strength2", "strength3"],
  "improvement_areas": ["area1", "area2", "area3"],
  "overall_score": <integer 0-100>,
  "one_line_pitch": "A compelling one-sentence recruiter pitch for this candidate"
}}"""


# ── 3. CLAUDE API CALL ───────────────────────────────────────────────────────

def summarize_with_claude(resume_text: str, target_job_title: str = "") -> dict:
    """Send resume text to Claude and parse the structured JSON response."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit(
            "ANTHROPIC_API_KEY environment variable not set.\n"
            "Set it with:  export ANTHROPIC_API_KEY=your_key_here"
        )

    client = anthropic.Anthropic(api_key=api_key)
    prompt = build_prompt(resume_text, target_job_title)

    print("  Sending to Claude API...")
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```", 2)[-1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"\nWarning: Could not parse JSON response. Raw output:\n{raw}")
        sys.exit(f"JSON parse error: {e}")


# ── 4. DISPLAY RESULTS ───────────────────────────────────────────────────────

def print_summary(data: dict) -> None:
    """Pretty-print the structured summary to the terminal."""
    sep = "─" * 60

    print(f"\n{'═' * 60}")
    print(f"  RESUME SUMMARY")
    print(f"{'═' * 60}")

    # Header
    print(f"\n  {data.get('candidate_name', 'Unknown').upper()}")
    c = data.get("contact", {})
    for field in ["email", "phone", "location", "linkedin"]:
        val = c.get(field)
        if val:
            print(f"  {field.capitalize():10} {val}")

    print(f"\n  One-line pitch:")
    pitch = data.get("one_line_pitch", "")
    print(textwrap.fill(pitch, width=58, initial_indent="  ", subsequent_indent="  "))

    # Score
    score = data.get("overall_score", "N/A")
    bar = "█" * int(score / 5) + "░" * (20 - int(score / 5)) if isinstance(score, int) else ""
    print(f"\n  Overall score  {score}/100  {bar}")

    # Education
    print(f"\n{sep}\n  EDUCATION\n{sep}")
    for edu in data.get("education", []):
        gpa = f"  |  GPA: {edu['gpa']}" if edu.get("gpa") else ""
        print(f"  {edu.get('degree', '')}  —  {edu.get('institution', '')}  ({edu.get('year', '')}){gpa}")

    # Skills
    print(f"\n{sep}\n  TOP SKILLS\n{sep}")
    skills = data.get("top_skills", [])
    print(textwrap.fill(", ".join(skills), width=58, initial_indent="  ", subsequent_indent="  "))

    if data.get("skill_gaps"):
        print(f"\n  Gaps vs target role:")
        print(textwrap.fill(", ".join(data["skill_gaps"]), width=58, initial_indent="  ", subsequent_indent="  "))

    # Experience
    print(f"\n{sep}\n  EXPERIENCE\n{sep}")
    for exp in data.get("work_experience", []):
        print(f"  {exp.get('title', '')}  @  {exp.get('company', '')}  ({exp.get('duration', '')})")
        for pt in exp.get("key_contributions", []):
            print(textwrap.fill(f"• {pt}", width=56, initial_indent="    ", subsequent_indent="      "))

    # Projects
    print(f"\n{sep}\n  PROJECTS\n{sep}")
    for proj in data.get("projects", []):
        techs = ", ".join(proj.get("technologies", []))
        print(f"  {proj.get('name', '')}  [{techs}]")
        impact = proj.get("impact", "")
        if impact:
            print(textwrap.fill(impact, width=56, initial_indent="    ", subsequent_indent="    "))

    # Strengths & improvements
    print(f"\n{sep}\n  STRENGTHS\n{sep}")
    for s in data.get("strengths", []):
        print(f"  ✓  {s}")

    print(f"\n{sep}\n  AREAS TO IMPROVE\n{sep}")
    for a in data.get("improvement_areas", []):
        print(f"  →  {a}")

    # Misc
    certs = data.get("certifications", [])
    if certs:
        print(f"\n{sep}\n  CERTIFICATIONS\n{sep}")
        for cert in certs:
            print(f"  •  {cert}")

    tools = data.get("tools", [])
    if tools:
        print(f"\n{sep}\n  TOOLS\n{sep}")
        print(textwrap.fill(", ".join(tools), width=58, initial_indent="  ", subsequent_indent="  "))

    print(f"\n{'═' * 60}\n")


# ── 5. EXPORT TO CSV ─────────────────────────────────────────────────────────

def export_to_csv(data: dict, output_path: str) -> None:
    """
    Flatten the structured JSON summary into a Pandas DataFrame and export to CSV.
    Demonstrates Pandas usage for structured data handling.
    """
    rows = []

    def add(section, key, value):
        rows.append({"section": section, "field": key, "value": str(value)})

    add("Header", "name", data.get("candidate_name", ""))
    add("Header", "overall_score", data.get("overall_score", ""))
    add("Header", "experience_years", data.get("total_experience_years", ""))
    add("Header", "one_line_pitch", data.get("one_line_pitch", ""))

    c = data.get("contact", {})
    for k, v in c.items():
        add("Contact", k, v or "")

    for i, edu in enumerate(data.get("education", []), 1):
        for k, v in edu.items():
            add(f"Education_{i}", k, v or "")

    add("Skills", "top_skills", " | ".join(data.get("top_skills", [])))
    add("Skills", "skill_gaps", " | ".join(data.get("skill_gaps", [])))
    add("Skills", "tools", " | ".join(data.get("tools", [])))
    add("Skills", "languages", " | ".join(data.get("languages", [])))

    for i, proj in enumerate(data.get("projects", []), 1):
        add(f"Project_{i}", "name", proj.get("name", ""))
        add(f"Project_{i}", "technologies", " | ".join(proj.get("technologies", [])))
        add(f"Project_{i}", "impact", proj.get("impact", ""))

    add("Assessment", "strengths", " | ".join(data.get("strengths", [])))
    add("Assessment", "improvements", " | ".join(data.get("improvement_areas", [])))
    add("Assessment", "certifications", " | ".join(data.get("certifications", [])))

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"  Exported structured summary → {output_path}")
    print(f"  DataFrame shape: {df.shape[0]} rows × {df.shape[1]} columns\n")


# ── 6. MAIN ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI-powered resume summarizer using Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python resume_summarizer.py --resume resume.pdf
          python resume_summarizer.py --resume resume.pdf --job-title "Data Scientist"
          python resume_summarizer.py --resume resume.pdf --export summary.csv
        """),
    )
    parser.add_argument("--resume", required=True, help="Path to resume PDF file")
    parser.add_argument("--job-title", default="", help="Target job title (optional)")
    parser.add_argument("--export", default="", help="Export structured summary to CSV (optional)")
    args = parser.parse_args()

    print("\n── AI Resume Summarizer ─────────────────────────────")
    print(f"\nStep 1/3  Extracting text from PDF...")
    resume_text = extract_text_from_pdf(args.resume)

    print(f"\nStep 2/3  Analyzing with Claude AI...")
    summary_data = summarize_with_claude(resume_text, args.job_title)

    print(f"\nStep 3/3  Generating summary...\n")
    print_summary(summary_data)

    if args.export:
        print("Exporting to CSV...")
        export_to_csv(summary_data, args.export)

    # Always save raw JSON alongside
    json_out = Path(args.resume).stem + "_summary.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    print(f"  Raw JSON saved → {json_out}")


if __name__ == "__main__":
    main()
