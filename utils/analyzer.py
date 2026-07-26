"""
analyzer.py
Analyzes the parsed resume data to:
 - Detect missing / incomplete sections
 - Detect signs of a "weak" resume
 - Generate actionable improvement suggestions
 - Compute a base ATS-style score (before job-description matching)
"""

import re
from utils.skills_db import ACTION_VERBS

REQUIRED_SECTIONS = ["education", "skills", "projects", "experience", "certifications"]

SECTION_DISPLAY_NAMES = {
    "education": "Education",
    "skills": "Skills",
    "projects": "Projects",
    "experience": "Experience",
    "certifications": "Certifications",
    "languages": "Languages",
    "summary": "Summary / Objective",
    "achievements": "Achievements",
}

MIN_WORD_COUNT = 150   # below this the resume is considered too short
IDEAL_MAX_WORD_COUNT = 1000  # above this it may be too long / unfocused


def detect_missing_sections(parsed_data):
    """Return a list of required sections that were not found in the resume."""
    sections_found = parsed_data.get("sections", {})
    missing = []
    for section in REQUIRED_SECTIONS:
        content = sections_found.get(section, "").strip()
        if not content or len(content.split()) < 3:
            missing.append(SECTION_DISPLAY_NAMES[section])
    return missing


def detect_missing_contact_info(parsed_data):
    """Return a list of missing contact/basic fields."""
    missing = []
    if not parsed_data.get("email"):
        missing.append("Email Address")
    if not parsed_data.get("phone"):
        missing.append("Phone Number")
    if parsed_data.get("name") in (None, "Not Found"):
        missing.append("Full Name")
    if not parsed_data.get("linkedin"):
        missing.append("LinkedIn Profile (recommended)")
    return missing


def detect_weak_points(parsed_data):
    """
    Analyze the resume for signs of weakness:
     - Too short / too long
     - No quantifiable achievements (numbers, %, metrics)
     - No strong action verbs
     - Very few skills listed
     - No certifications or languages listed
    Returns a list of human-readable weakness descriptions.
    """
    weak_points = []
    text = parsed_data.get("raw_text", "")
    word_count = parsed_data.get("word_count", 0)

    if word_count < MIN_WORD_COUNT:
        weak_points.append(
            f"Resume content is quite short ({word_count} words). "
            "Consider adding more detail to your projects and experience."
        )
    elif word_count > IDEAL_MAX_WORD_COUNT:
        weak_points.append(
            f"Resume content is very long ({word_count} words). "
            "Consider trimming it down to keep it concise (ideally 1-2 pages)."
        )

    # Quantifiable achievements: look for numbers, %, or metric-style phrases
    has_numbers = bool(re.search(r"\d+%|\d+\+|\b\d{2,}\b", text))
    if not has_numbers:
        weak_points.append(
            "No quantifiable achievements detected (e.g. percentages, numbers, "
            "metrics). Adding measurable results (like 'improved performance by 20%') "
            "makes your resume much stronger."
        )

    # Action verbs
    text_lower = text.lower()
    action_verb_count = sum(1 for verb in ACTION_VERBS if verb in text_lower)
    if action_verb_count < 3:
        weak_points.append(
            "Few strong action verbs detected (e.g. 'developed', 'implemented', "
            "'optimized'). Use more action-oriented language to describe your "
            "achievements."
        )

    # Skills count
    skills = parsed_data.get("skills", [])
    if len(skills) < 5:
        weak_points.append(
            f"Only {len(skills)} recognizable skill(s) found. Consider listing "
            "more relevant technical and soft skills."
        )

    # Certifications / Languages
    sections = parsed_data.get("sections", {})
    if not sections.get("certifications", "").strip():
        weak_points.append(
            "No certifications section found. Adding relevant certifications "
            "can strengthen your resume."
        )
    if not parsed_data.get("languages"):
        weak_points.append(
            "No languages detected. Consider listing spoken/written languages "
            "if relevant."
        )

    return weak_points


