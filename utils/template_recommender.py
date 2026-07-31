"""
template_recommender.py
Recommends the most suitable resume template by analyzing the resume's
detected skills together with the pasted Job Description text.

This is a lightweight, rule-based recommender (no new dependencies):
 - Counts how many "tech" vs "executive/management" signal words appear
   in the job description (and, as a fallback, in the resume skills).
 - Picks whichever template best matches that signal.
 - Falls back to the general-purpose "ATS Standard" template when the
   signal is weak or no job description was provided.
"""

# Static template metadata shown as cards in the UI.
RESUME_TEMPLATES = {
    "modern_tech": {
        "id": "modern_tech",
        "name": "Modern Tech Template",
        "best_for": ["Software Engineer", "Data Scientist", "Backend Developer"],
        "ats_friendly": True,
    },
    "ats_standard": {
        "id": "ats_standard",
        "name": "ATS Standard Template",
        "best_for": ["General Corporate Jobs"],
        "ats_friendly": True,
    },
    "executive": {
        "id": "executive",
        "name": "Executive Template",
        "best_for": ["Management Roles"],
        "ats_friendly": True,
    },
}

# Signal words used purely to decide WHICH template to recommend.
TECH_SIGNAL_WORDS = [
    "python", "java", "javascript", "typescript", "c++", "software engineer",
    "software developer", "backend", "front end", "frontend", "full stack",
    "fullstack", "data scientist", "data science", "machine learning",
    "deep learning", "sql", "react", "node.js", "django", "flask",
    "api", "rest api", "cloud", "aws", "azure", "docker", "kubernetes",
    "devops", "git", "algorithms", "data structures", "sde", "programmer",
    "developer", "engineer", "coding", "microservices", "database",
]

EXECUTIVE_SIGNAL_WORDS = [
    "manager", "management", "director", "head of", "vp", "vice president",
    "chief", "executive", "president", "principal", "lead", "leadership",
    "strategy", "stakeholder", "p&l", "operations", "senior manager",
    "general manager", "team lead", "business unit", "portfolio",
]


def _count_signal_hits(text, signal_words):
    """Count how many signal words/phrases appear in the given text."""
    text_lower = (text or "").lower()
    return sum(1 for word in signal_words if word in text_lower)


def recommend_template(resume_skills=None, job_description=""):
    """
    Analyze resume skills + job description and recommend the best
    matching resume template.

    Returns a dict:
        {
            "recommended_id": "modern_tech" | "ats_standard" | "executive",
            "reasons": [list of short "why this template" bullet strings]
        }
    """
    resume_skills = resume_skills or []
    skills_text = " ".join(resume_skills).lower()

    combined_text = f"{job_description or ''} {skills_text}"

    tech_hits = _count_signal_hits(combined_text, TECH_SIGNAL_WORDS)
    exec_hits = _count_signal_hits(combined_text, EXECUTIVE_SIGNAL_WORDS)

    if tech_hits == 0 and exec_hits == 0:
        recommended_id = "ats_standard"
    elif tech_hits >= exec_hits:
        recommended_id = "modern_tech"
    else:
        recommended_id = "executive"

    reasons_by_template = {
        "modern_tech": [
            "ATS friendly and easy to scan",
            "Projects placed before Education",
            "Best for Software Engineering / Data roles",
            f"Matched {tech_hits} technical keyword(s) in the job description",
        ],
        "executive": [
            "ATS friendly with a leadership-first layout",
            "Highlights impact, scope and team size upfront",
            "Best for Management / Leadership roles",
            f"Matched {exec_hits} leadership keyword(s) in the job description",
        ],
        "ats_standard": [
            "ATS friendly and easy to scan",
            "Balanced, general-purpose section order",
            "Best for General Corporate roles",
            "No strong tech or leadership signal detected, "
            "so a safe general-purpose layout is recommended",
        ],
    }

    return {
        "recommended_id": recommended_id,
        "reasons": reasons_by_template[recommended_id],
    }