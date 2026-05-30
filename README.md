# AI Resume Summarizer

An AI-powered resume analysis tool built with Python and the Anthropic Claude API. Available in two versions — a browser-based web app and a Python CLI tool — both performing the same intelligent analysis from two different interfaces.

🌐 **Live Demo:** [yeshwanthreddy1306.github.io/AI-Resume-Summarizer](https://yeshwanthreddy1306.github.io/AI-Resume-Summarizer/)

---

## What it does

- Extracts and parses text from PDF resumes
- Analyzes the resume against a target job title and job description
- Returns a structured summary including skills, projects, education, strengths, and improvement areas
- Provides an overall candidate score (0–100) and a one-line recruiter pitch
- Identifies skill gaps relative to the target role
- Exports structured data to CSV (Python version)

---

## Project structure

```
AI-Resume-Summarizer/
├── index.html              # Web app — open in any browser, no install needed
├── resume_summarizer.py    # Python CLI tool — run from terminal
└── README.md
```

---

## Version 1 — Web App (index.html)

A fully self-contained single-file web application. No server, no backend, no installation required — just open the file in a browser.

### Features
- Drag-and-drop PDF upload with in-browser parsing (via pdf.js)
- Paste resume text directly as an alternative
- Optional job title, company, and job description fields for tailored analysis
- Structured results rendered in a clean UI: score, skills, gaps, projects, strengths, improvements
- Works entirely in the browser — your resume never leaves your device except for the Claude API call

### How to use

1. Open [the live site](https://yeshwanthreddy1306.github.io/AI-Resume-Summarizer/) or download `index.html` and open it in Chrome/Edge/Firefox
2. Enter your [Anthropic API key](https://console.anthropic.com) (free tier available)
3. Upload a PDF resume or paste resume text
4. Optionally add a target job title and job description
5. Click **Analyze Resume**

### Technologies used
- HTML5, CSS3, Vanilla JavaScript
- [pdf.js](https://mozilla.github.io/pdf.js/) for in-browser PDF parsing
- Anthropic Claude API (`claude-opus-4-5`)
- Prompt engineering for structured JSON extraction

---

## Version 2 — Python CLI (resume_summarizer.py)

A command-line tool that processes PDF resumes locally and outputs a detailed analysis to the terminal, with optional CSV export via Pandas.

### Features
- PDF text extraction using `pdfplumber`
- Structured prompt engineering for consistent JSON output from Claude
- Rich terminal output with scores, sections, and visual progress bar
- CSV export using `pandas` for further data analysis
- Auto-saves raw JSON summary alongside the input file

### Installation

```bash
pip install anthropic pdfplumber pandas tabulate
```

Set your Anthropic API key:

```bash
# Mac/Linux
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Usage

```bash
# Basic analysis
python resume_summarizer.py --resume your_resume.pdf

# Targeted to a specific role
python resume_summarizer.py --resume your_resume.pdf --job-title "Data Scientist"

# With job description for gap analysis
python resume_summarizer.py --resume your_resume.pdf --job-title "ML Engineer" --export summary.csv
```

### Output files generated
| File | Description |
|------|-------------|
| Terminal output | Formatted summary with scores and recommendations |
| `*_summary.json` | Raw structured JSON saved automatically |
| `summary.csv` | Flat Pandas DataFrame export (when `--export` is used) |

### Technologies used
- Python 3.8+
- `pdfplumber` — PDF text extraction
- `anthropic` — Claude API client
- `pandas` — structured data export
- `argparse` — CLI interface
- Prompt engineering for deterministic JSON responses

---

## Skills demonstrated

| Skill | Where |
|-------|-------|
| Python programming | `resume_summarizer.py` |
| Prompt engineering | Both versions — structured JSON extraction from LLM |
| API integration | Anthropic Claude API in both versions |
| PDF parsing | `pdfplumber` (Python), `pdf.js` (browser) |
| Data handling with Pandas | Python CSV export |
| Frontend development (HTML/CSS/JS) | `index.html` |
| CLI tool design | `argparse` in Python script |
| GitHub Pages deployment | Live web app |

---

## Getting an API key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up for a free account
3. Navigate to **API Keys** → **Create Key**
4. Copy the key starting with `sk-ant-...`

The free tier is sufficient for personal use of this tool.

---

## Author

**Yeshwanth Reddy Chintala**
B.Tech Computer Science, NIAT (Expected 2029)
[LinkedIn](https://linkedin.com/in/yeshwanth-reddy-chintala-b3528b366) · reddyyeshwanth691@gmail.com
