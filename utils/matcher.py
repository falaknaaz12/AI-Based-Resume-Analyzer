"""
matcher.py
Compares a resume against a pasted Job Description (JD):
 - Extracts skills/keywords from the JD
 - Finds matching and missing skills
 - Computes an overall text similarity using TF-IDF + cosine similarity
 - Produces a final, JD-aware ATS score
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.extractor import extract_skills

# A generic stopword list (kept local to avoid needing NLTK downloads)
STOPWORDS = set("""
a an the and or but if while with without within to of in on for from by
as is are was were be been being this that these those it its it's you
your we our they their he she his her i me my mine ours yours theirs
will would can could should shall must may might not no nor do does did
have has had having at into over under again further then once here there
all any both each few more most other some such only own same so than too
very s t just don now etc using use used via per e.g eg i.e ie
""".split())


def extract_keywords(text, top_n=40):
    """
    Extract the most relevant keywords from a job description using simple
    frequency analysis (excluding stopwords and short tokens).
    """
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]{1,}", text.lower())
    freq = {}
    for w in words:
        w = w.strip(".,-/")
        if len(w) < 3 or w in STOPWORDS:
            continue
        freq[w] = freq.get(w, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:top_n]]


def compute_skill_match(resume_skills, jd_text):
    """
    Compare resume skills against skills detected in the JD text.
    Returns matching_skills, missing_skills, and match percentage.
    """
    jd_skills = extract_skills(jd_text)

    resume_skills_set = set(resume_skills)
    jd_skills_set = set(jd_skills)

    matching_skills = sorted(resume_skills_set & jd_skills_set)
    missing_skills = sorted(jd_skills_set - resume_skills_set)

    if jd_skills_set:
        match_percentage = round(len(matching_skills) / len(jd_skills_set) * 100, 1)
    else:
        match_percentage = 0.0

    return {
        "jd_skills": sorted(jd_skills_set),
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "skill_match_percentage": match_percentage,
    }


def compute_text_similarity(resume_text, jd_text):
    """
    Compute TF-IDF cosine similarity between the full resume text and the
    job description text, as an overall semantic-ish match indicator.
    """
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(similarity) * 100, 1)
    except ValueError:
        # Happens if texts are empty after stopword removal
        return 0.0


def compute_keyword_comparison(resume_text, jd_text):
    """
    Build a keyword-level comparison table: top JD keywords and whether
    each appears in the resume text.
    """
    jd_keywords = extract_keywords(jd_text, top_n=25)
    resume_text_lower = resume_text.lower()

    comparison = []
    for kw in jd_keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        present = bool(re.search(pattern, resume_text_lower))
        comparison.append({"keyword": kw, "present_in_resume": present})

    return comparison


def match_resume_to_job(resume_data, jd_text):
    """
    Master function: runs full JD comparison pipeline.
    Returns a dictionary with skill match, similarity score, and keyword
    comparison table, plus a combined job_match_percentage.
    """
    resume_skills = resume_data.get("skills", [])
    resume_text = resume_data.get("raw_text", "")

    skill_match = compute_skill_match(resume_skills, jd_text)
    text_similarity = compute_text_similarity(resume_text, jd_text)
    keyword_comparison = compute_keyword_comparison(resume_text, jd_text)

    # Combined job match percentage: weighted average of skill overlap
    # (70%) and overall text similarity (30%)
    job_match_percentage = round(
        skill_match["skill_match_percentage"] * 0.7 + text_similarity * 0.3, 1
    )

    return {
        "jd_skills": skill_match["jd_skills"],
        "matching_skills": skill_match["matching_skills"],
        "missing_skills": skill_match["missing_skills"],
        "skill_match_percentage": skill_match["skill_match_percentage"],
        "text_similarity": text_similarity,
        "keyword_comparison": keyword_comparison,
        "job_match_percentage": job_match_percentage,
    }


def compute_final_ats_score(base_score, base_breakdown, job_match_result=None):
    """
    Combine the base ATS score (resume-only quality) with the job
    description match (if provided) into a final ATS score with a
    full explanation breakdown.
    """
    if job_match_result is None:
        return base_score, base_breakdown, (
            "This score is based purely on resume completeness, formatting, "
            "and skill richness. Paste a job description for a more tailored, "
            "job-specific ATS score."
        )

    # When a JD is provided: final score = 60% base quality + 40% job match
    job_match_pct = job_match_result["job_match_percentage"]
    final_score = round(base_score * 0.6 + job_match_pct * 0.4, 1)
    final_score = min(final_score, 100.0)

    breakdown = dict(base_breakdown)
    breakdown["Job Description Match"] = {
        "score": round(job_match_pct * 0.4, 1),
        "max": 40,
        "detail": f"{job_match_pct}% alignment with the pasted job description "
                  f"({len(job_match_result['matching_skills'])} matching skill(s), "
                  f"{len(job_match_result['missing_skills'])} missing skill(s)).",
    }
    # Rescale the base categories to fit within 60 total when a JD is present
    for key in ["Section Completeness", "Contact Information",
                "Skill Richness", "Formatting & Content Quality"]:
        if key in breakdown:
            original_max = breakdown[key]["max"]
            new_max = round(original_max * 0.6, 1)
            breakdown[key] = {
                "score": round(breakdown[key]["score"] * 0.6, 1),
                "max": new_max,
                "detail": breakdown[key]["detail"],
            }

    explanation = (
        f"This score combines your resume's overall quality (60% weight) with "
        f"how well it matches the pasted job description (40% weight). "
        f"You matched {job_match_pct}% of the job's key requirements."
    )

    return final_score, breakdown, explanation
