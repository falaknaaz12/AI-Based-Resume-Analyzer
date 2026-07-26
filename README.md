# ResumeIQ — AI-Based Resume Analyzer

An AI & NLP powered web application that analyzes resumes (PDF/DOCX), detects
missing or weak sections, compares the resume against a pasted job
description, and produces a transparent 0–100 ATS Compatibility Score with
actionable suggestions.

Built as an academic project for **BIT Durg — CSE (Data Science)**.

---

## Features

- **Resume Upload** — Supports PDF and DOCX formats via drag-and-drop or file browser.
- **Resume Parsing** — Extracts Name, Email, Phone, LinkedIn/GitHub links, Education, Skills, Projects, Experience, Certifications, and Languages.
- **Resume Analysis** — Detects missing sections, weak/thin content, missing quantifiable achievements, and generates actionable suggestions.
- **Job Description Matching** — Paste any job description to see matching skills, missing skills, keyword-level comparison, and a job match percentage.
- **ATS Score** — A 0–100 score built from section completeness, contact info, skill richness, formatting/content quality, and (optionally) job description match — with a full explanation of how the score was calculated.
- **Dashboard** — A single results page showing the resume summary, skills found, missing skills, missing sections, suggestions, ATS score breakdown, and job match percentage.
- **Modern Responsive UI** — Home, Upload, Analysis Result, and About pages built with Bootstrap 5 and a custom design system.
- **100% Free** — Uses only free, open-source Python libraries. No paid APIs are used anywhere.

---

## Technology Stack

| Layer            | Technology                                   |
|-------------------|-----------------------------------------------|
| Backend           | Python 3, Flask                              |
| Frontend          | HTML5, CSS3, JavaScript, Bootstrap 5          |
| PDF Parsing       | PyMuPDF (`fitz`)                              |
| DOCX Parsing      | `python-docx`                                 |
| NLP / Matching    | Regex-based entity extraction + scikit-learn TF-IDF & cosine similarity |

---

## Project Structure

```
resume_analyzer/
│
├── app.py                     # Main Flask application (routes & app logic)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── utils/                      # Python helper / logic modules
│   ├── __init__.py
│   ├── parser.py                # PDF/DOCX text extraction
│   ├── extractor.py              # Name/email/phone/section/skill extraction
│   ├── analyzer.py               # Missing sections, weak points, suggestions, base ATS score
│   ├── matcher.py                # Job description matching & final ATS score
│   └── skills_db.py              # Static skills & section-header keyword database
│
├── templates/                   # Jinja2 HTML templates
│   ├── base.html                  # Shared layout (navbar, footer)
│   ├── index.html                 # Home page
│   ├── upload.html                # Upload page
│   ├── result.html                # Analysis result dashboard
│   └── about.html                 # About page
│
├── static/
│   ├── css/
│   │   └── style.css              # Custom design system (all styling)
│   └── js/
│       ├── main.js                # Global site behaviors
│       └── upload.js              # Drag-and-drop + upload UX
│
└── uploads/                     # Temporary storage for uploaded resumes
    └── .gitkeep                    # (files are deleted immediately after analysis)
```

---

## Setup Instructions

### 1. Prerequisites

- Python 3.9 or higher installed
- `pip` package manager

### 2. Clone / Extract the Project

Place the `resume_analyzer` folder anywhere on your computer, then open a
terminal inside it.

### 3. (Recommended) Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

> If you don't use a virtual environment and get a "externally managed
> environment" error on Linux, install with:
> `pip install -r requirements.txt --break-system-packages`

### 5. Run the Application

```bash
python app.py
```

You should see output similar to:

```
 * Running on http://127.0.0.1:5000
```

### 6. Open in Browser

Go to **http://127.0.0.1:5000** in your web browser.

---

## How to Use

1. Go to the **Analyze Resume** page from the navigation bar.
2. Upload your resume as a **PDF or DOCX** file (drag-and-drop or click to browse).
3. *(Optional but recommended)* Paste a **Job Description** in the text box to get a tailored score and skill-gap analysis.
4. Click **Analyze My Resume**.
5. View your full dashboard: ATS score with breakdown, resume summary, skills found, missing skills, missing sections, keyword comparison (if a JD was pasted), and improvement suggestions.

---

## How the ATS Score Is Calculated

**Without a Job Description** (resume-only quality, out of 100):
- Section Completeness — 40 points
- Contact Information — 15 points
- Skill Richness — 20 points
- Formatting & Content Quality — 25 points

**With a Job Description** (final score = 60% resume quality + 40% job match):
- The four categories above are rescaled to fit within 60 points.
- **Job Description Match** — 40 points, based on skill overlap (70% weight) and overall TF-IDF text similarity (30% weight) between the resume and the job description.

The full breakdown, including a plain-English explanation, is shown on the results dashboard.

---

## Notes on Privacy

Uploaded resumes are processed **entirely in memory/on local disk** during
analysis and are **deleted immediately** after the analysis completes. No
resume content or personal data is sent to any third-party or paid API — all
processing (parsing, extraction, matching, and scoring) happens locally using
free, open-source libraries.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'fitz'` | Run `pip install -r requirements.txt` again — `fitz` is provided by the `PyMuPDF` package. |
| "Could not extract enough text from this file" | Your PDF may be a scanned image rather than text-based. Use a text-based resume (exported from Word/Google Docs). |
| Port 5000 already in use | Edit the last line of `app.py` and change `port=5000` to another port, e.g. `port=5050`. |
| Styles look unstyled / broken | Make sure you have an active internet connection the first time you load the page, since Bootstrap and fonts are loaded from a CDN. |

---

## Author

**Falak Naaz**
BIT Durg — CSE (Data Science)

*Academic project: AI-Based Resume Analyzer*
