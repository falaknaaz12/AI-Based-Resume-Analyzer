"""
extractor.py
Extracts structured information from raw resume text:
 - Name, Email, Phone
 - Section text blocks (education, skills, projects, experience,
   certifications, languages)
 - Skills list
 - Languages list
"""

import re
from utils.skills_db import ALL_SKILLS, SECTION_HEADERS, COMMON_LANGUAGES

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[\s\-.]?)?(?:\(?\d{2,5}\)?[\s\-.]?){2,4}\d{2,4}"
)

LINKEDIN_REGEX = re.compile(r"(linkedin\.com/in/[A-Za-z0-9\-_/]+)", re.IGNORECASE)
GITHUB_REGEX = re.compile(r"(github\.com/[A-Za-z0-9\-_/]+)", re.IGNORECASE)


def extract_email(text):
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None


def extract_phone(text):
    """
    Extract a phone number. We scan candidate matches and pick the first
    one that has at least 10 digits (to avoid matching random numbers
    like years or short codes).
    """
    for match in PHONE_REGEX.finditer(text):
        candidate = match.group(0)
        digits = re.sub(r"\D", "", candidate)
        if 10 <= len(digits) <= 13:
            return candidate.strip()
    return None


def extract_linkedin(text):
    match = LINKEDIN_REGEX.search(text)
    return match.group(0) if match else None


def extract_github(text):
    match = GITHUB_REGEX.search(text)
    return match.group(0) if match else None


def extract_name(text):
    """
    Heuristic name extraction: the resume's name is almost always on one
    of the first few non-empty lines, is short (2-4 words), does not
    contain '@' or digits, and is not a known section header.
    """
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    known_headers = set()
    for headers in SECTION_HEADERS.values():
        known_headers.update(headers)

    for line in lines[:10]:
        lower = line.lower()
        if "@" in line or any(ch.isdigit() for ch in line):
            continue
        if lower in known_headers:
            continue
        word_count = len(line.split())
        if 1 <= word_count <= 4 and line.replace(" ", "").isalpha() is False:
            # allow names with periods/commas but reject lines with too
            # much punctuation (likely addresses/titles)
            if len(re.findall(r"[.,|/]", line)) > 1:
                continue
        if 1 <= word_count <= 4:
            return line.title() if line.isupper() else line
    return "Not Found"


def split_sections(text):
    """
    Split resume text into sections based on known section header
    keywords. Returns a dict: {section_name: section_text}
    """
    lines = text.split("\n")
    lower_lines = [ln.strip().lower() for ln in lines]

    # Build a flat map of header-keyword -> canonical section name
    header_to_section = {}
    for section, headers in SECTION_HEADERS.items():
        for h in headers:
            header_to_section[h] = section

    # Find line indices where a section header appears (line is short and
    # matches a known header closely)
    matches = []  # list of (line_index, section_name)
    for idx, line in enumerate(lower_lines):
        cleaned = re.sub(r"[^a-z\s]", "", line).strip()
        if not cleaned:
            continue
        if len(cleaned.split()) > 5:
            continue  # header lines are short
        for header, section in header_to_section.items():
            if cleaned == header or cleaned.startswith(header):
                matches.append((idx, section))
                break

    sections = {}
    for i, (idx, section) in enumerate(matches):
        start = idx + 1
        end = matches[i + 1][0] if i + 1 < len(matches) else len(lines)
        section_text = "\n".join(lines[start:end]).strip()
        # Merge if the same section appears more than once
        if section in sections:
            sections[section] += "\n" + section_text
        else:
            sections[section] = section_text

    return sections


def extract_skills(text):
    """Find which known skills (from skills_db) appear in the resume text."""
    text_lower = " " + re.sub(r"[^a-z0-9+#.\s]", " ", text.lower()) + " "
    found = []
    for skill in ALL_SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    # Deduplicate while preserving a clean display case
    return sorted(set(found))


def extract_languages(text):
    text_lower = text.lower()
    found = []
    for lang in COMMON_LANGUAGES:
        pattern = r"\b" + re.escape(lang) + r"\b"
        if re.search(pattern, text_lower):
            found.append(lang.title())
    return sorted(set(found))


def parse_resume(text):
    """
    Master function: runs all extraction routines and returns a single
    structured dictionary describing the resume.
    """
    sections = split_sections(text)

    data = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "github": extract_github(text),
        "skills": extract_skills(text),
        "languages": extract_languages(text),
        "sections": sections,
        "raw_text": text,
        "word_count": len(text.split()),
    }
    return data