def generate_suggestions(parsed_data, missing_sections, missing_contact, weak_points):
    """
    Combine all findings into a final, de-duplicated list of actionable
    suggestions for the user.
    """
    suggestions = []

    for section in missing_sections:
        suggestions.append(f"Add a clear '{section}' section to your resume.")

    for field in missing_contact:
        suggestions.append(f"Add your {field.lower()} so recruiters can reach you.")

    suggestions.extend(weak_points)

    if not parsed_data.get("skills"):
        suggestions.append(
            "List your technical and soft skills explicitly under a dedicated "
            "'Skills' section using keywords relevant to your target job."
        )

    if parsed_data.get("word_count", 0) > 0 and not missing_sections:
        suggestions.append(
            "Great job including all key sections! Focus on refining the "
            "wording and adding measurable achievements to stand out further."
        )

    # De-duplicate while preserving order
    seen = set()
    final_suggestions = []
    for s in suggestions:
        if s not in seen:
            seen.add(s)
            final_suggestions.append(s)

    return final_suggestions


def compute_base_ats_score(parsed_data, missing_sections, missing_contact, weak_points):
    """
    Compute an ATS-style compatibility score (0-100) based on:
     - Section completeness   (40 points)
     - Contact info completeness (15 points)
     - Skill richness         (20 points)
     - Formatting / content quality (25 points)

    Returns (score, breakdown_dict) where breakdown_dict explains the score.
    """
    breakdown = {}

    # 1. Section completeness (40 points)
    total_sections = len(REQUIRED_SECTIONS)
    sections_present = total_sections - len(missing_sections)
    section_score = round((sections_present / total_sections) * 40, 1)
    breakdown["Section Completeness"] = {
        "score": section_score,
        "max": 40,
        "detail": f"{sections_present}/{total_sections} required sections present.",
    }

    # 2. Contact info completeness (15 points)
    total_contact_fields = 3  # email, phone, name (linkedin is a bonus, not penalized)
    core_missing = [
        m for m in missing_contact
        if "recommended" not in m.lower()
    ]
    contact_present = total_contact_fields - len(core_missing)
    contact_score = round(max(contact_present, 0) / total_contact_fields * 15, 1)
    breakdown["Contact Information"] = {
        "score": contact_score,
        "max": 15,
        "detail": f"{contact_present}/{total_contact_fields} core contact fields present.",
    }

    # 3. Skill richness (20 points)
    skill_count = len(parsed_data.get("skills", []))
    skill_score = round(min(skill_count / 12, 1.0) * 20, 1)
    breakdown["Skill Richness"] = {
        "score": skill_score,
        "max": 20,
        "detail": f"{skill_count} recognizable skills found (target: 12+).",
    }

    # 4. Formatting / content quality (25 points)
    quality_deductions = len(weak_points)
    quality_score = round(max(25 - quality_deductions * 5, 0), 1)
    breakdown["Formatting & Content Quality"] = {
        "score": quality_score,
        "max": 25,
        "detail": f"{quality_deductions} quality issue(s) detected "
                  f"(length, action verbs, quantifiable results, etc.).",
    }

    total_score = round(
        section_score + contact_score + skill_score + quality_score, 1
    )
    total_score = min(total_score, 100.0)

    return total_score, breakdown


def analyze_resume(parsed_data):
    """
    Full analysis pipeline (without job description matching).
    Returns a dictionary with all analysis results.
    """
    missing_sections = detect_missing_sections(parsed_data)
    missing_contact = detect_missing_contact_info(parsed_data)
    weak_points = detect_weak_points(parsed_data)
    suggestions = generate_suggestions(
        parsed_data, missing_sections, missing_contact, weak_points
    )
    base_score, breakdown = compute_base_ats_score(
        parsed_data, missing_sections, missing_contact, weak_points
    )

    return {
        "missing_sections": missing_sections,
        "missing_contact": missing_contact,
        "weak_points": weak_points,
        "suggestions": suggestions,
        "base_ats_score": base_score,
        "score_breakdown": breakdown,
    }
