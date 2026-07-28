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

# Clean stop words set to prevent junk words (e.g. 'good', 'pvt', 'ltd') from leaking into the table
STOP_WORDS = set("""a an the and or but if while with without within to of in on for from by
as is are was were be been being this that these those it its it's you
your we our they their he she his her i me my mine ours yours theirs
will would can could should shall must may might not no nor do does did
have has had having at into over under again further then once here there
all any both each few more most other some such only own same so than too
very s t just don now etc using use used via per e.g eg i.e ie
pvt ltd inc llc llp co company corp corporation organization organisation
required requirement requirements desirable preferred responsibilities
responsibility role roles job position candidate candidates applicant
apply application looking seeking join joining opportunity opportunities
good strong excellent great solid proven demonstrated ability abilities
skill skills knowledge experience experienced years year fresher freshers
team teams member members individual environment work working works
about please note kindly regard regards ctc salary package benefits
location remote onsite hybrid full time part fulltime parttime internship
day days month months week weeks etc minimum maximum plus preferred""".split())

def extract_keywords(text, top_n=40):
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]{1,}", text.lower())
    freq = {}
    for w in words:
        w = w.strip(".,-/")
        if len(w) < 3 or w in STOP_WORDS or w.isdigit():
            continue
        freq[w] = freq.get(w, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:top_n]]

def compute_skill_match(resume_skills, jd_text):
    jd_skills = extract_skills(jd_text)
    resume_skills_set = set(resume_skills)
    jd_skills_set = set(jd_skills)

    matching_skills = sorted(resume_skills_set & jd_skills_set)
    missing_skills = sorted(jd_skills_set - resume_skills_set)

    match_percentage = round(len(matching_skills) / len(jd_skills_set) * 100, 1) if jd_skills_set else 0.0

    return {
        "jd_skills": sorted(jd_skills_set),
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "skill_match_percentage": match_percentage,
    }

def compute_text_similarity(resume_text, jd_text):
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(similarity) * 100, 1)
    except ValueError:
        return 0.0

def compute_keyword_comparison(resume_text, jd_text):
    resume_text_lower = resume_text.lower()
    jd_skills = extract_skills(jd_text)

    comparison = []
    seen = set()
    for skill in jd_skills:
        pattern = r"\b" + re.escape(skill) + r"\b"
        present = bool(re.search(pattern, resume_text_lower))
        comparison.append({"keyword": skill, "present_in_resume": present})
        seen.add(skill)

    extra_keywords = extract_keywords(jd_text, top_n=15)
    extra_added = 0
    for kw in extra_keywords:
        if kw in seen:
            continue
        if extra_added >= 8:
            break
        pattern = r"\b" + re.escape(kw) + r"\b"
        present = bool(re.search(pattern, resume_text_lower))
        comparison.append({"keyword": kw, "present_in_resume": present})
        seen.add(kw)
        extra_added += 1

    return comparison

def match_resume_to_job(resume_data, jd_text):
    resume_skills = resume_data.get("skills", [])
    resume_text = resume_data.get("raw_text", "")

    skill_match = compute_skill_match(resume_skills, jd_text)
    text_similarity = compute_text_similarity(resume_text, jd_text)
    keyword_comparison = compute_keyword_comparison(resume_text, jd_text)

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
    if job_match_result is None:
        return base_score, base_breakdown, "Score based on overall formatting and content quality."

    job_match_pct = job_match_result["job_match_percentage"]
    final_score = min(round(base_score * 0.6 + job_match_pct * 0.4, 1), 100.0)

    breakdown = dict(base_breakdown)
    breakdown["Job Description Match"] = {
        "score": round(job_match_pct * 0.4, 1),
        "max": 40,
        "detail": f"{job_match_pct}% match with job description.",
    }
    explanation = f"This score combines resume formatting quality with {job_match_pct}% job description alignment."
    return final_score, breakdown, explanation